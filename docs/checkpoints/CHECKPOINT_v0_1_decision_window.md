# Checkpoint: Decision Window Engine v0.1

**Date:** 2026-03-31
**Anchor:** 3 — Decision Window Engine (Timing)
**Status:** Core slice complete. Ready for portfolio packaging.

## What Was Built

A deterministic pass-viability evaluator that models whether a pass remains valid through the full execution window — from player input through animation wind-up to ball arrival.

### Core function

`evaluate_pass_viability()` — pure function, stdlib only.

Inputs: passer position, receiver position/velocity, defender positions/velocities, ball speed, animation delay.

Output: `PassViabilityResult` with viable/not-viable decision, time-to-target, earliest intercept, margin in milliseconds, and effective execution time.

## What Was Proven

1. **Static viability works** — clean pass, obvious interception, and borderline cases produce correct, non-trivial results.
2. **Lead-pass prediction** — receiver future position is iteratively corrected for motion during ball flight.
3. **Multi-defender selection** — earliest intercept is taken across all defenders.
4. **Animation delay changes outcomes** — same geometry, same defender, same ball speed. Adding 0.3s wind-up flips a viable pass to intercepted. This is the key result.
5. **Borderline behavior** — the -30ms margin case shows the evaluator produces continuous values, not just binary open/closed.

## Hero Result

The wind-up flip:

| Delay | Viable | Intercept | Margin |
|---|---|---|---|
| 0.0s | OPEN | --- | --- |
| 0.3s | DEAD | 0.352s | -448ms |

One variable changed. Outcome flipped.

## Artifact Index

| File | Purpose |
|---|---|
| `decision_window.py` | Core evaluator (v0.1) |
| `test_pass_viability.py` | 5 test scenarios |
| `demo_runner.py` | Terminal table demo |
| `visualize_windup_case.py` | Two-panel wind-up comparison figure |
| `windup_flip.png` | Generated hero image |
| `README.md` | Project documentation |

## Locked Assumptions (Do Not Change Without Reason)

- Defender model: constant max speed toward any point on pass line (conservative)
- Ball model: constant speed, straight line
- Sampling: 100 points along pass trajectory
- Lead-pass: 2 iterations of receiver position correction
- Margin threshold: 50ms default

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
python test_pass_viability.py        # verify all 5 tests pass
python demo_runner.py                # print scenario table
python visualize_windup_case.py      # regenerate windup_flip.png
```

## Next Steps (When Resuming)

1. Portfolio alignment and positioning materials
2. Optionally: defender reaction delay (next physics addition)
3. Optionally: temporal sweep (vary animation_delay from 0 to 0.5s, plot margin curve)
