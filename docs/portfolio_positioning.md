# Portfolio Positioning — Decision Window Engine

## Anchor Alignment

This project is the core deliverable of **Anchor 3 (Decision Window Engine)** in a portfolio of gameplay AI simulation systems.

| Anchor | Focus | Status |
|---|---|---|
| 1 — ISO4D | Extraction: raw input to structured spatial state | In progress |
| 2 — Voidline | Feasibility: possible vs impossible under constraints | Defined |
| **3 — Decision Window** | **Timing: is the action still viable at execution?** | **v0.1 complete** |

The three anchors form a pipeline: ISO4D provides state, Voidline defines the possibility space, Decision Window evaluates whether an action can still succeed when executed.

## Target Problem

Sports game AI evaluates pass openness at input time — when the player presses the button. But the pass doesn't execute instantly. There is a wind-up animation, and during that window, defenders are already closing on the passing lane. By the time the ball is released, the "open" pass may already be dead.

This is one of the most common player complaints in basketball and soccer games: *"it looked open when I pressed pass."*

The Decision Window Engine models this gap and returns a timing margin that tells you whether the pass will survive through execution.

## Resume Bullets

- Built a deterministic pass-viability evaluator that predicts whether a pass remains valid through execution, including receiver motion, multi-defender interception, and animation delay
- Demonstrated that a 0.3s animation wind-up can flip a viable pass to intercepted using identical game-state geometry — modeling the exact timing failure that causes bad passes in sports games
- Designed the system as a pure function consuming positions and velocities, with no engine dependency, suitable for integration into any gameplay decision pipeline

## Project Summary (Short)

> Deterministic pass-viability evaluator for sports gameplay AI. Models the timing gap between player input and ball release — proving that animation delay alone can kill an otherwise open pass. Pure function, test-backed, with a two-panel visualization showing the same pass flip from viable to intercepted when 0.3s of wind-up is added.

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
