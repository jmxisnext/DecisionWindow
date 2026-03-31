"""
Test cases for Pass Viability v0.1.

Scenarios:
  1. Clean pass — no defender near the lane, clearly viable
  2. Obvious interception — defender directly in the path, not viable
  3. Borderline timing — defender barely reaches lane, small margin
  4. Multiple defenders — earliest intercept from closest
  5. Late due to wind-up — viable at zero delay, killed by animation delay
"""

from decision_window import Vec2, evaluate_pass_viability


def test_clean_pass():
    """
    Passer at origin, receiver at (20, 0) stationary.
    Single defender far off at (10, 15) moving away.
    Ball speed 25 units/sec. Should be clearly viable.
    """
    result = evaluate_pass_viability(
        passer_pos=Vec2(0, 0),
        receiver_pos=Vec2(20, 0),
        receiver_vel=Vec2(0, 0),
        defenders=[(Vec2(10, 15), Vec2(0, 2))],  # moving away from lane
        ball_speed=25.0,
    )
    print(f"[Clean Pass]")
    print(f"  viable:            {result.viable}")
    print(f"  time_to_target:    {result.time_to_target}s")
    print(f"  earliest_intercept:{result.earliest_intercept}s")
    print(f"  margin_ms:         {result.margin_ms}ms")
    print()
    assert result.viable is True, f"Expected viable, got {result}"
    assert result.margin_ms > 100, f"Expected large margin, got {result.margin_ms}ms"


def test_obvious_interception():
    """
    Passer at origin, receiver at (20, 0) stationary.
    Defender sitting at (10, 0) — directly on the pass line — moving toward receiver.
    Ball speed 20 units/sec. Defender should easily intercept.
    """
    result = evaluate_pass_viability(
        passer_pos=Vec2(0, 0),
        receiver_pos=Vec2(20, 0),
        receiver_vel=Vec2(0, 0),
        defenders=[(Vec2(10, 0), Vec2(3, 0))],  # on the line, moving toward receiver
        ball_speed=20.0,
    )
    print(f"[Obvious Interception]")
    print(f"  viable:            {result.viable}")
    print(f"  time_to_target:    {result.time_to_target}s")
    print(f"  earliest_intercept:{result.earliest_intercept}s")
    print(f"  margin_ms:         {result.margin_ms}ms")
    print()
    assert result.viable is False, f"Expected not viable, got {result}"


def test_borderline_timing():
    """
    Passer at origin, receiver at (20, 0) stationary.
    Defender at (19.5, 1.9) with speed 2 — barely reaches the pass lane
    near the receiver end. Should produce a small negative margin (~-25ms).
    Moving defender 0.2 units further away would flip to no-intercept.
    """
    result = evaluate_pass_viability(
        passer_pos=Vec2(0, 0),
        receiver_pos=Vec2(20, 0),
        receiver_vel=Vec2(0, 0),
        defenders=[(Vec2(19.5, 1.9), Vec2(0, -2))],  # barely reaches lane
        ball_speed=20.0,
    )
    print("[Borderline Timing]")
    print(f"  viable:            {result.viable}")
    print(f"  time_to_target:    {result.time_to_target}s")
    print(f"  earliest_intercept:{result.earliest_intercept}s")
    print(f"  margin_ms:         {result.margin_ms}ms")
    print(f"  -- Small margin indicates borderline pass")
    print()
    assert abs(result.margin_ms) < 200, f"Expected borderline margin, got {result.margin_ms}ms"


def test_multiple_defenders():
    """
    Bonus: two defenders, one far and one close.
    Earliest intercept should come from the closer one.
    """
    result = evaluate_pass_viability(
        passer_pos=Vec2(0, 0),
        receiver_pos=Vec2(15, 5),
        receiver_vel=Vec2(1, 0),
        defenders=[
            (Vec2(20, 20), Vec2(-1, -1)),  # far, irrelevant
            (Vec2(7, 2), Vec2(1, 0)),       # close to lane
        ],
        ball_speed=20.0,
    )
    print(f"[Multiple Defenders]")
    print(f"  viable:            {result.viable}")
    print(f"  time_to_target:    {result.time_to_target}s")
    print(f"  earliest_intercept:{result.earliest_intercept}s")
    print(f"  margin_ms:         {result.margin_ms}ms")
    print()


def test_late_due_to_windup():
    """
    THE KEY v0.1 TEST.
    Same geometry: passer at origin, receiver at (20, 0), defender off-lane.
    With zero animation delay: pass is viable (defender can't reach lane in time).
    With 0.3s wind-up: defender now has enough extra time to close the lane.

    This is the exact player complaint: "it looked open when I pressed pass."
    """
    shared = dict(
        passer_pos=Vec2(0, 0),
        receiver_pos=Vec2(20, 0),
        receiver_vel=Vec2(0, 0),
        defenders=[(Vec2(10, 3), Vec2(0, -5))],  # 3 units off lane, closing at 5 u/s
        ball_speed=25.0,
    )

    # Without delay: pass is viable
    result_no_delay = evaluate_pass_viability(**shared, animation_delay_s=0.0)

    print("[Late Due to Wind-up — NO delay]")
    print(f"  viable:            {result_no_delay.viable}")
    print(f"  time_to_target:    {result_no_delay.time_to_target}s")
    print(f"  animation_delay:   {result_no_delay.animation_delay_s}s")
    print(f"  effective_time:    {result_no_delay.effective_execution_time}s")
    print(f"  earliest_intercept:{result_no_delay.earliest_intercept}s")
    print(f"  margin_ms:         {result_no_delay.margin_ms}ms")
    print()

    # With 0.3s wind-up: same geometry, pass dies
    result_with_delay = evaluate_pass_viability(**shared, animation_delay_s=0.3)

    print("[Late Due to Wind-up — 0.3s delay]")
    print(f"  viable:            {result_with_delay.viable}")
    print(f"  time_to_target:    {result_with_delay.time_to_target}s")
    print(f"  animation_delay:   {result_with_delay.animation_delay_s}s")
    print(f"  effective_time:    {result_with_delay.effective_execution_time}s")
    print(f"  earliest_intercept:{result_with_delay.earliest_intercept}s")
    print(f"  margin_ms:         {result_with_delay.margin_ms}ms")
    print()

    assert result_no_delay.viable is True, \
        f"Expected viable without delay, got {result_no_delay}"
    assert result_with_delay.viable is False, \
        f"Expected NOT viable with delay, got {result_with_delay}"
    print("  ** CONFIRMED: same pass flips viable -> not viable due to wind-up **")
    print()


if __name__ == "__main__":
    test_clean_pass()
    test_obvious_interception()
    test_borderline_timing()
    test_multiple_defenders()
    test_late_due_to_windup()
    print("All tests passed.")
