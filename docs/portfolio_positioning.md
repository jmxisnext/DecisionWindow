# Portfolio Positioning — Decision Window Engine

## Anchor Alignment

This project is the core deliverable of **Anchor 3 (Decision Window Engine)** in a portfolio of gameplay AI simulation systems.

| Anchor | Focus | Status |
|---|---|---|
| 1 — ISO4D | Extraction: raw input to structured spatial state | In progress |
| 2 — Voidline | Feasibility: possible vs impossible under constraints | v0.3 complete |
| **3 — Decision Window** | **Timing: is the action still viable at execution?** | **v0.2 complete** |

The three anchors form a pipeline: ISO4D provides state, Voidline defines the possibility space, Decision Window evaluates whether an action can still succeed when executed.

## Target Problem

Sports game AI evaluates action openness at input time — when the player presses the button. But the action doesn't execute instantly. A pass has a wind-up animation; a drive has a gather step. During that window, defenders are already closing. By the time the action completes, the "open" window may already be dead.

This is one of the most common player complaints in basketball and soccer games: *"it looked open when I pressed pass"* and *"the lane was open but help got there first."*

The Decision Window Engine models this gap for both passes and drives, returning a timing margin that tells you whether the action will survive through execution.

## Resume Bullets

- Built a deterministic execution-timing evaluator for sports gameplay AI that predicts whether passes and drives remain valid through the full animation window — from input to completion
- Demonstrated that 0.3s of pass wind-up or 0.2s of drive gather delay can flip a viable action to dead using identical geometry — modeling the exact timing failures that cause intercepted passes and blocked drives in sports games
- Proved that the same game state can produce different viability for different action types (drive viable, pass dead), validating a multi-action evaluation model
- Designed as pure functions consuming positions and velocities, with no engine dependency, suitable for integration into any gameplay decision pipeline

## Project Summary (Short)

> Deterministic execution-timing evaluator for sports gameplay AI. Models the gap between player input and action completion for both passes and drives — proving that animation delay alone can kill an otherwise open action. Pure functions, 9 tests, with visualization showing the same pass flip from viable to intercepted when 0.3s of wind-up is added.

## Why This Matters to Sports Gameplay AI

### The problem is real and widespread
Every basketball and soccer game ships with some version of this bug. Players press pass, see an open receiver, and watch the ball get intercepted. The root cause is that the AI evaluated openness at a single point in time instead of across the full execution window.

### The solution is tractable
This isn't a research problem. It's an engineering problem with a clear mathematical model: compute time-to-target, compute earliest defender intercept accounting for wind-up delay, compare. The Decision Window Engine is a working implementation of that model.

### It demonstrates the right skills
- **Spatial reasoning** — computing defender-to-lane distances and intercept geometry
- **Time-aware decision modeling** — the core capability that separates static AI from responsive AI
- **Constraint-based evaluation** — margin thresholds, multi-defender selection, lead-pass correction
- **Systems discipline** — small scope, deterministic output, test coverage, clear deferred items

### It maps directly to real gameplay AI roles
Studios hiring for gameplay AI (2K, EA, Ubisoft) need engineers who understand that game decisions happen over time, not at instants. This project demonstrates that understanding with a concrete, runnable artifact — not a whiteboard sketch.
