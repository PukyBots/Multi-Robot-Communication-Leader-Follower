
# 🤖 Multi-Robot Communication System

### Leader–Follower Architecture | ROS 2 Humble | Raspberry Pi 4

---

> **Two robots communicate over WiFi using ROS 2 topics. The Leader robot is controlled using a keyboard and continuously publishes its odometry data (position and orientation). The Follower robot subscribes to this data, calculates the positional error, and replicates the movement in real time — demonstrating coordinated multi-robot communication over a shared network.**

**Problem Statement:** Coordinating multiple robots in real time without centralized infrastructure is a core challenge in robotics. This project solves it using a decentralized ROS 2 publisher-subscriber model over WiFi.

---

## 🚀 Use Cases

This project demonstrates real-time coordination between multiple robots using a decentralized communication model. It can be applied in various real-world scenarios:

- **Warehouse Automation:** A leader robot can guide multiple follower robots for transporting goods efficiently.
- **Search and Rescue Operations:** Robots can navigate hazardous environments where a leader unit explores and others follow safely.
- **Agricultural Robotics:** One robot can scan or map the field while others perform tasks such as spraying or seeding.
- **Autonomous Convoy Systems:** Multiple unmanned vehicles can follow a lead vehicle in defense or logistics applications.

> The key advantage of this system is reduced human intervention and scalable multi-robot coordination.

---

## 🔮 Future Enhancements / Project Extensions

The current system can be further extended into the following advanced projects:

1.**Multi-Follower Coordination System:** Extend the system to support multiple follower robots maintaining formation with a single leader.<br>
2.**Obstacle-Aware Navigation:** Integrate sensors (ultrasonic/LiDAR) to enable the follower robot to avoid obstacles while still tracking the leader.<br>
3.**Path Recording and Replay System:** Store the leader’s trajectory and allow follower robots to replicate the same path later without real-time communication.<br>
4.**Vision-Based Tracking System:** Use computer vision techniques to track the leader instead of relying only on odometry data.<br>
5.**Real-Time Monitoring Dashboard:** Develop a dashboard to visualize robot movement, communication data, and performance metrics in real time.

---

## 📌 Table of Contents

