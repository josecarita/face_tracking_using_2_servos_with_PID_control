# -*- coding: utf-8 -*-
"""
Created on Thu Jul 22 23:21:45 2021

@author: jose_
"""
import cv2
import time
import numpy as np
import Adafruit_PCA9685
import pandas as pd
import threading


pwm = Adafruit_PCA9685.PCA9685()

servo_min = 100  # (105) Longitud de pulso mínima de 4096
servo_max = 530  # Longitud de pulso máxima de 4096

# Función para ajustar los parámetros del servomotor.
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us por segundo
    pulse_length //= 50       # 50 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits de resolución
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)

# Ajusta la frecuencia a 50Hz.
pwm.set_pwm_freq(50)

pwm.set_pwm(0, 0, 315) #punto medio x
pwm.set_pwm(1, 0, 208) #punto medio y (para el este proceso)

#Opencv
rostroCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)

cap.set(3,480)
cap.set(4,320)

_, img = cap.read()
rows,cols, _= img.shape

x_medio = 50.0
center_x = 50.0
y_medio = int(rows/2)
center_y = int(rows/2)
positionx = 315
positiony = 208

#Declaración de variables para almacenar los datos del proceso
datasp = []
datacv = []
datapv = []

temporal = 0
xmedio = 0

#Interrupción periódica para obtención de datos y cambio de estado de la variable del proceso
def SampleTime():
    global datasp
    global datapv
    global datacv
    position_x = 0.2326*positionx - 23.256
    print(position_x) 
    pwm.set_pwm(0, 0, int(positionx))
    datasp += [center_x]
    datacv += [position_x]
    datapv += [x_medio]
    
    threading.Timer(0.25,SampleTime).start()
    
threading.Timer(0.25,SampleTime).start()

#Tiempo de espera antes de toma de datos
time.sleep(5)

#Proceso principal
while True:
    ret, img=cap.read()
    
    img=cv2.flip(img,-1) #invertir imagen

    grises = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

    rostros = rostroCascade.detectMultiScale(
    grises,
    scaleFactor = 1.2,
    minNeighbors = 10,
    minSize= (30,30),
    flags = cv2.CASCADE_SCALE_IMAGE
    )
    
    for (x, y, w, h) in rostros:
        #cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        xmedio = int((x + x + w)/2)  #max480
        y_medio = int((y + y + h)/2)  #max320
    
        cv2.line(img,(xmedio,0),(xmedio,320),(0,255,0),2)
        cv2.line(img,(0,y_medio),(480,y_medio),(0,255,0),2)
            
        break
    
    cv2.imshow('video', img)
    k=cv2.waitKey(10) 

    if k==27:
        break
    
    # Mueve el servomotor
    x_medio =xmedio/4.8
    if x_medio < center_x and positionx < 530:
        positionx += 1
    elif x_medio > center_x and positionx > 100:
        positionx -= 1
        
    if y_medio < center_y:
        positiony -= 1
    elif y_medio > center_y:
        positiony += 1

#Una vez terminado el proceso, se le asigna un nombre a cada array de datos como columna
df1 = pd.DataFrame(datasp, columns = ['datos sp'])
df2 = pd.DataFrame(datacv, columns = ['datos cv'])
df3 = pd.DataFrame(datapv, columns = ['datos pv'])


#Cada array de datos se exporta en un archivo excel
df1.to_excel('sp.xlsx')
df2.to_excel('cv.xlsx')
df3.to_excel('pv.xlsx')

cap.release()
cv2.destroyAllWindows()


