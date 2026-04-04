"""
integration_voidline.py
========================
Cross-anchor integration: ISO4D -> VoidLine -> Decision Window.

Full pipeline demonstration:
    1. Load ISO4D extraction (offensive tracks from video)
    2. Transform coordinates (ui_halfcourt_normalized -> ISO4D feet)
    3. Generate scheme-driven defenders (VoidLine scheme engine)
    4. Evaluate pass and drive viability (Decision Window)
    5. Compare across schemes and animation delays

This script bridges two repos:
    - J:/projects/VoidLine  (scheme engine, coordinate transform)
    - J:/projects/decision_window  (viability evaluators)

The result is a single table showing how defensive scheme and animation
delay combine to change action outcomes — the core system story.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Cross-anchor import: VoidLine scheme engine
sys.path.insert(0, str(Path("J:/projects/VoidLine")))
from adapter.scheme import Scheme, generate_defenders, inject_defenders
from src.field.space_model import COURT_HALF_LENGTH_FT, COURT_WIDTH_FT

# Decision Window evaluators (local)
from decision_window import (
    Vec2,
    evaluate_pass_viability,
    evaluate_drive_viability,
)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

EXTRACTION_PATH = Path("J:/projects/ISO4D/data/reference/beta_is3_playui_tracks.json")
AGENT_ID = "PG"
DECISION_TIME = 1.5           # timestamp to evaluate (PG in motion on wing)
BALL_SPEED = 25.0             # ft/s (NBA chest pass)
DRIVER_SPEED = 15.0           # ft/s (NBA drive speed)
RIM = Vec2(0.0, 0.0)         # basket position in ISO4D
DELAYS = [0.0, 0.1, 0.2, 0.3]
SCHEMES = [Scheme.DROP, Scheme.ICE, Scheme.HELP_HEAVY]


# ---------------------------------------------------------------------------
# Coordinate transform (same as VoidLine integration_iso3.py)
# ---------------------------------------------------------------------------

def transform_extraction(raw: dict) -> dict:
    import copy
    transformed = copy.deepcopy(raw)
    transformed["coordinate_system"] = "iso4d"
    for entity in transformed["entities"]:
        for frame in entity["frames"]:
            px, py = frame["pos"]
            vx, vy = frame["vel"]
            frame["pos"] = [
                (py - 1.0) * COURT_HALF_LENGTH_FT,
                (px - 0.5) * COURT_WIDTH_FT,
            ]
            frame["vel"] = [
                vy * COURT_HALF_LENGTH_FT,
                vx * COURT_WIDTH_FT,
            ]
    return transformed


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_frame(entity: dict, t: float) -> dict | None:
    best, best_dt = None, float("inf")
    for f in entity["frames"]:
        dt = abs(f["t"] - t)
        if dt < best_dt:
            best_dt, best = dt, f
    return best if best_dt <= 0.05 else None


def to_vec2(pos: list[float]) -> Vec2:
    return Vec2(pos[0], pos[1])


def entity_at(extraction: dict, entity_id: str, t: float) -> tuple[Vec2, Vec2]:
    """Get (position, velocity) as Vec2 for an entity at time t."""
    entity = next(e for e in extraction["entities"] if e["id"] == entity_id)
    frame = get_frame(entity, t)
    return to_vec2(frame["pos"]), to_vec2(frame["vel"])


def defenders_at(extraction: dict, t: float, exclude: set[str] | None = None) -> list[tuple[Vec2, Vec2]]:
    """Get all defender (pos, vel) pairs at time t."""
    exclude = exclude or set()
    result = []
    for e in extraction["entities"]:
        if e.get("role") != "defender":
            continue
        if e["id"] in exclude:
            continue
        frame = get_frame(e, t)
        if frame:
            result.append((to_vec2(frame["pos"]), to_vec2(frame["vel"])))
    return result


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_scenario(
    extraction: dict,
    t: float,
    scheme_name: str,
) -> list[dict]:
    """Evaluate pass and drive at time t across all delay values."""
    pg_pos, pg_vel = entity_at(extraction, "PG", t)
    sg_pos, sg_vel = entity_at(extraction, "SG", t)

    # All scheme defenders can intercept the pass
    pass_defenders = defenders_at(extraction, t)

    # Help defenders for drive (exclude on-ball — they're behind the driver)
    drive_defenders = defenders_at(extraction, t, exclude={"D1_onball"})

    results = []

    for delay in DELAYS:
        # Pass: PG -> SG
        pass_result = evaluate_pass_viability(
            passer_pos=pg_pos,
            receiver_pos=sg_pos,
            receiver_vel=sg_vel,
            defenders=pass_defenders,
            ball_speed=BALL_SPEED,
            animation_delay_s=delay,
        )

        # Drive: PG -> rim
        drive_result = evaluate_drive_viability(
            driver_pos=pg_pos,
            driver_vel=pg_vel,
            target_pos=RIM,
            defenders=drive_defenders,
            driver_speed=DRIVER_SPEED,
            animation_delay_s=delay,
        )

        results.append({
            "scheme": scheme_name,
            "delay": delay,
            "pass_viable": pass_result.viable,
            "pass_margin_ms": pass_result.margin_ms,
            "pass_intercept": pass_result.earliest_intercept,
            "pass_ttt": pass_result.time_to_target,
            "drive_viable": drive_result.viable,
            "drive_margin_ms": drive_result.margin_ms,
            "drive_help": drive_result.earliest_help_arrival,
            "drive_ttt": drive_result.time_to_target,
        })

    return results


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def fmt_viable(viable: bool) -> str:
    return "OPEN" if viable else "DEAD"


def fmt_margin(margin_ms: float) -> str:
    if margin_ms == float("inf"):
        return "---"
    return f"{margin_ms:+.0f}ms"


def print_results(all_results: list[dict]) -> None:
    # Header
    print(f"\n{'=' * 90}")
    print("  CROSS-ANCHOR EVALUATION: ISO4D -> VoidLine -> Decision Window")
    print(f"{'=' * 90}")
    print(f"  Decision time: t={DECISION_TIME}s  |  Ball: {BALL_SPEED} ft/s  |  Drive: {DRIVER_SPEED} ft/s")
    print(f"  Action: PG passes to SG  /  PG drives to rim")

    # Pass table
    print(f"\n  {'':10s}  PASS PG -> SG")
    print(f"  {'scheme':12s}", end="")
    for d in DELAYS:
        print(f"  {'delay='+str(d)+'s':>14s}", end="")
    print()
    print(f"  {'-'*12}" + f"  {'-'*14}" * len(DELAYS))

    for scheme in SCHEMES:
        scheme_rows = [r for r in all_results if r["scheme"] == scheme.value]
        line = f"  {scheme.value:12s}"
        for r in scheme_rows:
            cell = f"{fmt_viable(r['pass_viable'])} {fmt_margin(r['pass_margin_ms'])}"
            line += f"  {cell:>14s}"
        print(line)

    # Drive table
    print(f"\n  {'':10s}  DRIVE PG -> RIM")
    print(f"  {'scheme':12s}", end="")
    for d in DELAYS:
        print(f"  {'delay='+str(d)+'s':>14s}", end="")
    print()
    print(f"  {'-'*12}" + f"  {'-'*14}" * len(DELAYS))

    for scheme in SCHEMES:
        scheme_rows = [r for r in all_results if r["scheme"] == scheme.value]
        line = f"  {scheme.value:12s}"
        for r in scheme_rows:
            cell = f"{fmt_viable(r['drive_viable'])} {fmt_margin(r['drive_margin_ms'])}"
            line += f"  {cell:>14s}"
        print(line)

    # Detail table
    print(f"\n{'=' * 90}")
    print("  TIMING DETAIL")
    print(f"{'=' * 90}")
    print(f"  {'scheme':12s}  {'delay':>5s}  "
          f"{'pass':>6s}  {'margin':>8s}  {'intercpt':>8s}  {'ttt':>6s}  "
          f"{'drive':>6s}  {'margin':>8s}  {'help':>8s}  {'ttt':>6s}")
    print(f"  {'-'*12}  {'-'*5}  "
          f"{'-'*6}  {'-'*8}  {'-'*8}  {'-'*6}  "
          f"{'-'*6}  {'-'*8}  {'-'*8}  {'-'*6}")

    for r in all_results:
        pi = f"{r['pass_intercept']:.3f}s" if r['pass_intercept'] != float('inf') else "---"
        dh = f"{r['drive_help']:.3f}s" if r['drive_help'] != float('inf') else "---"
        print(f"  {r['scheme']:12s}  {r['delay']:5.1f}  "
              f"{fmt_viable(r['pass_viable']):>6s}  {fmt_margin(r['pass_margin_ms']):>8s}  {pi:>8s}  {r['pass_ttt']:.3f}  "
              f"{fmt_viable(r['drive_viable']):>6s}  {fmt_margin(r['drive_margin_ms']):>8s}  {dh:>8s}  {r['drive_ttt']:.3f}")


def print_summary(all_results: list[dict]) -> None:
    print(f"\n{'=' * 90}")
    print("  SIGNAL SUMMARY")
    print(f"{'=' * 90}")

    # Count flips per scheme
    for scheme in SCHEMES:
        rows = [r for r in all_results if r["scheme"] == scheme.value]
        pass_flips = sum(1 for i in range(1, len(rows))
                        if rows[i]["pass_viable"] != rows[i-1]["pass_viable"])
        drive_flips = sum(1 for i in range(1, len(rows))
                         if rows[i]["drive_viable"] != rows[i-1]["drive_viable"])

        no_delay = rows[0]
        max_delay = rows[-1]

        print(f"\n  {scheme.value}:")
        print(f"    Pass:  {fmt_viable(no_delay['pass_viable'])} -> {fmt_viable(max_delay['pass_viable'])}  "
              f"(margin shift: {fmt_margin(no_delay['pass_margin_ms'])} -> {fmt_margin(max_delay['pass_margin_ms'])})")
        print(f"    Drive: {fmt_viable(no_delay['drive_viable'])} -> {fmt_viable(max_delay['drive_viable'])}  "
              f"(margin shift: {fmt_margin(no_delay['drive_margin_ms'])} -> {fmt_margin(max_delay['drive_margin_ms'])})")

    # Cross-scheme: which scheme is most delay-sensitive?
    print(f"\n  Key finding:")
    for action in ["pass", "drive"]:
        flipped = []
        for scheme in SCHEMES:
            rows = [r for r in all_results if r["scheme"] == scheme.value]
            if rows[0][f"{action}_viable"] and not rows[-1][f"{action}_viable"]:
                flipped.append(scheme.value)
            elif not rows[0][f"{action}_viable"] and rows[-1][f"{action}_viable"]:
                flipped.append(f"{scheme.value} (reversed)")
        if flipped:
            print(f"    {action}: delay flips outcome in [{', '.join(flipped)}]")
        else:
            print(f"    {action}: no outcome flip across delay range")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    with open(EXTRACTION_PATH) as f:
        raw = json.load(f)

    extraction = transform_extraction(raw)

    print(f"Source:       {EXTRACTION_PATH.name}")
    print(f"Pipeline:     ISO4D -> VoidLine (scheme engine) -> Decision Window")
    print(f"Ball handler: {AGENT_ID}")
    print(f"Decision at:  t={DECISION_TIME}s")
    print(f"Schemes:      {', '.join(s.value for s in SCHEMES)}")
    print(f"Delays:       {', '.join(f'{d}s' for d in DELAYS)}")

    all_results = []

    for scheme in SCHEMES:
        defenders = generate_defenders(extraction, AGENT_ID, scheme)
        combined = inject_defenders(extraction, defenders)

        # Show defender summary
        def_summary = []
        for d in defenders:
            frame = get_frame(d, DECISION_TIME)
            if frame:
                pos = to_vec2(frame["pos"])
                pg_pos, _ = entity_at(combined, "PG", DECISION_TIME)
                dist = (pos - pg_pos).length()
                def_summary.append(f"{d['id']}({dist:.0f}ft)")
        print(f"\n  [{scheme.value}] {', '.join(def_summary)}")

        results = evaluate_scenario(combined, DECISION_TIME, scheme.value)
        all_results.extend(results)

    print_results(all_results)
    print_summary(all_results)


if __name__ == "__main__":
    main()
