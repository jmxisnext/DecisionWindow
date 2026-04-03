# Checkpoint: Decision Window Engine v0.2

**Date:** 2026-04-03
**Anchor:** 3 — Decision Window Engine (Timing)
**Status:** Pass + drive viability complete. Ready for portfolio packaging.

## What Was Built

A deterministic execution-timing evaluator that models whether an action (pass or drive) remains valid through the full execution window — from player input through animation wind-up to completion.

### Core functions

`evaluate_pass_viability()` — pure function, stdlib only.

Inputs: passer position, receiver position/velocity, defender positions/velocities, ball speed, animation delay.

Output: `PassViabilityResult` with viable/not-viable decision, time-to-target, earliest intercept, margin in milliseconds, and effective execution time.

`evaluate_drive_viability()` — pure function, stdlib only.

Inputs: driver position/velocity, target position (rim), help defender positions/velocities, driver speed, animation delay.

Output: `DriveViabilityResult` with viable/not-viable decision, time-to-target, earliest help arrival, margin in milliseconds, and effective execution time.

Both share the same timing model: animation delay creates a gap between input and execution where defenders can close.

## What Was Proven

1. **Static viability works** — clean pass, obvious interception, and borderline cases produce correct, non-trivial results.
2. **Lead-pass prediction** — receiver future position is iteratively corrected for motion during ball flight.
3. **Multi-defender selection** — earliest intercept is taken across all defenders.
4. **Animation delay changes outcomes (pass)** — same geometry, same defender, same ball speed. Adding 0.3s wind-up flips a viable pass to intercepted. This is the key result.
5. **Borderline behavior** — the -30ms margin case shows the evaluator produces continuous values, not just binary open/closed.
6. **Open drive detection** — drive with no help defender near the path returns viable with large margin.
7. **Help defender cuts off drive** — defender closing on the paint correctly kills the drive.
8. **Gather delay kills drive** — same geometry, viable without delay, dead with 0.2s gather delay. Mirrors the pass wind-up flip.
9. **Drive and pass diverge on same state** — identical defender positions produce different viability for drive vs pass, proving both evaluators are needed.

## Hero Results

### Pass wind-up flip

| Delay | Viable | Intercept | Margin |
|---|---|---|---|
| 0.0s | OPEN | --- | --- |
| 0.3s | DEAD | 0.352s | -448ms |

One variable changed. Outcome flipped.

### Drive gather-delay flip

Same geometry, same help defender. Adding 0.2s gather delay flips a viable drive to dead — the help defender rotates into the lane during the animation.

## Artifact Index

| File | Purpose |
|---|---|
| `decision_window.py` | Core evaluator (v0.2 — pass + drive) |
| `test_pass_viability.py` | 5 pass viability tests |
| `test_drive_viability.py` | 4 drive viability tests |
| `demo_runner.py` | Terminal table demo (pass + drive) |
| `visualize_windup_case.py` | Two-panel wind-up comparison figure |
| `windup_flip.png` | Generated hero image |
| `README.md` | Project documentation |

## Locked Assumptions (Do Not Change Without Reason)

- Defender model: constant max speed toward any point on action path (conservative)
- Ball model: constant speed, straight line
- Drive model: constant speed, straight line to target
- Sampling: 100 points along action trajectory
- Lead-pass: 2 iterations of receiver position correction
- Margin threshold: 50ms default (pass), 100ms default (drive)

## Deferred Items (Do Not Start Yet)

- Non-linear defender acceleration / deceleration curves
- Defender reaction delay (currently assumes instant reaction at input time)
- Pass arc modeling (lob vs bounce vs chest)
- 5v5 team-level evaluation
- Temporal simulation loop
- Engine integration layer

## Resume Commands

```bash
cd J:/projects/decision_window
python test_pass_viability.py        # verify all 5 pass tests pass
python test_drive_viability.py       # verify all 4 drive tests pass
python demo_runner.py                # print scenario table
python visualize_windup_case.py      # regenerate windup_flip.png
```

## Next Steps (When Resuming)

1. Portfolio alignment and positioning materials
2. Optionally: defender reaction delay (next physics addition)
3. Optionally: temporal sweep (vary animation_delay from 0 to 0.5s, plot margin curve)
