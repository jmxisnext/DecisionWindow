# Decision Window — Claude Code Project Instructions

## Role

Anchor 3: Deterministic execution timing evaluator.

Determines whether an action (pass, drive) remains viable through the full execution window — from player input through animation wind-up to ball arrival. Does NOT perform state extraction or constraint modeling — those belong to ISO4D and VoidLine.

## Current Milestone

v0.2 pass + drive viability complete. See `docs/checkpoints/CHECKPOINT_v0_2_decision_window.md`.

## Session Start

1. Read this file
2. Read `docs/checkpoints/CHECKPOINT_v0_1_decision_window.md`
3. Run `git status` and `git log --oneline -3`
4. Summarize: current milestone, dirty state, next 3 actions

## Session Close

1. Update checkpoint if milestone state changed
2. Summarize what changed
3. List next actions
4. Confirm `git status`

## Run / Test

```bash
python test_pass_viability.py          # 5 pass viability tests
python test_drive_viability.py         # drive viability tests
python demo_runner.py                  # terminal scenario table
python visualize_windup_case.py        # regenerate windup_flip.png
```

## Directory Map

| Path | Purpose |
|---|---|
| `decision_window.py` | Core evaluator (pass + drive viability) |
| `test_pass_viability.py` | Pass scenario tests |
| `test_drive_viability.py` | Drive scenario tests |
| `demo_runner.py` | Terminal demo |
| `visualize_windup_case.py` | Hero figure generator |
| `docs/checkpoints/` | Milestone checkpoints |

## Anchor Boundary

This module is responsible ONLY for execution timing. Do not add:
- State extraction (ISO4D)
- Constraint modeling (VoidLine)
- Validation / ground-truth comparison (RenderTrace)

## What Not to Touch

- Locked assumptions in the checkpoint (defender model, ball model, sampling, margin threshold)
- Deferred items listed in the checkpoint — do not start without explicit instruction
- Pure-function interface of `evaluate_pass_viability()` and `evaluate_drive_viability()` — stack_integration depends on these signatures
