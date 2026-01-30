# 🎯 Portal-Themed Automated Turret System

An intelligent, real-time **face-tracking turret** inspired by the *Portal* universe.

This project uses **Computer Vision (OpenCV)** to detect targets and a **PID Controller** to drive a dual-axis *(Pan/Tilt)* servo mechanism with high precision.

---

## 🚀 Features

- **Real-time Face Detection** — Utilizes OpenCV and `cvzone` for high-speed human face tracking.
- **Laser Point Detection** — Tracks the laser position in the HSV color space to calculate real-time error.
- **PID Control Logic** — Custom Proportional–Integral–Derivative algorithm for smooth, non-oscillatory movement.
- **Dynamic UI** — Interactive calibration window with trackbars for real-time PID tuning.
- **Immersive Audio** — Integrated `pygame` sound engine playing iconic Portal turret voice lines.
- **Smart Sleep Mode** — Automatic inactivity detection that parks the servos and powers down peripherals.
- **Flicker Effect** — Non-blocking LED “muzzle flash” simulation using `millis()` timing.

---

## 🔌 Hardware Connections (Pinout)

To build this system, connect your components to the Arduino Uno as follows:

| Component | Arduino Pin | Description |
| :--- | :---: | :--- |
| **Servo X (Horizontal)** | **D9** | Controls left/right rotation |
| **Servo Y (Vertical)** | **D10** | Controls up/down rotation |
| **Laser Module** | **D6** | Targeted red dot laser |
| **Red LED** | **D4** | "Target Locked" / Firing flicker |
| **Green LED** | **D5** | "Searching" / Idle indicator |
| **GND** | **GND** | Common Ground for all components |
| **VCC (5V)** | **5V** | Power for Servos, Laser, and LEDs |

> [!NOTE]  
> If using high-torque servos, it is recommended to use an external 5V-6V power supply to avoid drawing too much current from the Arduino.

---

## 🛠️ Tech Stack

### Software
- **Python 3.x** — Main processing engine  
- **OpenCV / cvzone** — Computer vision utilities  
- **Pygame** — Audio management  
- **Arduino C++** — Hardware execution  
- **UART (Serial)** — High-speed (115200 baud) communication  

### Hardware
- **Arduino Uno**
- **SG90 / MG90S Servos**
- **Red Dot Laser Module**
- **Feedback LEDs**

---

## 📐 The PID Algorithm

The system calculates the error **E** between the **Target Center (T)** and the **Laser Position (L)**:

$$Error = T_{pos} - L_{pos}$$

The PID controller processes this error to create smooth motion:
1. **P (Proportional):** Adjusts speed based on how far the laser is from the face.
2. **I (Integral):** Corrects small offsets that persist over time.
3. **D (Derivative):** Acts as a brake to prevent the turret from "shaking" or overshooting the target.

---

## 📂 Project Structure

```plaintext
├── main.py                # Main Python script (Logic, CV, PID)
├── turret_firmware.ino    # Arduino code (Serial parsing & Servos)
├── portal sounds/         # Folder containing .mp3 assets
└── README.md              # Documentation
