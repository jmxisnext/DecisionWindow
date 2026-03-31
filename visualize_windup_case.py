"""
Decision Window Engine — Wind-up Flip Visualization

Two-panel figure showing the same pass geometry:
  Left:  0.0s animation delay -> VIABLE
  Right: 0.3s animation delay -> INTERCEPTED

Saved to windup_flip.png
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from decision_window import Vec2, evaluate_pass_viability


def draw_scenario(ax, title, result, passer, receiver, defender_pos, defender_vel,
                  animation_delay, ball_speed):
    ax.set_xlim(-2, 24)
    ax.set_ylim(-4, 8)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel("x (units)")
    ax.set_ylabel("y (units)")

    # Pass lane
    ax.plot([passer.x, receiver.x], [passer.y, receiver.y],
            color="#2196F3", linewidth=2, linestyle="--", alpha=0.6, zorder=1)

    # Ball travel arrow
    ax.annotate("", xy=(receiver.x, receiver.y), xytext=(passer.x, passer.y),
                arrowprops=dict(arrowstyle="-|>", color="#2196F3", lw=1.5),
                zorder=2)

    # Passer
    ax.plot(passer.x, passer.y, "o", color="#4CAF50", markersize=14, zorder=5)
    ax.annotate("Passer", (passer.x, passer.y), textcoords="offset points",
                xytext=(0, -18), ha="center", fontsize=9, color="#4CAF50",
                fontweight="bold")

    # Receiver
    ax.plot(receiver.x, receiver.y, "s", color="#4CAF50", markersize=12, zorder=5)
    ax.annotate("Receiver", (receiver.x, receiver.y), textcoords="offset points",
                xytext=(0, -18), ha="center", fontsize=9, color="#4CAF50",
                fontweight="bold")

    # Defender starting position
    ax.plot(defender_pos.x, defender_pos.y, "^", color="#F44336", markersize=13, zorder=5)
    ax.annotate("Defender", (defender_pos.x, defender_pos.y),
                textcoords="offset points", xytext=(12, 2), fontsize=9,
                color="#F44336", fontweight="bold")

    # Defender closure path during animation delay
    if animation_delay > 0:
        def_future = Vec2(
            defender_pos.x + defender_vel.x * animation_delay,
            defender_pos.y + defender_vel.y * animation_delay,
        )
        ax.annotate("", xy=(def_future.x, def_future.y),
                    xytext=(defender_pos.x, defender_pos.y),
                    arrowprops=dict(arrowstyle="-|>", color="#F44336",
                                    lw=2, linestyle="-"),
                    zorder=4)
        ax.plot(def_future.x, def_future.y, "^", color="#F44336",
                markersize=10, alpha=0.5, zorder=4)
        ax.annotate(f"+{animation_delay}s\nwind-up",
                    (def_future.x, def_future.y),
                    textcoords="offset points", xytext=(12, -5), fontsize=8,
                    color="#F44336", alpha=0.8)

    # Intercept point (if applicable)
    if result.earliest_intercept != float("inf"):
        # Ball position at intercept time
        pass_dir = Vec2(receiver.x - passer.x, receiver.y - passer.y)
        pass_len = pass_dir.length()
        unit = Vec2(pass_dir.x / pass_len, pass_dir.y / pass_len)
        intercept_dist = ball_speed * result.earliest_intercept
        ix = passer.x + unit.x * intercept_dist
        iy = passer.y + unit.y * intercept_dist

        ax.plot(ix, iy, "X", color="#F44336", markersize=16, zorder=6,
                markeredgecolor="white", markeredgewidth=1.5)
        ax.annotate(f"INTERCEPT\nt={result.earliest_intercept}s",
                    (ix, iy), textcoords="offset points",
                    xytext=(0, 12), ha="center", fontsize=8,
                    color="#F44336", fontweight="bold")

    # Result box
    if result.viable:
        box_color = "#4CAF50"
        label = "VIABLE"
        margin_text = "No intercept possible"
    else:
        box_color = "#F44336"
        label = "INTERCEPTED"
        margin_text = f"Margin: {result.margin_ms}ms"

    props = dict(boxstyle="round,pad=0.4", facecolor=box_color, alpha=0.15,
                 edgecolor=box_color, linewidth=2)
    ax.text(0.5, 0.95,
            f"{label}\n"
            f"T_target: {result.time_to_target}s | "
            f"Delay: {result.animation_delay_s}s | "
            f"Eff: {result.effective_execution_time}s\n"
            f"{margin_text}",
            transform=ax.transAxes, fontsize=9, verticalalignment="top",
            horizontalalignment="center", bbox=props, color=box_color,
            fontweight="bold")

    ax.grid(True, alpha=0.2)


def main():
    passer = Vec2(0, 0)
    receiver = Vec2(20, 0)
    defender_pos = Vec2(10, 3)
    defender_vel = Vec2(0, -5)
    ball_speed = 25.0

    shared = dict(
        passer_pos=passer,
        receiver_pos=receiver,
        receiver_vel=Vec2(0, 0),
        defenders=[(defender_pos, defender_vel)],
        ball_speed=ball_speed,
    )

    result_no_delay = evaluate_pass_viability(**shared, animation_delay_s=0.0)
    result_with_delay = evaluate_pass_viability(**shared, animation_delay_s=0.3)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Pass Viability: Animation Delay Flip",
                 fontsize=15, fontweight="bold", y=0.98)

    draw_scenario(ax1, "No Animation Delay (0.0s)", result_no_delay,
                  passer, receiver, defender_pos, defender_vel, 0.0, ball_speed)
    draw_scenario(ax2, "With Animation Delay (0.3s)", result_with_delay,
                  passer, receiver, defender_pos, defender_vel, 0.3, ball_speed)

    fig.text(0.5, 0.01,
             "Same geometry. Same defender. Same ball speed. "
             "Only difference: 0.3s of wind-up animation.",
             ha="center", fontsize=11, style="italic", color="#555")

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.savefig("J:/projects/decision_window/windup_flip.png", dpi=150,
                bbox_inches="tight", facecolor="white")
    print("Saved: windup_flip.png")
    plt.close()


if __name__ == "__main__":
    main()
