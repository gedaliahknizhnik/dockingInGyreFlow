from typing import Optional

import matplotlib.pyplot as plt
import numpy as np


class Swimmer:
    """Defines a point-mass swimmer with 2D position and orientation"""

    def __init__(self, pose: np.ndarray, lifespan: int) -> None:
        """Creates a swimmer.

        Inputs:
            pose: numpy 2D pose [x,y,theta]
            lifespan: int number of simulation steps that will be taken

        """

        self.life = 0
        self.lifespan = lifespan

        self.poseHist = np.zeros((self.lifespan, 4))  # [t, x, y, theta]
        self.poseHist[0, 1:] = pose

    def get_pose(self) -> np.ndarray:
        """Returns the current pose of the swimmer"""

        return self.poseHist[self.life, 1:]

    def update(
        self,
        t: float,
        vel: np.ndarray,
        contVel: Optional[np.ndarray] = np.array((0, 0, 0)),
    ) -> None:
        """
        Updates the position of the swimmer given a velocity and time.
            Assumes given velocity applied from the last time to the given time.

        Inputs:
            t: time at the update step
            vel: numpy 2D velocity [xdot, ydot, thetadot]
            contVel: optional velocity imparted by a controller [xdot, ydot, thetadot]

        """

        if self.life >= self.lifespan - 1:
            raise IndexError("Simulation has gone on too long...")

        dt = t - self.poseHist[self.life, 0]

        # If vel = [dx, dy] -> use vel = [dx, dy, 0]
        if len(vel) == 2:
            vel = np.hstack((vel, 0))

        newPose = self.poseHist[self.life, 1:] + (vel + contVel) * dt

        self.life += 1
        self.poseHist[self.life, 0] = t
        self.poseHist[self.life, 1:] = newPose

    def plot(self, ax: plt.Axes, *args, **kwargs) -> None:
        """
        Plots the trajectory of the swimmer on the given axes

        Inputs:
            ax: matplotlib axes object for plotting on
            *args, **kwargs: matplotlib plotting parameters passed
                             directly along to the plot command
        """

        traj = self.poseHist[: self.life + 1, 1:3]
        ax.plot(traj[:, 0], traj[:, 1], *args, **kwargs)
        plt.draw()


def main():

    f, ax = plt.subplots()

    s = Swimmer(np.array((0, 0, 0)), 10)
    for i in range(9):
        s.update(i + 1, np.array((0, 1, 0)))

    s.plot(ax, "r-")
    plt.show()
    pass


if __name__ == "__main__":
    main()
