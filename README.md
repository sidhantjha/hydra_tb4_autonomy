# Hydra + TurtleBot4 Autonomy Stack (Monorepo)

This repository contains a **fully working, end-to-end autonomy stack** for a TurtleBot4 in Gazebo, integrated with the **MIT SPARK Kimera-Hydra 3D Scene Graph pipeline**.

The goal of this repo is **zero-friction reproducibility**:
> clone → build → run

Everything lives in **one repository**, including:
- Hydra / Kimera workspace
- TurtleBot4 simulation workspace
- A custom odometry-based waypoint follower (no Nav2, no AMCL)

---

## Verified Working Environment

This stack has been tested and confirmed working on:

- **OS:** Ubuntu 24.04.3 LTS (Noble)
- **ROS 2:** Jazzy Jalisco
- **Gazebo:** Gazebo Sim 8.10.0
- **Python:** 3.12.3
- **Robot:** TurtleBot4 (Gazebo simulation)

---

## Repository Structure
hydra_tb4_autonomy/
├── hydra_ws/ # Kimera-Hydra + PGMO (source workspace)
│ ├── src/
│ ├── build/ (ignored)
│ └── install/ (ignored)
│
├── tb4_ws/ # TurtleBot4 simulation workspace
│ ├── src/
│ ├── build/ (ignored)
│ └── install/ (ignored)
│
├── hydra_tb4_stack/ # Custom autonomy + integration stack
│ └── src/
│ └── hydra_tb4_stack/
│ ├── waypoint_follower.py
│ ├── warehouse_waypoints.py
│ └── launch/
│
└── README.md


---

## System Architecture
Gazebo (TurtleBot4)
├── /odom
├── /scan
├── /tf
└── /cmd_vel_unstamped
▲
Waypoint Follower (odom frame)
▲
Warehouse Waypoints

Hydra Pipeline
├── Frontend (perception)
├── Backend (PGMO)
└── 3D Scene Graph

RViz
├── TF
├── LaserScan
└── Hydra markers


### Key Design Decisions
- No Nav2
- No AMCL
- No `map → odom` dependency
- Ground-truth odometry from Gazebo
- Lightweight custom waypoint controller
- Perception-first autonomy via Hydra

---

## Waypoints

Waypoints are defined **in the odom frame**.

**File:**
hydra_tb4_stack/src/hydra_tb4_stack/warehouse_waypoints.py

Example:
```python
WAREHOUSE_WAYPOINTS = [
    (0.0, 0.0),
    (1.5, 0.0),
    (1.5, 2.0),
    (0.0, 2.0),
    (0.0, 0.0),
]
```
🛠️ System Dependencies
ROS 2
sudo apt install ros-jazzy-desktop

TurtleBot4 Simulation
sudo apt install ros-jazzy-turtlebot4*
sudo apt install ros-jazzy-turtlebot4-gz-bringup

Gazebo

Installed automatically with TB4 simulation packages.

🐍 Python Environment (Optional but Recommended)
```
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install numpy scipy pyyaml matplotlib
```

ROS Python packages (rclpy, etc.) are provided by ROS and must not be installed via pip.

🔧 Build Instructions
1. Source ROS
source /opt/ros/jazzy/setup.bash

2. Build Hydra
cd hydra_ws
colcon build --symlink-install
source install/setup.bash
cd ..

3. Build TurtleBot4 workspace
cd tb4_ws
colcon build --symlink-install
source install/setup.bash
cd ..

4. Build Autonomy Stack
cd hydra_tb4_stack
colcon build --symlink-install
source install/setup.bash
cd ..

▶️ Running the Full Stack
source /opt/ros/jazzy/setup.bash
source hydra_ws/install/setup.bash
source tb4_ws/install/setup.bash
source hydra_tb4_stack/install/setup.bash

ros2 launch hydra_tb4_stack tb4_warehouse_hydra.launch.py

🧭 RViz (Hydra Visualization)
ros2 launch hydra_tb4_stack hydra_rviz.launch.py


RViz settings:

Fixed Frame: odom

Displays:

TF

LaserScan (/scan)

MarkerArray (/hydra/frontend/markers)

MarkerArray (/hydra/backend/markers)

🚀 What This Stack Is For

Perception-first autonomy research

Kimera-Hydra experimentation

Custom planning and control

Multi-robot extensions

Academic / lab-grade prototyping

⚠️ Notes

This is a research stack, not a productized navigation system.

The monorepo approach prioritizes reproducibility over minimal size.

If GitHub size limits become an issue, this repo can be converted to submodules.
