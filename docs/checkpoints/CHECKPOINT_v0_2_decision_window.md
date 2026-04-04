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

## v0.2.1 — Cross-Anchor Integration (2026-04-03)

**Full pipeline: extracted motion -> scheme defense -> action viability under timing pressure.**

### What was added

- **Cross-anchor integration** (`integration_voidline.py`): loads ISO4D extraction, generates scheme-driven defenders via the Scheme Engine, evaluates pass and drive viability under each scheme with delay sweep (0-300ms).

### What was proven

Pass viability (PG -> SG at t=1.5s):

| Scheme | 0ms | 100ms | 200ms | 300ms |
|---|---|---|---|---|
| drop | OPEN | OPEN | DEAD | DEAD |
| ice | DEAD | DEAD | DEAD | DEAD |
| help_heavy | OPEN | DEAD | DEAD | DEAD |

1. **Scheme determines baseline viability.** Ice kills the pass at any speed — deny-middle positioning places the on-ball defender directly in the passing lane. Drop and help_heavy allow it at zero delay.
2. **Delay is the tipping point in permissive schemes.** Drop flips OPEN->DEAD at 200ms. Help_heavy flips at just 100ms.
3. **More aggressive schemes are more timing-sensitive.** Help_heavy's tight gap help means even small delays are fatal — the narrowest viable window of any scheme.
4. **Drive viability is limited by court geometry at this decision point.** 42ft to rim at 15 ft/s = 2.8s; help defenders arrive regardless of scheme or delay. A correct result: at this position, passing is the live action, not driving.
5. **Two complementary analysis layers on the same state.** VoidLine measures how much space is removed (macro pressure). Decision Window measures whether a specific action survives execution (micro timing).

### Architecture

```
ISO4D          ->  state (positions, velocities from video)
Scheme Engine  ->  defense (generated from offensive state + scheme rules)
VoidLine       ->  pressure field (how constrained is the agent?)
Decision Window -> action viability (does this pass/drive survive execution?)
```

Four layers, one game state. Each layer answers a different question.

## Resume Commands

```bash
cd J:/projects/decision_window
python test_pass_viability.py        # verify all 5 pass tests pass
python test_drive_viability.py       # verify all 4 drive tests pass
python demo_runner.py                # print scenario table
python integration_voidline.py       # cross-anchor integration demo
python visualize_windup_case.py      # regenerate windup_flip.png
```

## v0.2.2 — Portfolio Packaging (2026-04-04)

### What was added

- **Quick Start + expected output** in README (clone, install, run, see results in 10 seconds)
- **Cross-anchor integration block** in all three repo READMEs: consistent diagram, scheme x delay table, one-sentence claim
- **`requirements.txt`** for Decision Window and VoidLine
- **`gameplay-ai-stack/` integration repo** — canonical front door with `run_pipeline.py` that orchestrates all three anchors via relative sibling paths

### Packaging state

All four entry points verified:
- `ISO4D/demo_runner.py` — extraction table
- `VoidLine/demo_runner.py` — constraint + counterfactual table
- `decision_window/demo_runner.py` — pass + drive viability table
- `gameplay-ai-stack/run_pipeline.py` — full cross-anchor pipeline

## Next Steps (When Resuming)

1. Commit packaging changes across all four repos
2. Create GitHub remotes for `gameplay-ai-stack` and push all repos
3. Optionally: defender reaction delay (next physics addition)
4. Optionally: temporal sweep (vary animation_delay from 0 to 0.5s, plot margin curve)
