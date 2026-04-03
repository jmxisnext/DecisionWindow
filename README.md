# Decision Window Engine

**A deterministic pass-viability evaluator that predicts whether a pass remains valid through execution — not just at input time.**

Sports game passing logic often evaluates openness at input time instead of whether the pass will still be valid when released and received. This system models the gap between when a player presses "pass" and when the ball actually arrives, accounting for animation delay, receiver motion, and defender interception.

**Anchor boundary:** This module is responsible ONLY for execution timing (will an action survive through execution delay). It does NOT perform state extraction or constraint modeling — those belong to ISO4D and VoidLine respectively.

## The Core Problem

In gameplay AI, a pass can look open when the player commits to it but become invalid by the time the ball is released. This happens because:

1. **Animation delay** — the passer has a wind-up before the ball leaves their hands
2. **Defender closure** — defenders are already moving toward the passing lane during that wind-up
3. **The game evaluates at the wrong time** — checking openness at input rather than at execution

The result: the player sees an open receiver, presses pass, and watches the ball get intercepted. The system told them "open" but the pass was dead before it started.

This system evaluates execution timing. It complements [VoidLine](../VoidLine), which defines the feasible action space — what actions are possible under constraint. Decision Window answers the next question: will a feasible action still be valid by the time it executes?

## How It Works

```
margin = earliest_intercept - time_to_target

time_to_target   = distance(passer, receiver_future) / ball_speed
receiver_future  = receiver_pos + receiver_vel * (animation_delay + time_to_target)
earliest_intercept = min time a defender can reach any point on the ball's flight path

if margin > threshold:
    pass is viable
else:
    pass is dead
```

The key insight: defenders get `animation_delay + t_ball` seconds to reach each point on the pass trajectory, because they start moving when the player commits (input time), not when the ball is released.

## The Wind-up Flip

The strongest demonstration is a single scenario run twice — same geometry, same defender, same ball speed. The only variable is animation delay.

![Wind-up Flip](windup_flip.png)

| Scenario | Viable | T_target | Anim Delay | Eff. Time | Intercept | Margin |
|---|---|---|---|---|---|---|
| 0.0s delay | **OPEN** | 0.80s | 0.0s | 0.80s | --- | --- |
| 0.3s delay | **DEAD** | 0.80s | 0.3s | 1.10s | 0.352s | -448ms |

With zero delay, the defender at (10, 3) cannot reach the pass lane before the ball passes. With 0.3s of wind-up, that same defender now has enough time to close 3 units and intercept at 0.35s into ball flight.

This is the exact player complaint: *"it looked open when I pressed pass."*

## Full Scenario Suite

```
Scenario                  Viable  T_target   Anim  Eff_time  Intercept     Margin
---------------------------------------------------------------------------------
Clean pass                  OPEN      0.8s   0.0s      0.8s        ---        ---
Obvious interception        DEAD      1.0s   0.0s      1.0s      0.44s   -560.0ms
Borderline timing           DEAD      1.0s   0.0s      1.0s      0.97s    -30.0ms
Multiple defenders          DEAD     0.83s   0.0s     0.83s    0.3569s  -473.07ms
Wind-up: 0.0s delay         OPEN      0.8s   0.0s      0.8s        ---        ---
Wind-up: 0.3s delay         DEAD      0.8s   0.3s      1.1s     0.352s   -448.0ms
```

The borderline case (-30ms margin) demonstrates the evaluator produces non-trivial results, not just binary open/closed.

## What This Models

| Capability | Description |
|---|---|
| Lead-pass prediction | Receiver future position is iteratively corrected for motion during flight |
| Multi-defender evaluation | Takes the earliest intercept across all defenders |
| Animation delay | Wind-up time where defenders move but ball doesn't |
| Conservative intercept model | Defenders use max speed toward any point on the pass line |

## Engine Integration Context

- Consumes current game-state positions and velocities (no special data format required)
- Runs during gameplay decision evaluation, before committing to a pass action
- Outputs a pass viability score and timing margin that a decision-maker can act on

## What This Does Not Model (Yet)

- Non-linear defender acceleration
- Reaction delay (defenders don't react instantly)
- Pass arc / lob vs bounce
- 5v5 team context

## Usage

```python
from decision_window import Vec2, evaluate_pass_viability

result = evaluate_pass_viability(
    passer_pos=Vec2(0, 0),
    receiver_pos=Vec2(20, 0),
    receiver_vel=Vec2(2, 0),
    defenders=[(Vec2(10, 3), Vec2(0, -5))],
    ball_speed=25.0,
    animation_delay_s=0.3,
)

print(result.viable)                  # False
print(result.margin_ms)               # margin in milliseconds
print(result.effective_execution_time) # delay + flight time
```

## Files

| File | Purpose |
|---|---|
| `decision_window.py` | Core evaluator — pure function, no dependencies |
| `test_pass_viability.py` | 5 test scenarios including the wind-up flip |
| `demo_runner.py` | Prints all scenarios in table format |
| `visualize_windup_case.py` | Generates the two-panel wind-up comparison figure |

## Run

```bash
python test_pass_viability.py        # run tests
python demo_runner.py                # print demo table
python visualize_windup_case.py      # generate windup_flip.png
```
