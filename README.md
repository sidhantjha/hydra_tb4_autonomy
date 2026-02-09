# Hydra + TurtleBot4 Autonomy Stack (Monorepo)

This repository contains a fully working, end to end autonomy stack for a TurtleBot4 in Gazebo, integrated with the MIT SPARK Kimera Hydra 3D Scene Graph pipeline.

The goal of this repository is zero friction reproducibility.

Clone the repository, build the workspaces, and run the full autonomy stack without manual patching or environment specific fixes.

Everything lives in a single monorepo, including the Hydra workspace, the TurtleBot4 simulation workspace, and a custom odometry based waypoint follower that does not rely on Nav2 or AMCL.

---

## Verified Working Environment

This stack has been tested and confirmed working on the following configuration.

Operating system  
Ubuntu 24.04.3 LTS (Noble)

ROS 2 distribution  
Jazzy Jalisco

Gazebo  
Gazebo Sim 8.10.0

Python  
Python 3.12.3

Robot  
TurtleBot4 in Gazebo simulation

---

## Repository Structure

```
hydra_tb4_autonomy/
├── hydra_ws/
│   ├── src/
│   ├── build/
│   └── install/
│
├── tb4_ws/
│   ├── src/
│   ├── build/
│   └── install/
│
├── hydra_tb4_stack/
│   └── src/
│       └── hydra_tb4_stack/
│           ├── waypoint_follower.py
│           ├── warehouse_waypoints.py
│           └── launch/
│
└── README.md
```

The repository is intentionally structured as a monorepo to ensure deterministic builds and consistent environment sourcing across machines.

---

## System Architecture

The autonomy stack uses Gazebo ground truth odometry as the global reference frame.

```
Gazebo (TurtleBot4)
├── /odom
├── /scan
├── /tf
└── /cmd_vel_unstamped
        ▲
        Waypoint Follower (odom frame)
        ▲
        Warehouse Waypoints
```

The perception pipeline runs in parallel.

```
Hydra Pipeline
├── Frontend (perception)
├── Backend (PGMO)
└── 3D Scene Graph
```

Visualization is handled through RViz.

```
RViz
├── TF
├── LaserScan
└── Hydra markers
```

---

## Key Design Decisions

This stack deliberately avoids Nav2 and AMCL.

Localization is not performed using a map to odom transform.

Gazebo odometry is treated as ground truth.

Waypoint following is implemented through a lightweight custom controller operating directly in the odom frame.

The autonomy stack is perception first and designed to support Hydra driven reasoning and planning.

---

## Waypoints

Waypoints are defined directly in the odom frame.

File location

```
hydra_tb4_stack/src/hydra_tb4_stack/warehouse_waypoints.py
```

Example waypoint definition

```python
WAREHOUSE_WAYPOINTS = [
    (0.0, 0.0),
    (1.5, 0.0),
    (1.5, 2.0),
    (0.0, 2.0),
    (0.0, 0.0),
]
```

---

## System Dependencies

ROS 2 Jazzy

```
sudo apt install ros-jazzy-desktop
```

TurtleBot4 simulation

```
sudo apt install ros-jazzy-turtlebot4*
sudo apt install ros-jazzy-turtlebot4-gz-bringup
```

Gazebo is installed automatically with the TurtleBot4 simulation packages.

---

## Python Environment

Using a Python virtual environment is optional but recommended for non ROS tooling.

```
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install numpy scipy pyyaml matplotlib
```

ROS Python packages such as rclpy must be provided by the ROS installation and must not be installed via pip.

---

## Build Instructions

Source ROS

```
source /opt/ros/jazzy/setup.bash
```

Build the Hydra workspace

```
cd hydra_ws
colcon build --symlink-install
source install/setup.bash
cd ..
```

Build the TurtleBot4 workspace

```
cd tb4_ws
colcon build --symlink-install
source install/setup.bash
cd ..
```

Build the autonomy stack

```
cd hydra_tb4_stack
colcon build --symlink-install
source install/setup.bash
cd ..
```

---

## Running the Full Stack

Source all environments

```
source /opt/ros/jazzy/setup.bash
source hydra_ws/install/setup.bash
source tb4_ws/install/setup.bash
source hydra_tb4_stack/install/setup.bash
```

Launch Gazebo, Hydra, and the waypoint follower

```
ros2 launch hydra_tb4_stack tb4_warehouse_hydra.launch.py
```

---

## RViz Visualization

Launch RViz with Hydra configuration

```
ros2 launch hydra_tb4_stack hydra_rviz.launch.py
```

RViz configuration

Fixed frame  
odom

Enabled displays

TF  
LaserScan on topic /scan  
MarkerArray on topic /hydra/frontend/markers  
MarkerArray on topic /hydra/backend/markers  

---

## Intended Use

This repository is designed for perception first autonomy research.

It supports Kimera Hydra experimentation, custom planning and control development, and multi robot extensions.

It is intended for academic and lab grade prototyping rather than production navigation systems.

---

## Notes

This is a research stack and not a productized navigation solution.

The monorepo structure prioritizes reproducibility over minimal repository size.

If repository size limits become a concern, the workspaces can be migrated to git submodules without changing the system architecture.
