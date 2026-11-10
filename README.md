# 🎥 Face-Tracking Gimbal (2-axis, PID)

> A Raspberry Pi pan–tilt camera that follows a face, built as a first step towards a gimbal. The plant was identified from data and a digital PID was tuned in MATLAB.

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?logo=opencv&logoColor=white)
![MATLAB](https://img.shields.io/badge/MATLAB-System%20ID-E16737)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-A22846?logo=raspberrypi&logoColor=white)

## Overview

The camera detects a face, measures how far it is from the center of the image, and two servos (pan and tilt) move the camera to bring it back to the center. The work followed a classic control workflow:

**collect open-loop data → identify the transfer function → tune PID → close the loop → evaluate**

## Hardware

- Raspberry Pi + Pi Camera
- 2 × MG995 servos
- PCA9685 PWM driver (I²C)
- 5 V / 3 A power supply

**Block diagram (PFD)**

![Block diagram](https://user-images.githubusercontent.com/87034576/209713029-9d8b94e1-9483-4eae-9535-b4dcc12f9100.png)

**Wiring: servos – PCA9685 – Raspberry Pi**

![Wiring](https://user-images.githubusercontent.com/87034576/209713126-2144707d-fb73-46bb-9f54-b8d96da3811f.png)

## 1. System identification

`getting_data.py` moves the pan servo in open loop while recording, every 0.25 s, the setpoint, the control signal and the measured face position. The data is exported to Excel and loaded in MATLAB (`tuning.m`, `iddata`) to estimate the transfer function, then tuned with the **PID Tuner**.

![Identification](https://user-images.githubusercontent.com/87034576/209715537-4dc8b9ca-f926-4ed6-a913-8bc8c8144db0.png)
![PID tuning](https://user-images.githubusercontent.com/87034576/209715562-74ccdede-7343-4e85-97e8-179cca329b50.png)

## 2. Closed-loop control

`pid_control_xy.py` runs a **discrete PID in incremental (velocity) form** for each axis:

```
u[k] = u[k-1] + q0·e[k] + q1·e[k-1] + q2·e[k-2]
```

with `Ts = 0.25 s`, `Kp = 0.122`, `Ti = 0.3`, `Td = 0` (so in practice a PI controller), output saturated to 0–100 % and mapped to the PCA9685 pulse range. Faces are detected with an OpenCV Haar cascade and the controller runs on a timer thread.

## Results and lessons learned

The response was **not stable enough for a gimbal**: the camera oscillated around the face instead of settling. Likely causes:

- **Slow and delayed measurement** – the loop runs at only 4 Hz, and face detection adds latency, which reduces the phase margin.
- **Noisy measurement** – the face center from the Haar detector jumps between frames.
- **Model reused for both axes** – the model was identified on the pan axis only, but the same gains are used for tilt.
- **Servo deadband and backlash** in the MG995.

## Next version

- [ ] Faster loop and a better detector (e.g. MediaPipe face detection).
- [ ] Kalman filter on the face position to reduce noise and compensate the delay.
- [ ] State-space model per axis and an **LQR** (or LQG with the Kalman filter) controller.
- [ ] Compare PID vs. LQR with the same metrics: settling time, overshoot and steady-state error.

## Run

```bash
pip install opencv-python Adafruit_PCA9685 pandas openpyxl
python getting_data.py     # collect open-loop data
python pid_control_xy.py   # closed-loop tracking (Esc to quit)
```
