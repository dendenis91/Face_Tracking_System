# 🎯 Portal-Themed Automated Turret System

An intelligent, real-time **face-tracking turret** inspired by the *Portal* universe.

This project uses **Computer Vision (OpenCV)** to detect targets and a **PID Controller** to drive a dual-axis *(Pan/Tilt)* servo mechanism with high precision.

---

## 🚀 Features

- **Real-time Face Detection**  
  Utilizes OpenCV and `cvzone` for high-speed human face tracking.

- **Laser Point Detection**  
  Tracks the laser position in the HSV color space to calculate real-time error.

- **PID Control Logic**  
  Custom Proportional–Integral–Derivative algorithm for smooth, non-oscillatory movement.

- **Dynamic UI**  
  Interactive calibration window with trackbars for real-time PID tuning.

- **Immersive Audio**  
  Integrated `pygame` sound engine playing iconic Portal turret voice lines and sound effects.

- **Smart Sleep Mode**  
  Automatic inactivity detection that parks the servos and powers down peripherals to save energy.

- **Flicker Effect**  
  Non-blocking LED “muzzle flash” simulation using `millis()` timing.

---

## 🛠️ Tech Stack

### Software
- **Python 3.x** — Main processing engine  
- **OpenCV** — Computer vision and image processing  
- **cvzone** — High-level CV utilities  
- **Pygame** — Audio management  
- **Arduino C++** — Hardware execution and servo control  
- **UART (Serial)** — High-speed (115200 baud) communication  

### Hardware
- **Arduino Uno**
- **SG90 / MG90S Servos** (Pan / Tilt)
- **Red Dot Laser Module**
- **Feedback LEDs**
  - Green: Search
  - Red: Lock / Fire

---

## 📐 The PID Algorithm

The system calculates the error **E** between the **Target Center (T)** and the **Laser Position (L)**:

```math
Error = T_{pos} - L_{pos}
