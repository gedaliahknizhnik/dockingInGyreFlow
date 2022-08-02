from enum import Enum

import numpy as np

import anglefunctions
import flowfield
import swimmer


class FlowDirection(Enum):
    IN = -1
    OUT = 1


class FlowOrientation(Enum):
    CW = -1
    CCW = 1


class ApproachController:
    """
    Models a controller that drives a mobile boat towards a target boat using the flow.
    """

    time_to_convergence = 2  # [s]
    convergence_threshold = 0.01  # [m]

    def __init__(
        self,
        flow_model: flowfield.GyreFlow,
        flow_ori: FlowOrientation,
        flow_dir: FlowDirection,
        time_step: float,
    ) -> None:
        """Creates a controller object by storing the flowfield and setting params"""

        # Control params
        self.Kp = 0.5
        self.vel_from_thrusters = 0.01

        # Flow model
        self.flow_model = flow_model
        self.flow_ori = flow_ori
        self.flow_dir = flow_dir

        # Data to store
        self.convergence_count = 0
        self.convergence_count_threshold = self.time_to_convergence / time_step
        self.r_diff = np.inf
        self.theta_diff = np.inf

    def get_control_vel(self, pos: np.ndarray, targ: np.ndarray) -> np.ndarray:
        """
        Gets the velocity to apply to the mobile boat. The controller looks like:

            r_des = r_targ + Kp*phase_error

        and the applied velocity is either out or in along the phase direction.

        Inputs:
            pos: numpy [x, y, theta] pose of the mobile swimmer
            targ: numpy [x, y, theta] pose of the target swimmer

        Outputs:
            control_vel: [dx, dy, dtheta] velocity to apply to the mobile boat.

        """

        r_mob, theta_mob = self.flow_model.get_state(pos)
        r_targ, theta_targ = self.flow_model.get_state(targ)

        err = anglefunctions.wrap_to_pi(theta_targ - theta_mob) * self.flow_ori.value

        r_des = r_targ + self.Kp * err * self.flow_dir.value
        dir = 1 if r_des > r_mob else -1

        # print(f"{theta_mob=: 0.3} {theta_targ=: 0.3} {err=:0.3}")
        # print(f"{dir=} {r_targ=} {r_des=: 0.3} {r_mob=: 0.3}")
        # print()

        control_vel = (
            dir
            * self.vel_from_thrusters
            * np.array((np.cos(theta_mob), np.sin(theta_mob), 0))
        )

        # Store data
        self.r_diff = r_targ - r_mob
        self.theta_diff = err

        return control_vel

    def evaluate_convergence(self) -> bool:

        total_err = np.sqrt(self.r_diff**2 + self.theta_diff**2)

        if total_err <= self.convergence_threshold:
            self.convergence_count += 1
        else:
            self.convergence_count = 0

        return self.convergence_count >= self.convergence_count_threshold
