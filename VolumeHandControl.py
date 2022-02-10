
import cv2
import time
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import HandTrackingModule as htm
import math

import sys
import keyboard

################# Parámetros #################
pTime = 0
cap = cv2.VideoCapture(1)
detector = htm.handDetector(detectionCon=0.7)
##############################################

############ Módulo para el uso de Pycaw #################################
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
# volume.SetMasterVolumeLevel(-20.0, None)
minVol = volRange[0]
maxVol = volRange[1]
##########################################################################

#################### Programación de la interfaz de Imagen y sus funcionalidades  ########################
while True:
    try:
        success, img = cap.read()
        # Tenemos que encontrar la mano, por lo que vamos a proceder a ello
        img = detector.findHands(img)
        # Buscamos la posicion de la mano. Si ponemos draw = false --> no dibuja el cuadrado que limita la mano
        lmList = detector.findPosition(img, draw=False)
        # Visualizamos el landmark de la mano en la imagen, es decir, los 21 puntos de la mano:
        # print(lmList)

        # Pero como queremos dos puntos en conctreto para el gesto del pellizco, que son el 4 y el 8, según la documentación
        # de mediapipe, pues mostramos esos valores
        if len(lmList) != 0:
            print(lmList[4], lmList[8])

            # Vamos a dibujar la representación de los puntos en la mano:
            # x coge de lmlist la coordenada x, e y coge de lmlist de la coordenada y del punto 4 y 8 de los dedos
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]

            # Centroide de la linea de los dedos de distancia
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            # Aquí dibujamos los círculos:
            # Le pasamos a ambos círculos, la posición de los dedos en la imagen
            cv2.circle(img, (x1, y1), 9, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 9, (255, 0, 255), cv2.FILLED)

            # Si queremos crear un slider que vea como hacemos la extensión del dedo:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

            # Esta variable, tomará la distancia entre los puntos
            length = math.hypot(x2 - x1, y2 - y1)
            print(length)

            # Rango de mano: 35-250
            # Rango del volumen: -65 - 0, siendo 0 el máximo y -65 el mínimo

            vol = np.interp(length, [35, 250], [minVol, maxVol])
            volume.SetMasterVolumeLevel(vol, None)

            if length < 35:
                cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)

        # Esto lo usamos para poder ver los frames por segundo que vamos teniendo en el frame de la imagen
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        # Ahora vamos a mostrarlo por pantalla
        # A donde queremos aplicarlo
        # Que queremos que aparezca
        # La posicion en la ventana
        # La fuente que queremos
        # La escala del texto
        # El color
        # Y la anchura del texto

        cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)

        cv2.imshow("Volume Hand Control - David Campero Mana", img)
        cv2.waitKey(1)

        if keyboard.is_pressed("Esc"):
            sys.exit(0)
    except:
        break
