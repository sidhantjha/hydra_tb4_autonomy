# Hydra 3D Scene Graph Pipeline — TurtleBot3 Gazebo Integration

> **End-to-end 3D Dynamic Scene Graph generation from a custom simulated robot, running MIT SPARK Hydra on ROS2 Jazzy without ground-truth semantics or the official uHumans2 dataset.**

---

## What This Is

This repository documents and implements a fully working integration of [MIT SPARK Hydra](https://github.com/MIT-SPARK/Hydra) — a state-of-the-art 3D Dynamic Scene Graph pipeline — running on a custom ROS2 bag recorded from a TurtleBot3 Waffle Gazebo simulation.

The core challenge: Hydra is designed for the uHumans2 dataset with a specific sensor suite. This stack makes it work on a completely different robot and sensor configuration, without modifying Hydra's core source code.

---

## Results

### 3D Mesh Reconstruction
> *(placeholder — insert RViz screenshot of mesh)*

### Scene Graph Visualization
> *(placeholder — insert RViz screenshot showing graph with rooms, places, objects layers)*

### TSDF Occupancy Map
> *(placeholder — insert occupancy grid screenshot)*

### Live Camera + Scene Graph
> *(placeholder — insert composite RViz view)*

---

## Verified Working Environment

| Component | Version |
|---|---|
| OS | Ubuntu 24.04.3 LTS (Noble) |
| ROS 2 | Jazzy Jalisco |
| Gazebo | Gazebo Sim 8.10.0 |
| Python | 3.12.3 |
| Robot | TurtleBot3 Waffle (Gazebo) |
| Hydra | MIT SPARK Hydra (ROS2 branch) |

---

## Repository Structure

```
hydra_tb4_autonomy/
├── hydra_ws/                          # MIT SPARK Hydra workspace
│   └── src/
│       ├── hydra_ros/                 # ROS2 Hydra node + launch files
│       ├── spark_dsg/                 # Dynamic Scene Graph library
│       └── kimera_pgmo/               # Pose Graph Mesh Optimization
│
├── tb3_custom_description/            # Modified TB3 sensor stack
│   ├── models/turtlebot3_waffle/
│   │   └── model.sdf                  # SDF with added depth camera sensor
│   └── params/
│       └── turtlebot3_waffle_bridge.yaml  # ROS-Gazebo bridge with depth topic
│
├── scripts/
│   ├── hydra_resizer.py               # Image resize + semantic relay node
│   └── launch_hydra.sh                # Full pipeline launcher
│
├── datasets/                          # ROS2 bags (gitignored)
│
└── README.md
```

---

## System Architecture

### Sensor Pipeline
```
TurtleBot3 Waffle (Gazebo)
├── /camera/image_raw          (RGB, 1920x1080)
├── /camera/depth/image_raw    (Depth, 32FC1, 640x480)  ← added via SDF edit
├── /camera/camera_info
├── /imu
├── /odom
├── /tf + /tf_static
└── /clock
        │
        ▼
   Topic Relay Layer
   (remap to /tesse/* uHumans2 conventions)
        │
        ▼
   Python Resizer Node
   (resize RGB to 640x480, generate zero-label semantic mask)
        │
        ▼
   Static TF Publishers
   (world→odom→base_footprint→base_link→base_link_gt→camera frames)
        │
        ▼
   MIT SPARK Hydra
   ├── Input Module (RGB + Depth + Semantic)
   ├── Active Window Module
   ├── Frontend (TSDF + GVD + Places)
   ├── Backend (PGMO + Scene Graph)
   └── Hydra Visualizer
        │
        ▼
   RViz
   ├── 3D Mesh
   ├── Scene Graph (Buildings → Rooms → Places → Objects)
   ├── TSDF Occupancy
   └── Pose Graph
```

---

## Key Engineering Challenges Solved

### 1. Depth Camera Did Not Exist
TurtleBot3 Waffle ships with RGB only in Gazebo. Added a `depth_camera` sensor block to the SDF and a corresponding ROS-Gazebo bridge entry to produce real `32FC1` depth images.

### 2. Silent TSDF Integration Failure
Hydra requires a semantic image input even when not using ground-truth semantics. Without it, Hydra runs silently and produces no output. Discovered via `ros2 node info /hydra | grep Subscribers` and resolved by publishing a zero-label semantic mask.

### 3. TF Tree Disconnection
Hydra needs `world → base_link_gt` but the TB3 bag only contains `odom → base_footprint`. Required a chain of 5 static TF publishers to bridge the trees.

### 4. Image Resolution Mismatch
RGB camera outputs 1920x1080 but depth camera outputs 640x480. Hydra requires all inputs to match. Built a Python node using OpenCV to resize RGB and generate matching semantic masks on-the-fly.

### 5. uHumans2 Config Assumptions
Hydra's stock uHumans2 config hardcodes `base_link_gt`, `stereo_left_camera`, and expects a running ONNX semantic inference model. Each required targeted config edits and TF alias injection without modifying Hydra's core code.

---

## Quick Start

### 1. Install dependencies
```bash
# ROS2 Jazzy
sudo apt install ros-jazzy-desktop-full

# TurtleBot3
sudo apt install ros-jazzy-turtlebot3* ros-jazzy-turtlebot3-simulations*

# Pipeline tools
sudo apt install ros-jazzy-topic-tools ros-jazzy-depth-image-proc \
  ros-jazzy-image-transport ros-jazzy-cv-bridge

# Python
pip install pyzmq networkx matplotlib rosbags opencv-python
```

### 2. Install custom TB3 SDF with depth camera
```bash
sudo cp tb3_custom_description/models/turtlebot3_waffle/model.sdf \
  /opt/ros/jazzy/share/turtlebot3_gazebo/models/turtlebot3_waffle/model.sdf

sudo cp tb3_custom_description/params/turtlebot3_waffle_bridge.yaml \
  /opt/ros/jazzy/share/turtlebot3_gazebo/params/turtlebot3_waffle_bridge.yaml
```

### 3. Build Hydra workspace
```bash
cd hydra_ws
colcon build
source install/setup.bash
```

### 4. Record a bag
```bash
# Launch TB3 house world
source /opt/ros/jazzy/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo turtlebot3_house.launch.py

# Record
ros2 bag record \
  /camera/image_raw /camera/camera_info /camera/depth/image_raw \
  /imu /odom /tf /tf_static /clock \
  -o datasets/tb3_bag
```

### 5. Run the full pipeline
```bash
# Terminal 1 — Static TFs
source /opt/ros/jazzy/setup.bash
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 world odom &
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 base_footprint base_link &
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 base_link base_link_gt &
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 base_link camera_rgb_frame &
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 base_link camera_depth_frame &

# Terminal 2 — Play bag
ros2 bag play datasets/tb3_bag --clock \
  --qos-profile-overrides-path ~/.tf_overrides.yaml

# Terminal 3 — Topic relays
ros2 run topic_tools relay /camera/depth/image_raw /tesse/depth_cam/mono/image_raw &
ros2 run topic_tools relay /camera/depth/image_raw /tesse/left_cam/depth_registered/image_rect &
ros2 run topic_tools relay /imu /tesse/imu/clean/imu &
ros2 run topic_tools relay /odom /tesse/odom &

# Terminal 4 — Image resizer + semantic generator
python3 scripts/hydra_resizer.py

# Terminal 5 — Launch Hydra (after 10s)
cd hydra_ws && source install/setup.bash
ros2 launch hydra_ros uhumans2.launch.yaml \
  use_gt_semantics:=false \
  semantic_colormap_file:=$(ros2 pkg prefix hydra_ros)/share/hydra_ros/config/color/uhumans2_office.csv

# Terminal 6 — RViz
rviz2 -d $(ros2 pkg prefix hydra_ros)/share/hydra_ros/rviz/hydra.rviz
```

---

## Config Changes from Stock Hydra

| File | Change | Reason |
|---|---|---|
| `uhumans2.yaml` | `max_range: 5.0 → 10.0` | TB3 depth range up to 8m |
| `uhumans2.yaml` | `robot_frame: base_link_gt` | Kept, bridged via TF alias |
| `uhumans2.launch.yaml` | `closed_set_node` disabled | ONNX model not available |
| `model.sdf` | Added `depth_camera` sensor | TB3 has no depth by default |
| `turtlebot3_waffle_bridge.yaml` | Added depth topic bridge | Required for ROS-Gazebo depth |

---

## Hydra Output Topics

| Topic | Type | Description |
|---|---|---|
| `/hydra/reconstruction/mesh` | `kimera_pgmo_msgs/Mesh` | 3D mesh reconstruction |
| `/hydra/frontend/dsg` | `hydra_msgs/DsgUpdate` | Scene graph (frontend) |
| `/hydra/backend/dsg` | `hydra_msgs/DsgUpdate` | Scene graph (backend) |
| `/hydra/tsdf/occupancy` | `nav_msgs/OccupancyGrid` | TSDF occupancy map |
| `/hydra/gvd/occupancy` | `nav_msgs/OccupancyGrid` | GVD occupancy |
| `/hydra_visualizer/mesh` | `visualization_msgs/MarkerArray` | RViz mesh markers |
| `/hydra_visualizer/graph` | `visualization_msgs/MarkerArray` | RViz graph markers |

---

## Intended Use

This stack is designed for spatial AI and scene understanding research. It demonstrates:

- Running state-of-the-art 3D scene graph pipelines on custom robot data
- Sensor integration and ROS2 topic bridging for non-standard configurations
- Foundation for multi-robot distributed scene graph architectures

---

## References

- [MIT SPARK Hydra](https://github.com/MIT-SPARK/Hydra)
- [Rosinol et al., 3D Dynamic Scene Graphs, RSS 2020](https://arxiv.org/abs/2002.06289)
- [Hughes et al., Hydra, RSS 2022](https://arxiv.org/abs/2201.13360)
- [uHumans2 Dataset](http://web.mit.edu/sparklab/datasets/uHumans2/)
