"""
Decision Window Engine — Execution Timing v0.2

Anchor 3: Determines whether an action is still viable at execution time.
Gameplay problem: actions that look open at input time die during execution.

Evaluates two action types:
  - Pass viability (v0.1): ball flight vs defender interception
  - Drive viability (v0.2): drive to rim vs help defender arrival

Both share the same timing model: animation delay creates a gap between
input and execution where defenders can close.

Pure functions. No engine, no UI, no simulation loop.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Vec2:
    x: float
    y: float

    def __add__(self, other: Vec2) -> Vec2:
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec2) -> Vec2:
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vec2:
        return Vec2(self.x * scalar, self.y * scalar)

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def dot(self, other: Vec2) -> float:
        return self.x * other.x + self.y * other.y


@dataclass(frozen=True)
class PassViabilityResult:
    viable: bool
    time_to_target: float           # seconds for ball to reach receiver (after release)
    animation_delay_s: float        # seconds of wind-up before ball is released
    effective_execution_time: float  # animation_delay + time_to_target
    earliest_intercept: float       # seconds (in ball-flight time) for fastest defender
    margin_ms: float                # (earliest_intercept - time_to_target) in milliseconds


def _closest_approach_time(
    defender_pos: Vec2,
    defender_vel: Vec2,
    pass_origin: Vec2,
    pass_target: Vec2,
    ball_speed: float,
    animation_delay: float = 0.0,
) -> float:
    """
    Compute the time at which a defender can first reach the ball's position
    along its flight path from pass_origin to pass_target.

    Models the ball as a point moving at constant speed along the pass line.
    Models the defender as a point moving at max speed toward intercept point.

    animation_delay: extra time (seconds) the defender has before the ball
    is released. During wind-up, the ball is stationary but the defender
    is already moving — this is what makes animation delay lethal.

    Returns the earliest ball-flight time (seconds after release) at which
    the defender reaches the ball, or float('inf') if no intercept.
    """
    pass_vec = pass_target - pass_origin
    pass_dist = pass_vec.length()
    if pass_dist == 0:
        return float("inf")

    # Ball direction (unit vector along pass line)
    ball_dir = Vec2(pass_vec.x / pass_dist, pass_vec.y / pass_dist)

    # Ball position at time t: pass_origin + ball_dir * ball_speed * t
    # Defender position at time t: defender_pos + defender_vel * t
    # We want: |defender(t) - ball(t)| = 0
    #
    # relative_pos + relative_vel * t = 0  (vector equation)
    # This is overconstrained in 2D (2 equations, 1 unknown), so we find
    # the time of closest approach and check if distance ~ 0.
    #
    # Instead: find time when defender can reach any point on the ball's
    # trajectory, considering both are moving.

    # Parametric: ball at time t is at pass_origin + ball_dir * ball_speed * t
    # Defender needs to reach that same point at time t.
    # Defender can be at defender_pos + defender_vel * t at time t (constant vel).
    # But defender can also change direction — defender_vel is current velocity,
    # and we treat defender *speed* as max capability.
    #
    # Conservative model: defender moves at their current speed (magnitude of vel)
    # toward the closest intercept point on the pass line.

    defender_speed = defender_vel.length()

    # Sample points along the pass line and find earliest time where
    # defender can arrive before/when the ball does.
    # For v0 this is a clean numerical approach — no need for closed-form.

    time_to_target = pass_dist / ball_speed
    best_intercept = float("inf")

    # Sample 100 points along the pass trajectory
    steps = 100
    for i in range(steps + 1):
        frac = i / steps
        t_ball = frac * time_to_target  # time ball reaches this point

        # Ball position at this fraction of the pass
        ball_pos = pass_origin + ball_dir * (ball_speed * t_ball)

        # Distance from defender to this ball position
        d = (ball_pos - defender_pos).length()

        # Time for defender to reach this point (straight line, max speed)
        if defender_speed > 0:
            t_defender = d / defender_speed
        else:
            # Stationary defender — can only intercept if already on the line
            if d < 0.1:  # within 10cm
                t_defender = 0.0
            else:
                continue

        # Defender has animation_delay + t_ball total seconds to reach this point
        # (they start moving at input time, ball releases after animation_delay)
        if t_defender <= animation_delay + t_ball:
            best_intercept = min(best_intercept, t_ball)
            break  # earliest point on the line where defender beats the ball

    return best_intercept


def evaluate_pass_viability(
    passer_pos: Vec2,
    receiver_pos: Vec2,
    receiver_vel: Vec2,
    defenders: list[tuple[Vec2, Vec2]],
    ball_speed: float,
    animation_delay_s: float = 0.0,
    margin_threshold_ms: float = 50.0,
) -> PassViabilityResult:
    """
    Evaluate whether a pass from passer to receiver is viable given defenders.

    Args:
        passer_pos: position of the passer
        receiver_pos: current position of the receiver
        receiver_vel: velocity of the receiver (units/sec)
        defenders: list of (position, velocity) for each defender
        ball_speed: speed of the ball (units/sec)
        animation_delay_s: wind-up time before ball release (seconds)
        margin_threshold_ms: minimum margin in ms for pass to be viable

    Returns:
        PassViabilityResult with viability decision and timing breakdown.
    """
    # 1. Compute time for ball to reach receiver
    dist = (receiver_pos - passer_pos).length()
    if ball_speed <= 0:
        raise ValueError("ball_speed must be positive")
    time_to_target = dist / ball_speed

    # 2. Predict receiver's future position at arrival time.
    #    Receiver moves during BOTH animation delay and ball flight.
    #    Iterate until time_to_target converges (receiver position depends on
    #    flight time, which depends on receiver position).
    for _ in range(20):
        total_receiver_time = animation_delay_s + time_to_target
        receiver_future = receiver_pos + receiver_vel * total_receiver_time
        corrected_dist = (receiver_future - passer_pos).length()
        new_ttt = corrected_dist / ball_speed
        if abs(new_ttt - time_to_target) < 0.001:
            time_to_target = new_ttt
            break
        time_to_target = new_ttt

    # 4. For each defender, compute earliest intercept time
    #    Defenders get animation_delay extra seconds (they move during wind-up)
    earliest_intercept = float("inf")
    for def_pos, def_vel in defenders:
        t = _closest_approach_time(
            def_pos, def_vel, passer_pos, receiver_future, ball_speed,
            animation_delay=animation_delay_s,
        )
        earliest_intercept = min(earliest_intercept, t)

    # 5. Decision
    #    margin = earliest_intercept - time_to_target (both in ball-flight time)
    #    animation delay affects which intercepts are possible, not the formula
    margin_s = earliest_intercept - time_to_target
    margin_ms = margin_s * 1000.0

    viable = margin_ms > margin_threshold_ms

    effective_execution_time = animation_delay_s + time_to_target

    return PassViabilityResult(
        viable=viable,
        time_to_target=round(time_to_target, 4),
        animation_delay_s=round(animation_delay_s, 4),
        effective_execution_time=round(effective_execution_time, 4),
        earliest_intercept=round(earliest_intercept, 4) if earliest_intercept != float("inf") else float("inf"),
        margin_ms=round(margin_ms, 2) if margin_ms != float("inf") else float("inf"),
    )


# ---------------------------------------------------------------------------
# Drive viability
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DriveViabilityResult:
    viable: bool
    time_to_target: float           # seconds for driver to reach target
    animation_delay_s: float        # seconds of gather/first-step delay
    effective_execution_time: float  # animation_delay + time_to_target
    earliest_help_arrival: float    # seconds for fastest help defender to reach drive path
    margin_ms: float                # (earliest_help_arrival - time_to_target) in ms


def evaluate_drive_viability(
    driver_pos: Vec2,
    driver_vel: Vec2,
    target_pos: Vec2,
    defenders: list[tuple[Vec2, Vec2]],
    driver_speed: float,
    animation_delay_s: float = 0.0,
    margin_threshold_ms: float = 100.0,
) -> DriveViabilityResult:
    """
    Evaluate whether a drive to the rim is viable given help defenders.

    The driver moves from driver_pos toward target_pos at driver_speed.
    During the animation delay (gather step, first-step animation), the
    driver is stationary but help defenders are already rotating.

    Args:
        driver_pos: current position of the ball handler
        driver_vel: current velocity of the driver (used for momentum direction)
        target_pos: destination (typically near the rim)
        defenders: list of (position, velocity) for each help defender
        driver_speed: drive speed in units/sec
        animation_delay_s: gather/first-step delay before movement starts
        margin_threshold_ms: minimum margin in ms for drive to be viable

    Returns:
        DriveViabilityResult with viability decision and timing breakdown.
    """
    drive_dist = (target_pos - driver_pos).length()
    if driver_speed <= 0:
        raise ValueError("driver_speed must be positive")

    time_to_target = drive_dist / driver_speed

    # Drive path: driver moves from driver_pos to target_pos
    drive_vec = target_pos - driver_pos
    if drive_dist == 0:
        return DriveViabilityResult(
            viable=True,
            time_to_target=0.0,
            animation_delay_s=round(animation_delay_s, 4),
            effective_execution_time=round(animation_delay_s, 4),
            earliest_help_arrival=float("inf"),
            margin_ms=float("inf"),
        )

    drive_dir = Vec2(drive_vec.x / drive_dist, drive_vec.y / drive_dist)

    # For each help defender, find if they can reach any point on the drive
    # path before the driver arrives at that point.
    earliest_help = float("inf")

    steps = 100
    for def_pos, def_vel in defenders:
        defender_speed = def_vel.length()
        if defender_speed <= 0:
            # Stationary defender — check if they're already on the path
            for i in range(steps + 1):
                frac = i / steps
                t_driver = frac * time_to_target
                point_on_path = driver_pos + drive_dir * (driver_speed * t_driver)
                d = (point_on_path - def_pos).length()
                if d < 1.0:  # within 1 foot = in the lane
                    earliest_help = min(earliest_help, t_driver)
                    break
            continue

        for i in range(steps + 1):
            frac = i / steps
            t_driver = frac * time_to_target  # time driver reaches this point

            # Position on drive path
            point_on_path = driver_pos + drive_dir * (driver_speed * t_driver)

            # Distance from defender to this point
            d = (point_on_path - def_pos).length()

            # Time for defender to reach this point
            t_defender = d / defender_speed

            # Defender has animation_delay + t_driver seconds total
            # (defender starts moving at input time, driver starts after delay)
            if t_defender <= animation_delay_s + t_driver:
                earliest_help = min(earliest_help, t_driver)
                break

    margin_s = earliest_help - time_to_target
    margin_ms = margin_s * 1000.0
    viable = margin_ms > margin_threshold_ms

    return DriveViabilityResult(
        viable=viable,
        time_to_target=round(time_to_target, 4),
        animation_delay_s=round(animation_delay_s, 4),
        effective_execution_time=round(animation_delay_s + time_to_target, 4),
        earliest_help_arrival=round(earliest_help, 4) if earliest_help != float("inf") else float("inf"),
        margin_ms=round(margin_ms, 2) if margin_ms != float("inf") else float("inf"),
    )
