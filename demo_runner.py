"""
Decision Window Engine — Demo Runner

Prints all scenarios in a clean table format.
"""

from decision_window import Vec2, evaluate_pass_viability, evaluate_drive_viability


SCENARIOS = [
    {
        "name": "Clean pass",
        "args": dict(
            passer_pos=Vec2(0, 0),
            receiver_pos=Vec2(20, 0),
            receiver_vel=Vec2(0, 0),
            defenders=[(Vec2(10, 15), Vec2(0, 2))],
            ball_speed=25.0,
        ),
    },
    {
        "name": "Obvious interception",
        "args": dict(
            passer_pos=Vec2(0, 0),
            receiver_pos=Vec2(20, 0),
            receiver_vel=Vec2(0, 0),
            defenders=[(Vec2(10, 0), Vec2(3, 0))],
            ball_speed=20.0,
        ),
    },
    {
        "name": "Borderline timing",
        "args": dict(
            passer_pos=Vec2(0, 0),
            receiver_pos=Vec2(20, 0),
            receiver_vel=Vec2(0, 0),
            defenders=[(Vec2(19.5, 1.9), Vec2(0, -2))],
            ball_speed=20.0,
        ),
    },
    {
        "name": "Multiple defenders",
        "args": dict(
            passer_pos=Vec2(0, 0),
            receiver_pos=Vec2(15, 5),
            receiver_vel=Vec2(1, 0),
            defenders=[
                (Vec2(20, 20), Vec2(-1, -1)),
                (Vec2(7, 2), Vec2(1, 0)),
            ],
            ball_speed=20.0,
        ),
    },
    {
        "name": "Wind-up: 0.0s delay",
        "args": dict(
            passer_pos=Vec2(0, 0),
            receiver_pos=Vec2(20, 0),
            receiver_vel=Vec2(0, 0),
            defenders=[(Vec2(10, 3), Vec2(0, -5))],
            ball_speed=25.0,
            animation_delay_s=0.0,
        ),
    },
    {
        "name": "Wind-up: 0.3s delay",
        "args": dict(
            passer_pos=Vec2(0, 0),
            receiver_pos=Vec2(20, 0),
            receiver_vel=Vec2(0, 0),
            defenders=[(Vec2(10, 3), Vec2(0, -5))],
            ball_speed=25.0,
            animation_delay_s=0.3,
        ),
    },
]


def fmt(val, suffix=""):
    if val == float("inf"):
        return "---"
    return f"{val}{suffix}"


def main():
    header = f"{'Scenario':<24} {'Viable':>7} {'T_target':>9} {'Anim':>6} {'Eff_time':>9} {'Intercept':>10} {'Margin':>10}"
    sep = "-" * len(header)

    print()
    print("Decision Window Engine v0.2 — Pass Viability")
    print(sep)
    print(header)
    print(sep)

    for s in SCENARIOS:
        r = evaluate_pass_viability(**s["args"])
        viable_str = "OPEN" if r.viable else "DEAD"
        print(
            f"{s['name']:<24} {viable_str:>7} "
            f"{fmt(r.time_to_target, 's'):>9} "
            f"{fmt(r.animation_delay_s, 's'):>6} "
            f"{fmt(r.effective_execution_time, 's'):>9} "
            f"{fmt(r.earliest_intercept, 's'):>10} "
            f"{fmt(r.margin_ms, 'ms'):>10}"
        )

    print(sep)
    print()
    print("Key result: the wind-up pair uses identical geometry.")
    print("The only difference is 0.3s of animation delay.")
    print("That single variable flips the pass from OPEN to DEAD.")

    # --- Drive viability ---
    drive_header = f"{'Scenario':<24} {'Viable':>7} {'T_target':>9} {'Anim':>6} {'Eff_time':>9} {'Help_arr':>10} {'Margin':>10}"
    drive_sep = "-" * len(drive_header)

    drive_scenarios = [
        {
            "name": "Open drive",
            "args": dict(
                driver_pos=Vec2(-16.0, 4.0),
                driver_vel=Vec2(5.0, 0.0),
                target_pos=Vec2(0.0, 0.0),
                defenders=[(Vec2(-20.0, 20.0), Vec2(0.0, 0.0))],
                driver_speed=15.0,
            ),
        },
        {
            "name": "Help cuts off drive",
            "args": dict(
                driver_pos=Vec2(-16.0, 4.0),
                driver_vel=Vec2(5.0, 0.0),
                target_pos=Vec2(0.0, 0.0),
                defenders=[(Vec2(-4.0, 2.0), Vec2(-3.0, -1.0))],
                driver_speed=15.0,
            ),
        },
        {
            "name": "Gather: 0.0s delay",
            "args": dict(
                driver_pos=Vec2(-16.0, 4.0),
                driver_vel=Vec2(5.0, 0.0),
                target_pos=Vec2(0.0, 0.0),
                defenders=[(Vec2(-5.0, 7.0), Vec2(0.0, -6.0))],
                driver_speed=15.0,
                animation_delay_s=0.0,
            ),
        },
        {
            "name": "Gather: 0.2s delay",
            "args": dict(
                driver_pos=Vec2(-16.0, 4.0),
                driver_vel=Vec2(5.0, 0.0),
                target_pos=Vec2(0.0, 0.0),
                defenders=[(Vec2(-5.0, 7.0), Vec2(0.0, -6.0))],
                driver_speed=15.0,
                animation_delay_s=0.2,
            ),
        },
    ]

    print()
    print("Decision Window Engine v0.2 — Drive Viability")
    print(drive_sep)
    print(drive_header)
    print(drive_sep)

    for s in drive_scenarios:
        r = evaluate_drive_viability(**s["args"])
        viable_str = "OPEN" if r.viable else "DEAD"
        print(
            f"{s['name']:<24} {viable_str:>7} "
            f"{fmt(r.time_to_target, 's'):>9} "
            f"{fmt(r.animation_delay_s, 's'):>6} "
            f"{fmt(r.effective_execution_time, 's'):>9} "
            f"{fmt(r.earliest_help_arrival, 's'):>10} "
            f"{fmt(r.margin_ms, 'ms'):>10}"
        )

    print(drive_sep)
    print()
    print("Key result: the gather-delay pair uses identical geometry.")
    print("The only difference is 0.2s of gather delay.")
    print("That single variable flips the drive from OPEN to DEAD.")
    print()


if __name__ == "__main__":
    main()
