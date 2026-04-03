"""
Tests for drive viability evaluation.

Mirrors test_pass_viability.py structure — each test isolates one variable.
"""

from decision_window import Vec2, DriveViabilityResult, evaluate_drive_viability


def test_open_drive():
    """No help defender near the drive path — viable with large margin."""
    result = evaluate_drive_viability(
        driver_pos=Vec2(-16.0, 4.0),
        driver_vel=Vec2(5.0, 0.0),
        target_pos=Vec2(0.0, 0.0),       # rim
        defenders=[
            (Vec2(-20.0, 20.0), Vec2(0.0, 0.0)),  # far corner, stationary
        ],
        driver_speed=15.0,                 # ~15 ft/s sprint
    )
    assert result.viable is True
    assert result.margin_ms > 200


def test_help_defender_cuts_off_drive():
    """Help defender in the paint — drive is not viable."""
    result = evaluate_drive_viability(
        driver_pos=Vec2(-16.0, 4.0),
        driver_vel=Vec2(5.0, 0.0),
        target_pos=Vec2(0.0, 0.0),       # rim
        defenders=[
            (Vec2(-4.0, 2.0), Vec2(-3.0, -1.0)),  # help defender closing
        ],
        driver_speed=15.0,
    )
    assert result.viable is False
    assert result.margin_ms < 0


def test_drive_killed_by_gather_delay():
    """Same geometry — viable without delay, dead with 0.2s gather delay.

    This mirrors the wind-up flip for passes. The gather step (first-step
    animation) gives the help defender time to rotate into the lane.
    """
    # Without delay
    baseline = evaluate_drive_viability(
        driver_pos=Vec2(-16.0, 4.0),
        driver_vel=Vec2(5.0, 0.0),
        target_pos=Vec2(0.0, 0.0),
        defenders=[
            (Vec2(-5.0, 7.0), Vec2(0.0, -6.0)),  # help defender rotating toward lane
        ],
        driver_speed=15.0,
        animation_delay_s=0.0,
    )

    # With 0.2s gather delay
    delayed = evaluate_drive_viability(
        driver_pos=Vec2(-16.0, 4.0),
        driver_vel=Vec2(5.0, 0.0),
        target_pos=Vec2(0.0, 0.0),
        defenders=[
            (Vec2(-5.0, 7.0), Vec2(0.0, -6.0)),  # same defender
        ],
        driver_speed=15.0,
        animation_delay_s=0.2,
    )

    assert baseline.viable is True
    assert delayed.viable is False


def test_drive_and_pass_different_outcomes():
    """Same game state — drive is viable but pass to corner is not.

    This proves the two evaluation functions can reach different conclusions
    from identical input, which is why both exist.
    """
    from decision_window import evaluate_pass_viability

    driver_pos = Vec2(-16.0, 4.0)
    corner_pos = Vec2(-3.0, 22.0)
    corner_vel = Vec2(0.0, 0.0)
    defenders = [
        (Vec2(-10.0, 12.0), Vec2(0.0, -5.0)),  # wing defender closing toward corner
    ]

    # Drive to rim — defender is behind the driver, can't catch up
    drive = evaluate_drive_viability(
        driver_pos=driver_pos,
        driver_vel=Vec2(5.0, 0.0),
        target_pos=Vec2(0.0, 0.0),
        defenders=defenders,
        driver_speed=15.0,
    )

    # Pass to corner — defender is between passer and receiver
    pass_result = evaluate_pass_viability(
        passer_pos=driver_pos,
        receiver_pos=corner_pos,
        receiver_vel=corner_vel,
        defenders=defenders,
        ball_speed=25.0,
        animation_delay_s=0.3,
    )

    # Drive works, pass doesn't — different timing windows, same state
    assert drive.viable is True
    assert pass_result.viable is False


if __name__ == "__main__":
    tests = [
        ("Open drive", test_open_drive),
        ("Help defender cuts off drive", test_help_defender_cuts_off_drive),
        ("Drive killed by gather delay", test_drive_killed_by_gather_delay),
        ("Drive and pass different outcomes", test_drive_and_pass_different_outcomes),
    ]
    for name, fn in tests:
        fn()
        print(f"  [PASS] {name}")
    print(f"\nAll {len(tests)} drive viability tests passed.")
