import cv2
import RPi.GPIO as GPIO
import serial
from datetime import datetime
import time
import xlwt
from xlwt import Workbook
import lcddriver
import struct
import concurrent.futures
import numpy as np


from camera_position2 import find_position
from ultrasonic import find_dist_ult
from camera_distance2 import find_dist_cam
from fuzzy_RCAS import fuzzy_RCAS
from fuzzy_fusion import fuzzy_fusion

# Defining pins
pin_ult1 = 13
pin_ult2 = 19
pin_switch = 5
pin_relay = 6

# setting up GPIO
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_switch, GPIO.IN)
GPIO.setup(pin_relay, GPIO.OUT)

# init Arduino Serial COM
arduino_serial = serial.Serial('/dev/ttyACM0', 9600)


# init fuzzy logic
RCAS = fuzzy_RCAS()
fusion = fuzzy_fusion()
inSpeed = 200


def find_fusion(dist_ult, dist_cam, offset_center):
    if dist_cam != None:
        if dist_ult < 50:
            dist_fusion = dist_ult
        elif dist_cam >= 350:
            dist_fusion = dist_cam
        else:
            fusion.input['offset_center'] = offset_center
            fusion.input['dist_cam'] = dist_cam
            fusion.compute()
            ult_weight = fusion.output['ult_weight']
            cam_weight = 1 - ult_weight
            dist_fusion = dist_ult*ult_weight + dist_cam*cam_weight
    else:
        dist_fusion = dist_ult

    return dist_fusion


def move_car(steer, speed, position, dist_fusion):
    arduino_serial.write(struct.pack('>BBBB', int(steer+30), int((speed+100)/2), int(position+100), int(dist_fusion/4)))


def do_RCAS(distance, speed_dif, position):
    RCAS.input['distance'] = distance
    RCAS.input['speed_dif'] = speed_dif
    RCAS.input['position'] = position
    RCAS.compute()
    steer = RCAS.output['steer']
    brake = RCAS.output['brake']
    return steer, brake


def save_data(inSpeed, dist_cam_data, dist_ult_data, dist_fusion_data, speed_dif_data, position_data, steer_data, outSpeed_data, error_log_data):
    wb = Workbook()
    sheet1 = wb.add_sheet('Sheet 1')
    sheet1.write(0, 0, 'dist_cam')
    sheet1.write(0, 1, 'dist_ult')
    sheet1.write(0, 2, 'dist_fusion')
    sheet1.write(0, 3, 'speed_dif')
    sheet1.write(0, 4, 'position')
    sheet1.write(0, 5, 'steer')
    sheet1.write(0, 6, 'outSpeed')
    sheet1.write(0, 7, 'error_log')

    for i in range(len(dist_cam_data)):
        sheet1.write(i+1, 0, dist_cam_data[i])
        sheet1.write(i+1, 1, dist_ult_data[i])
        sheet1.write(i+1, 2, dist_fusion_data[i])
        sheet1.write(i+1, 3, speed_dif_data[i])
        sheet1.write(i+1, 4, position_data[i])
        sheet1.write(i+1, 5, steer_data[i])
        sheet1.write(i+1, 6, outSpeed_data[i])
        sheet1.write(i+1, 7, error_log_data[i])
    wb.save('./data/' + str(inSpeed) +'--' + str(datetime.now()) + '.xls')


dist_cam_data = []
dist_ult_data = []
dist_fusion_data = []
speed_dif_data = []
position_data = []
steer_data = []
outSpeed_data = []
error_log_data = []

t_1 = 0
dist_fusion_1 = 0


# SHOWING THE IMAGE RESULT. WARNING: IT CAN MAKE THE SISTEM SLOWER DUE TO I/O OPERATION
show_result = True
inSpeed = 230 # mode kecepatan rendah = 150, mode kecepatan tinggi = 230
error_counter = 0
error_limit = 5
stop_when_error = True
dist_cam = dist_ult = dist_fusion = speed_dif = position = steer = outSpeed = error_log = 0
while 1:
    try:
        # default images to display is black
        image_dist = image_position = np.zeros((480, 640, 3), np.uint8)

        # error limit checking
        if stop_when_error == True and error_counter >= error_limit:
            print('program exited due to error')
            break

        # timer
        t = time.time()
        start = t

        # storing data to list
        print(error_log)
        dist_cam_data.append(dist_cam)
        dist_ult_data.append(dist_ult)
        dist_fusion_data.append(dist_fusion)
        speed_dif_data.append(speed_dif)
        position_data.append(position)
        steer_data.append(steer)
        outSpeed_data.append(outSpeed)
        error_log_data.append(error_log)
 
        # sensor reading
        with concurrent.futures.ThreadPoolExecutor() as executor:
            f1 = executor.submit(find_dist_ult)
            f2 = executor.submit(find_dist_cam, show_result)
            dist_ult = f1.result()
            dist_cam, offset_center, image_dist, image = f2.result()

        # offset
        dist_cam = dist_cam - 20

        # fusion
        dist_fusion = find_fusion(dist_ult, dist_cam, offset_center)

        # error detection and logging
        if dist_fusion > 1000:
            error_counter += 1
            error_log = f'fusion is more than 1000 cm-{error_counter}'

        else:
            speed_dif = (dist_fusion-dist_fusion_1)/(t-t_1)
            if speed_dif > 0:
                speed_dif = 0

            if speed_dif < -150:
                error_counter += 1
                error_log = f'speed_dif is less than -150 cm/s-{error_counter}'

            else:
                # position
                position, image_position = find_position(image, show_result)

                # steer and speed
                steer, brake = do_RCAS(distance=dist_fusion, speed_dif=speed_dif, position=position)
                error_counter = 0
                error_log = '-'

                outSpeed = inSpeed - inSpeed*brake

                move_car(steer, outSpeed, position, dist_fusion)

        if show_result == True:
            result = cv2.addWeighted(image_dist, 1, image_position, 0.3, 0)
            cv2.imshow('result', result)

        if GPIO.input(pin_switch) == 1:
            GPIO.output(pin_relay, 0)
        else:
            GPIO.output(pin_relay, 1)

        dist_fusion_1 = dist_fusion
        t_1 = t
        error_counter = 0
        print(
            f'distance: {dist_fusion}, position: {position}, steer: {steer}, outSpeed: {outSpeed}')
        # print(f'cycle took {time.time()-start} seconds')
        if cv2.waitKey(1) == ord('q'):
            move_car(0, 0, position, dist_fusion)
            GPIO.output(pin_relay, 1)
            break
    except Exception as e:
        print(e)

move_car(0, 0, position, dist_fusion)
print('Saving data..')
save_data(inSpeed, dist_cam_data, dist_ult_data, dist_fusion_data,
          speed_dif_data, position_data, steer_data, outSpeed_data, error_log_data)
print('Done. Thank you!')
