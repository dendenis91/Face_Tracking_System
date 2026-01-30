🎯 Portal-Themed Automated Turret System
An intelligent, real-time face-tracking turret inspired by the Portal universe. 
This project uses Computer Vision (OpenCV) to detect targets and a PID Controller to drive a dual-axis (Pan/Tilt) 
servo mechanism with high precision.
🚀 Features
Real-time Face Detection: Utilizes OpenCV and cvzone for high-speed human face tracking.
Laser Point Detection: Specifically tracks the laser's position in the HSV color space to calculate real-time error.
PID Control Logic: Custom Proportional-Integral-Derivative algorithm for smooth, non-oscillatory movement.
Dynamic UI: Includes an interactive calibration window with trackbars for real-time PID tuning.
Immersive Audio: Integrated pygame sound engine playing iconic Portal turret voice lines and sound effects.
Smart Sleep Mode: Automatic inactivity detection that parks the servos and powers down peripherals to save energy.
Flicker Effect: Non-blocking LED "muzzle flash" simulation using millis() timing.
🛠️ Tech Stack
Software
Python 3.x: Main processing engine.
OpenCV: Computer vision and image processing.
Pygame: Audio management.
Arduino C++: Hardware execution and servo control.
UART (Serial): High-speed (115200 baud) communication protocol.
Hardware
Arduino Uno 
SG90/MG90S Servos (Pan/Tilt)
Red Dot Laser Module
Feedback LEDs (Green for Search, Red for Lock/Fire)
📐 The PID Algorithm
The system calculates the error ($E$) between the Target Center ($T$) and the Laser Position ($L$):
$$Error = T_{pos} - L_{pos}$$
The PID controller then adjusts the current servo position (curX, curY) using:
Kp (Proportional): Immediate reaction to error.
Ki (Integral): Corrects long-term steady-state error.
Kd (Derivative): Predicts future error to dampen oscillations.
📂 Project StructurePlaintext
├──main.py                 # Main Python script (OpenCV, PID, UI)
├── turret_firmware.ino      # Arduino C++ code (Serial parsing, Servos)
├── portal sounds/          # MP3 assets for voice lines
└── README.md
🔧 Installation & Setup
Clone the Repository:
Bashgit clone https://github.com/yourusername/portal-turret.git
Install Python Dependencies:
Bashpip install opencv-python cvzone numpy pyserial pygame
Flash the Arduino:
Open turret_firmware.ino in Arduino IDE or VSCode/PlatformIO.
Upload the code to your Arduino.Run the System:Bashpython main.py
🎮 Controls
'a': Switch to AUTO Mode (Face tracking).
'm': Switch to MANUAL Mode (Trackbar control).
'q': Quit application.📜 LicenseThis project is for educational and hobbyist purposes. 
