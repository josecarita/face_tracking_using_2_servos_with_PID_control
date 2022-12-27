# face_tracking_using_2_servos_with_PID_control

## Description
This project uses two servomotors to control the position of a camera that will be tracking faces detected in its visual field using
PID control for both of the servos.

## Materials
  - Raspberry Pi
  - Pi camera
  - 2 servos MG995
  - Driver PCA9685
  - Power supply 5V 3A
 
## Connection Diagram (PFD)
 ![image](https://user-images.githubusercontent.com/87034576/209713029-9d8b94e1-9483-4eae-9535-b4dcc12f9100.png)

## Connection between servo, PCA9685 module and Raspberry Pi
 ![image](https://user-images.githubusercontent.com/87034576/209713126-2144707d-fb73-46bb-9f54-b8d96da3811f.png)

## Libraries to be used
 - OpenCV
 - Adafruit_PCA9685
 - Threading
 - Pandas
 
 ## Getting data for the PID controller tuning
 The `getting_data.py` file is a program that will let the process, in open loop mode, act
 and get by a defined time the data of the position of the servomotor. All this data will be 
 write in an excel file to then pass this data to `Matlab` and with this software get the function
 transfer of the process, this will be done with the `tuning.m` script and with the `PID tuning` tool of Matlab.
 
 ![image](https://user-images.githubusercontent.com/87034576/209715537-4dc8b9ca-f926-4ed6-a913-8bc8c8144db0.png)
![image](https://user-images.githubusercontent.com/87034576/209715562-74ccdede-7343-4e85-97e8-179cca329b50.png)

 ## Main program
 Once having the parameters for the PID controller, just have to place them in the `kp`,
 `ti` and `td` variables in the main program `pid_control_xy.py`.