- [Project Overview](#-project-overview)
- [System Architecture](#️-system-architecture)
- [Hardware Components](#-hardware-components)
- [Circuit Connections](#-circuit-connections)
- [Leader Robot Setup](#-leader-robot-setup)
  - [1. Flashing Ubuntu on Raspberry Pi](#1-flashing-ubuntu-on-raspberry-pi)
  - [2. SSH Remote Access](#2-ssh-remote-access)
  - [3. Fixing Hostname Resolution on Windows](#3-fixing-hostname-resolution-on-windows)
  - [4. Updating the Pi](#4-updating-the-pi)
  - [5. Installing ROS 2 Humble](#5-installing-ros-2-humble)
  - [6. Creating ROS 2 Workspace](#6-creating-ros-2-workspace)
  - [7. Uploading Arduino Code](#7-uploading-arduino-code)
  - [8. Writing Leader Node](#8-writing-leader-node)
  - [9. Running the Leader Robot](#9-running-the-leader-robot)
- [Follower Robot Setup](#-follower-robot-setup)
  - [1. Flashing Ubuntu on Follower Pi](#1-flashing-ubuntu-on-follower-pi)
  - [2. SSH into Follower Pi](#2-ssh-into-follower-pi)
  - [3. Fixing Hostname Resolution for Follower](#3-fixing-hostname-resolution-for-follower)
  - [4. Updating the Follower Pi](#4-updating-the-follower-pi)
  - [5. Installing ROS 2 Humble on Follower](#5-installing-ros-2-humble-on-follower)
  - [6. Creating Follower Workspace](#6-creating-follower-workspace)
  - [7. Uploading Arduino Code to Follower](#7-uploading-arduino-code-to-follower)
  - [8. Writing Follower Node](#8-writing-follower-node)
  - [9. Running the Follower Robot](#9-running-the-follower-robot)
  - [10. Independent Motor Test via ROS 2 (Pre-Integration)](#10-independent-motor-test-via-ros-2-pre-integration)
- [ROS 2 Topics](#-ros-2-topics)
- [Code Structure](#-code-structure)
- [Current Progress](#-current-progress)
- [Acknowledgements](#-acknowledgements)
- [Team](#-team)

---

## 📖 Project Overview

This project implements a **Multi-Robot Communication System** using a Leader–Follower architecture built on **ROS 2 Humble**.

The system works as follows:
- The **Leader Robot** moves based on keyboard input (W/A/S/D keys).
- The Leader's **encoder motors** track its movement and calculate **odometry** (x position, y position, and orientation/theta).
- This odometry data is **published over WiFi** using the ROS 2 `/odom` topic on a shared hotspot network.
- The **Follower Robot** subscribes to this `/odom` topic, calculates the positional error between its current position and the leader's position, and sends motor commands to close that gap — replicating the leader's path.

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────┐                   
│                    Shared WiFi Hotspot                   │
│                                                          │
│   ┌─────────────────────┐    ┌─────────────────────┐     │           
│   │    Leader Robot     │    │   Follower Robot    │     │
│   │─────────────────────│    │─────────────────────│     │
│   │  Raspberry Pi 4     │    │  Raspberry Pi 4     │     │
│   │  Arduino Nano       │    │  Arduino Nano       │     │
│   │  Encoder Motors     │    │  DC Motors          │     │
│   │  MDD10A Driver      │    │  L298N Driver       │     │
│   │                     │    │                     │     │           
│   │  Publishes:         │--->│ Subscribes:         │     │
│   │    /cmd_vel         │    │    /odom            │     │
│   │    /odom            │    │                     │     │ 
│   └─────────────────────┘    └─────────────────────┘     │
└──────────────────────────────────────────────────────────┘
```

---

## 🔧 Hardware Components

### Leader Robot

| Component | Purpose |
|---|---|
| Raspberry Pi 4 Model B | Main brain — runs Ubuntu 22.04 and ROS 2 Humble |
| Arduino Nano | Reads encoder pulses and controls motors via serial commands from Pi |
| Encoder Motors (x2) | DC motors with encoders for precise odometry calculation |
| MDD10A Motor Driver | Amplifies Arduino signals to drive motors at 12V |
| Custom PCB Board | Connects all components in a clean, organized manner |
| 12V Power Adapter | Powers the motor driver and Arduino; Pi is powered separately |

### Follower Robot

| Component | Purpose |
|---|---|
| Raspberry Pi 4 Model B | Main brain — runs Ubuntu 22.04 and ROS 2 Humble |
| Arduino Nano | Receives motor commands from Pi and drives motors |
| L298N Motor Driver | Amplifies Arduino signals to drive DC motors at 12V |
| DC Motors (x2) | Standard DC motors for physical movement |
| 12V Power Adapter | Powers the motor driver and Arduino |
| Pi Power Adapter (5V) | Powers the Raspberry Pi 4 via USB-C separately |

> ⚠️ **Note:** A buck converter was tested but caused power instability issues. Both robots now use a dedicated Pi adapter (5V USB-C) for the Raspberry Pi and the 12V adapter solely for the motor driver and Arduino.

---

## ⚡ Circuit Connections

### Leader Robot — Arduino Nano Pin Connections

**Encoder Pins:**

| Encoder | Arduino Nano Pin |
|---|---|
| Right Encoder A | D3 |
| Right Encoder B | D2 |
| Left Encoder A | A4 |
| Left Encoder B | A5 |

> 📎 [`leader/left_motor.png`](leader/left_motor.png) — [`leader/right_motor.png`](leader/right_motor.png)

---

**Motor Control Pins (MDD10A ↔ Arduino Nano):**

| Signal | Arduino Nano Pin |
|---|---|
| M1 PWM | D10 |
| M1 DIR | D6 |
| M2 PWM | D9 |
| M2 DIR | D5 |

> 📎 [`leader/MD_Nano.png`](leader/MD_Nano.png)

---

**Raspberry Pi ↔ Arduino Nano (USB):**

| From | To | Cable |
|---|---|---|
| Raspberry Pi 4 USB 2.0 Port | Arduino Nano Mini-B USB Port | USB 2.0 A to Mini-B |

> 📎 [`leader/Pi_Nano.png`](leader/Pi_Nano.png)

---

**Power Connections (12V Adapter → Buck Converter → Pi & Motor Driver):**

| From | To |
|---|---|
| 12V Adapter (+) | B+ (MDD10A Motor Driver) |
| 12V Adapter (−) | B− (MDD10A Motor Driver) |
| 12V Adapter (+) | IN+ (Buck Converter) |
| 12V Adapter (−) | IN− (Buck Converter) |
| Buck Converter OUT+ | 5V (Raspberry Pi via USB-C) |
| Buck Converter OUT− | GND (Raspberry Pi) |

> 📎 [`leader/power.png`](leader/power.png)

> ℹ️ **Note:** The connection diagram shows a LiPo battery for reference. The actual setup uses a 12V power adapter as the power source.

---

**Full Wiring Overview:**

> 📎 [`leader/diagram1.png`](leader/diagram1.png)

> ⚠️ **Note:** The leader robot uses a custom PCB that integrates the MDD10A motor driver, Arduino Nano, and power connections. The above diagrams are provided as fragments since a single unified diagram is not available. Refer to the pin tables above for exact wiring.

---

### Follower Robot — Arduino Nano to L298N

| L298N Pin | Arduino Pin | Why |
|---|---|---|
| IN1 | D5 | Controls left motor direction |
| IN2 | D6 | Controls left motor direction |
| IN3 | D9 | Controls right motor direction |
| IN4 | D10 | Controls right motor direction |
| ENA | D3 | PWM speed control for left motor |
| ENB | D11 | PWM speed control for right motor |

**Motor to Motor Driver (L298N):**

| L298N Terminal | Connection |
|---|---|
| OUT1 | Left Motor + |
| OUT2 | Left Motor − |
| OUT3 | Right Motor + |
| OUT4 | Right Motor − |

> ⚠️ **Note:** If both wheels spin in opposite directions when FORWARD is sent, swap the two wires of one motor on the L298N output terminals.

> 📎 **Circuit Diagram:** The follower robot's full connection diagram is available at [`follower/connection diagram.jpeg`](follower/connection%20diagram.jpeg). Refer to the pin tables above for exact wiring.

---

### Power Connections

**Leader Robot:**
```
12V Power Adapter
      |
      └──→ Buck Converter IN+ and IN−
                |
                ├──→ MDD10A B+ and B−
                │         |
                │         ├──→ Motors (via M1A, M1B, M2A, M2B)
                │         └──→ Arduino Nano (via MDD10A 5V out and GND)
                │
                └──→ Raspberry Pi 4 (via OUT+ and OUT−)
```

**Follower Robot:**
```
12V Power Adapter
      |
      └──→ L298N 12V IN (+) and GND (−)
                |
                ├──→ Motors (via OUT1–OUT4)
                └──→ Arduino Nano (via L298N 5V out and GND)

(separate) Pi Power Adapter (5V USB-C) ──→ Raspberry Pi 4
```

---

## 🚀 Leader Robot Setup

### 1. Flashing Ubuntu on Raspberry Pi

**Why this step:** The Raspberry Pi needs an operating system. Ubuntu 22.04 LTS Server is used because ROS 2 Humble officially supports only Ubuntu 22.04. The Server version (no desktop GUI) is lightweight and perfect for headless SSH-based control — no monitor needed.

**Steps:**
1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/) on your laptop
2. Insert SD card into laptop
3. Open Imager → Choose Device: **Raspberry Pi 4**
4. Choose OS → Other general-purpose OS → Ubuntu → **Ubuntu Server 22.04 LTS (64-bit)**
5. Choose Storage → Select your SD card (keep "Exclude system drives" checked ✅)
6. Click **Next → Edit Settings** and fill in:

| Field | Value |
|---|---|
| Hostname | `leader-robot` |
| Username | `pi` |
| Password | `robot1234` |
| WiFi SSID | your hotspot name |
| WiFi Password | your hotspot password |
| Timezone | Asia/Kolkata |

> 💡 **Note:** The password used in this project is `robot1234`. You may change it to your preferred password during the Ubuntu flash setup.

7. Services tab → Enable SSH ✅ → Password authentication ✅
8. Click **Save → Yes → Yes** → Wait 5–10 minutes for flashing
9. Once "Write Successful" appears → remove SD card → insert into Pi → power on

---

### 2. SSH Remote Access

**Why this step:** SSH (Secure Shell) allows remote control of the Pi from a laptop over WiFi — no monitor or keyboard needed on the Pi. This is called **headless mode** and is the standard approach for embedded robotics.

Turn on hotspot → power on Pi → wait 90 seconds → open terminal on laptop:

```bash
 ssh pi@leader-robot.local
```

Type `yes` for fingerprint confirmation → enter password → you are inside the Pi!

> ⚠️ If `leader-robot.local` fails, use the IPv6 address shown in your phone's hotspot connected devices to connect initially, then fix hostname resolution in the next step.

---

### 3. Fixing Hostname Resolution on Windows

**Why this step:** Windows sometimes resolves `.local` hostnames using IPv6, causing SSH to fail. We manually map the Pi's IPv4 address in the Windows hosts file so `leader-robot.local` always resolves correctly — without needing to look up the IP address each time.

**Step 1 — Get Pi's IPv4 address (run inside Pi):**
```bash
 hostname -I
```
Note the first IP (e.g. `10.88.164.178`)

**Step 2 — Open cmd as Administrator on Windows laptop:**
```bash
 notepad C:\Windows\System32\drivers\etc\hosts
```

**Step 3 — Add this line at the bottom:**
```
10.88.164.178    leader-robot.local
```

Save and close. Now SSH works directly every time:
```bash
 ssh pi@leader-robot.local
```

> ⚠️ If IP changes after hotspot reconnect, update this file with the new IP from `hostname -I`

---

### 4. Updating the Pi

**Why this step:** Freshly flashed Ubuntu may have outdated packages. Updating ensures all system libraries are current before ROS 2 installation.

```bash
 sudo apt update && sudo apt upgrade -y
```

---

### 5. Installing ROS 2 Humble

**Why this step:** ROS 2 is the communication middleware that enables robots to talk to each other using a publisher-subscriber model. ROS 2 Humble is chosen as it is the LTS (Long Term Support) version compatible with Ubuntu 22.04. Both robots must run the same version for topics to be compatible.

```bash
 sudo apt install curl -y
```

```bash
 sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
```

```bash
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

```bash
 sudo apt update
 sudo apt install -y ros-humble-ros-base
```

```bash
# Auto-load ROS 2 on every SSH session
 echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
 source ~/.bashrc
```

```bash
# Install build tools and Python serial library
 sudo apt install python3-colcon-common-extensions -y
 sudo apt install python3-pip -y
 pip3 install pyserial
```

---

### 6. Creating ROS 2 Workspace

**Why this step:** A ROS 2 workspace is the standard folder structure where robot code (packages and nodes) is organized, built, and executed. Without a workspace, ROS 2 cannot find and run custom nodes.

```bash
 mkdir -p ~/ros2_ws/src
 cd ~/ros2_ws
 ros2 pkg create --build-type ament_python leader_robot
```

```bash
# Auto-load workspace on every SSH session
 echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
```

---

### 7. Uploading Arduino Code

**Why this step:** The Raspberry Pi GPIO pins provide only 3.3V/16mA — not enough to drive motors. The Arduino Nano acts as the dedicated motor controller: it receives serial commands from the Pi (FORWARD, BACKWARD, LEFT, RIGHT, SMOOTH_LEFT, SMOOTH_RIGHT, STOP), converts them to PWM signals for the L298N motor driver, reads encoder pulses, and sends odometry data back to the Pi.

**Steps:**
1. Connect Arduino Nano to laptop via USB
2. Open Arduino IDE → Tools → Board → **Arduino Nano**
3. Select correct COM port
4. Upload code from [`leader/arduino/motor_control.ino`](leader/arduino/motor_control.ino)
5. Disconnect from laptop → reconnect to Pi USB port

---

### 8. Writing Leader Node

**Why this step:** `leader_node.py` is the core ROS 2 software of the leader robot. It reads keyboard input, sends motor commands to Arduino via serial, reads encoder data to calculate and publish odometry on `/odom`, and uses MultiThreadedExecutor so all callbacks run concurrently without blocking keyboard input.

```bash
 nano ~/ros2_ws/src/leader_robot/leader_robot/leader_node.py
```

See full code in [`leader/leader_node.py`](leader/leader_node.py)

Update `setup.py` entry points:

```bash
 nano ~/ros2_ws/src/leader_robot/setup.py
```

```python
'console_scripts': [
    'leader_node = leader_robot.leader_node:main',
],
```

Build the package:
```bash
 cd ~/ros2_ws && colcon build --packages-select leader_robot
 source install/setup.bash
```

---

### 9. Running the Leader Robot

```bash
 cd ~/ros2_ws && ros2 run leader_robot leader_node
```

**Keyboard Controls:**

| Key | Action |
|---|---|
| `w` | Move Forward |
| `s` | Move Backward |
| `a` | Turn Left |
| `d` | Turn Right| 
| `q` | Stop |
| `x` | Exit |

Use **W/A/S/D** keys to control the robot. Odometry is published automatically on `/odom` as the robot moves.

---

## 🤖 Follower Robot Setup

### 1. Flashing Ubuntu on Follower Pi

**Why this step:** The follower Pi needs the same Ubuntu 22.04 + ROS 2 Humble stack as the leader for ROS 2 topics to be compatible. A different hostname (`follower-robot`) is assigned so both Pis can be identified separately on the same network.

Follow the same flashing steps as the leader but use these settings:

| Field | Value |
|---|---|
| Hostname | `follower-robot` |
| Username | `pi` |
| Password | `robot1234` |
| WiFi SSID | **same hotspot as leader** ⚠️ |

> 💡 **Note:** The password used in this project is `robot1234`. You may change it to your preferred password during the Ubuntu flash setup.

> ⚠️ **Critical:** Both robots MUST connect to the same WiFi hotspot for ROS 2 topics to reach each other.

---

### 2. SSH into Follower Pi

```bash
 ssh pi@follower-robot.local
```

> ⚠️ If this fails, check phone hotspot connected devices for the IP address and connect using `ssh pi@<IP-address>`

---

### 3. Fixing Hostname Resolution for Follower

**Why this step:** Same reason as leader — Windows needs the IPv4 mapping for `follower-robot.local` to resolve correctly.

**Inside follower Pi, run:**
```bash
 hostname -I
```
Note the IPv4 address (e.g. `10.88.164.133`)

**Open hosts file on Windows (cmd as Administrator):**
```bash
 notepad C:\Windows\System32\drivers\etc\hosts
```

Add this line at the bottom (alongside leader's entry):
```
10.88.164.178    leader-robot.local
10.88.164.133    follower-robot.local
```

Save and close. Both robots now accessible by hostname directly.

---

### 4. Updating the Follower Pi

```bash
 sudo apt update && sudo apt upgrade -y
```

---

### 5. Installing ROS 2 Humble on Follower

**Why this step:** Both robots must run the exact same ROS 2 version. If versions differ, the follower cannot receive the leader's `/odom` messages.

Run the same commands as Leader Robot [Step 5](#5-installing-ros-2-humble):

```bash
 sudo apt install curl -y
```

```bash
 sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
```

```bash
 echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

```bash
 sudo apt update
```

```bash
 sudo apt install -y ros-humble-ros-base
```

```bash
 echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
```

```bash
 source ~/.bashrc
```

```bash
 sudo apt install python3-colcon-common-extensions -y
```

```bash
 sudo apt install python3-pip -y
```

```bash
 pip3 install pyserial
```

---

### 6. Creating Follower Workspace

```bash
 mkdir -p ~/ros2_ws/src
 cd ~/ros2_ws
 ros2 pkg create --build-type ament_python follower_robot
 echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
```

---

### 7. Uploading Arduino Code to Follower

**Why this step:** The follower Arduino receives FORWARD/BACKWARD/LEFT/RIGHT/STOP commands from the Pi via serial and drives the L298N motor driver with appropriate PWM signals to physically move the robot.

Upload [`follower/arduino/follower_motor.ino`](follower/arduino/follower_motor.ino) using Arduino IDE (same steps as leader).

After uploading → disconnect from laptop → reconnect to follower Pi USB port.

---

### 8. Writing Follower Node

**Why this step:** `follower_node.py` subscribes to the leader's `/odom` topic to get its real-time position. It calculates the error between the follower's current position and the leader's position, then sends motor commands to close that gap — replicating the leader's movement automatically.

```bash
 nano ~/ros2_ws/src/follower_robot/follower_robot/follower_node.py
```

See full code in [`follower/follower_node.py`](follower/follower_node.py)

Update `setup.py`:

```bash
 cd ~/ros2_ws/follower_robot
 nano setup.py
```

```python
'console_scripts': [
    'follower_node = follower_robot.follower_node:main',
],
```

Build:
```bash
 cd ~/ros2_ws && colcon build --packages-select follower_robot
 source install/setup.bash
```

---

### 9. Running the Follower Robot

```bash
 cd ~/ros2_ws && colcon build --packages-select follower_robot && source install/setup.bash && ros2 run follower_robot follower_node
```

The follower automatically subscribes to the leader's `/odom` topic and replicates the movement.

---

### 10. Independent Motor Test via ROS 2 (Pre-Integration)

**Why this step:** Before integrating both robots, we first verify the follower robot's motors work correctly by sending ROS 2 commands directly from the terminal. This tests the complete pipeline: ROS 2 → Pi → Serial → Arduino → Motors — without involving the leader robot at all.

**Files Used:**

| File | Location | Purpose |
|---|---|---|
| `motor_test.ino` | [`follower/arduino/motor_test.ino`](follower/arduino/motor_test.ino) | Uploaded to Arduino — receives serial commands, drives motors |
| `motor_test.py` | [`follower/motor_test.py`](follower/motor_test.py) | Runs on Pi — receives ROS 2 commands, sends to Arduino via serial |

**Step 1 — Upload Arduino code (on laptop):**

1. Connect Arduino to laptop via USB
2. Open Arduino IDE → paste code from [`follower/arduino/serial_test.ino`](follower/arduino/serial_test.ino) → Upload
3. Wait for "Done uploading"
4. Disconnect from laptop → connect Arduino to follower Pi USB port

**Step 2 — Terminal 1 (Follower Pi):**

```bash
ssh pi@follower-robot.local
```

```bash
ls /dev/ttyUSB*
```

Note which port Arduino is on (USB0 or USB1) and update `ros2_motor_test.py` if needed.

```bash
sudo chmod 666 /dev/ttyUSB0
```

```bash
python3 ~/ros2_ws/src/follower_robot/follower_robot/ros2_motor_test.py
```

Wait for:
```
Arduino connected!
Ready! Waiting for ROS2 commands...
```

**Step 3 — Terminal 2 — Method A: Manual ROS 2 commands:**

```bash
ssh pi@follower-robot.local
```

Forward:
```bash
ros2 topic pub --once /follower/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

Backward:
```bash
ros2 topic pub --once /follower/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: -0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

Left:
```bash
ros2 topic pub --once /follower/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.5}}"
```

Right:
```bash
ros2 topic pub --once /follower/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: -0.5}}"
```

Stop:
```bash
ros2 topic pub --once /follower/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

**Step 3 — Terminal 2 — Method B: Keyboard control using teleop:**

Install teleop (one time only):
```bash
sudo apt install ros-humble-teleop-twist-keyboard -y
source /opt/ros/humble/setup.bash
```

Run keyboard controller remapped to follower:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r /cmd_vel:=/follower/cmd_vel
```

| Key | Action |
|---|---|
| `i` | Forward |
| `,` | Backward |
| `j` | Turn Left |
| `l` | Turn Right |
| `k` | STOP |
| `Ctrl+C` | Quit |

**Expected Output:**

Terminal 1 prints:
```
Sending: FORWARD
Sending: STOP
Sending: BACKWARD
```
Motors move accordingly ✅

**Troubleshooting:**

| Problem | Cause | Fix |
|---|---|---|
| Arduino not found! | Wrong USB port | Change `/dev/ttyUSB0` to `/dev/ttyUSB1` in `ros2_motor_test.py` |
| Permission denied | No USB access | Run `sudo chmod 666 /dev/ttyUSB0` |
| Input/output error | USB connection dropped | Unplug and replug Arduino, run chmod again |
| Sending: FORWARD but no movement | Power issue | Check 12V adapter is ON and GND is shared between Arduino and L298N |
| Robot slants to one side | Motor speed imbalance | Adjust ENA/ENB values in Arduino code |

---

## 📡 ROS 2 Topics

| Topic | Message Type | Publisher | Subscriber | Purpose |
|---|---|---|---|---|
| `/cmd_vel` | geometry_msgs/Twist | leader_node | — | Leader movement velocity commands |
| `/odom` | nav_msgs/Odometry | leader_node | follower_node | Leader position and orientation |
| `/follower/cmd_vel` | geometry_msgs/Twist | follower_node | — | Follower movement commands |

---

## 📁 Code Structure

```
multi-robot-communication/
├── README.md
├── leader/
│   ├── leader_node.py          ← ROS 2 node for leader robot (keyboard control + odometry)
│   └── arduino/
│       └── motor_control.ino   ← Arduino code for leader motor control + encoder reading
└── follower/
    ├── follower_node.py        ← ROS 2 node for follower robot (subscribes to /odom)
    ├── motor_test.py      ← Test script for verifying motors via ROS 2 commands
    └── arduino/
        ├── follower_motor.ino  ← Arduino code for follower motor control
        └── motor_test.ino     ← Arduino test code for independent motor testing
```

Each file is linked directly from the setup steps above for easy navigation.

---

## 📅 Current Progress

| Component | Status |
|---|---|
| Leader Pi — Ubuntu 22.04 | ✅ Done |
| Leader Pi — ROS 2 Humble | ✅ Done |
| Leader Pi — SSH & Hostname | ✅ Done |
| Leader Robot — Arduino Motor Code | ✅ Done |
| Leader Robot — Forward/Backward/Turn | ✅ Done |
| Leader Robot — Odometry Publishing | ✅ Done |
| Follower Pi — Ubuntu 22.04 | ✅ Done |
| Follower Pi — ROS 2 Humble | ✅ Done |
| Follower Pi — SSH & Hostname | ✅ Done |
| Follower Robot — Hardware Wiring | ✅ Done |
| Follower Robot — Arduino Motor Code | ✅ Done |
| Follower Robot — Movement | ✅ Done |
| Leader–Follower Communication | ✅ Done |

---

## 🙏 Acknowledgements

**Internship Supervisor:** Pulkit Garg <br>
**Organization:** Technical Career Education

**Institution:** Yenepoya Institute of Arts, Science, Commerce and Management<br>
**Programme:** BCA — Artificial Intelligence, Machine Learning, Robotics and IoT

---

## 👥 Team

| Name | Register No |
|---|---|
| Nafeesath Saadha | 23BCARI118 |
| Shibeen Abid V | 23BCARI148 |

---