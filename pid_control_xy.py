# -*- coding: utf-8 -*-
"""
Created on Sun Jul 18 21:27:50 2021

@author: jose_
"""

import threading
import time
import cv2
import numpy as np
import Adafruit_PCA9685


Ts = 0.25 #periodo de muestreo en segundos

#parámetros eje x
Spx = 50.0  #setpoint
ux = 0.0 #acción de control
ux_1 = 50.0 #establecer en su proporción al valor inicial del servo
ex = 0.0 #error en el tiempo
ex_1 = 0.0
ex_2 = 0.0
#k = 50 #parametros del modelo del sistema
#tau = 0
#theta = 10+Ts/2

#parametros eje y
Spy = 50.0  #setpoint
uy = 0.0 #accion de control
uy_1 = 75.0 #establecer en su proporción al valor inicial del servo
ey = 0.0 #error en el tiempo
ey_1 = 0.0
ey_2 = 0.0

x_medio = 0
y_medio = 0

#Setup para sintonia de la planta por Matlab
kp = 0.122
ti = 0.3#0.04
td = 0.0

#Cálculo de control PID digital
q0=kp*(1+Ts/(2.0*ti)+td/Ts)
q1=-kp*(1-Ts/(2.0*ti)+(2.0*td)/Ts)
q2=(kp*td)/Ts

#Llama a la librería del módulo
pwm = Adafruit_PCA9685.PCA9685()

servo_min = 100  # (105) Longitud de pulso mínima de 4096
servo_max = 530  # Longitud de pulso máxima de 4096

# Función para setear parámetros del servo.
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us por segundo
    pulse_length //= 50       # 50 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits de resolución
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)

# Ajusta la frecuencia a 50hz
pwm.set_pwm_freq(50)

pwm.set_pwm(0, 0, 315) #punto medio x
pwm.set_pwm(1, 0, 208) #punto_medio y (para la aplicación)

#OpenCV
rostroCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)

cap.set(3,480)
cap.set(4,320)

#Función PID
def PID():
    global ux_1
    global ex_1
    global ex_2
    
    global uy_1
    global ey_1
    global ey_2
    
    ex = (Spx-Pvx)
    ey = (Spy-Pvy)
    #control PID
    ux = ux_1 + q0*ex + q1*ex_1 + q2*ex_2
    uy = uy_1 + q0*ey + q1*ey_1 + q2*ey_2

    if ux >= 100.0:  #Saturo la acción de control 'uT' en un tope máximo y mínimo
        ux = 100.0
    
    if ux <= 0.0 or Spx==0:
        ux = 0.0
        
    if uy >= 100.0:  #Saturo la acción de control 'uT' en un tope máximo y mínimo
        uy = 100.0
    
    if uy <= 0.0 or Spy==0:
        uy = 0.0
     
    #Retorno a los valores reales
    ex_2=ex_1
    ex_1=ex
    ux_1=ux
    
    #Retorno a los valores reales
    ey_2=ey_1
    ey_1=ey
    uy_1=uy
    
    #pasa del rango de 0 a 100 al rango de 100 a 530
    position_x = int(4.3*ux + 100)
    position_y = int(530 - 4.3*uy)
    
    #Ajusta el servo a la posición requerida
    pwm.set_pwm(0, 0, position_x)
    pwm.set_pwm(1, 0, position_y)
    print(position_y)

temporal = 0

#Interrupción para ejecutar el control
def SampleTime():
    PID()
    threading.Timer(Ts,SampleTime).start()
    
#Proceso principal
def proceso():
    ret, img=cap.read()
    img=cv2.flip(img,-1) #Invertir imagen
    grises = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    rostros = rostroCascade.detectMultiScale(
    grises,
    scaleFactor = 1.1, #Parámetros para el reconocimiento facial
    minNeighbors = 10,
    minSize= (30,30),
    flags = cv2.CASCADE_SCALE_IMAGE
    )
    
    for (x, y, w, h) in rostros:
        #cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)    
        global x_medio
        global y_medio
        x_medio = int((x + x + w)/2)  #max480
        y_medio = int((y + y + h)/2)  #max320
        #trazo de líneas
        cv2.line(img,(x_medio,0),(x_medio,320),(0,255,0),2)
        cv2.line(img,(0,y_medio),(480,y_medio),(0,255,0),2)
        #uso de variable para iniciar por primera vez el Timer
        global temporal
        if temporal == 0:
            threading.Timer(Ts,SampleTime).start()
            temporal = 1
        break
    #Muestra lo que captura la cámara
    cv2.imshow('video', img)
    
#Programa principal   
while True:
    proceso()
    #Escala los valores al rango de 0 a 100
    Pvx=int(x_medio/4.8)#Pvx
    Pvy=int(y_medio/3.2)#Pvy
    #print("Pv1 ",Pv1)
    #Espera a que se presione 'Esc' para salir del bucle
    k=cv2.waitKey(10)
    if k==27:
        break

#Cierra la ventana y cancela o detiene el Timer          
cap.release()
cv2.destroyAllWindows()
threading.Timer(Ts,SampleTime).cancel()
threading.Timer(Ts,SampleTime).join()
    
        