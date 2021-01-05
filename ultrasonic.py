import RPi.GPIO as GPIO
import time

def measure_dist(pin_ult, maxTime=0.02):
    GPIO.setup(pin_ult, GPIO.OUT)
    GPIO.output(pin_ult, 1)  
    time.sleep(0.00001)
    GPIO.output(pin_ult, 0) 
    GPIO.setup(pin_ult, GPIO.IN)

    pulse_start = time.time()
    timeout = pulse_start + maxTime
    while GPIO.input(pin_ult)==0 and pulse_start < timeout:
        pulse_start = time.time()

    pulse_end = time.time()
    timeout = pulse_end + maxTime

    while GPIO.input(pin_ult) == 1 and pulse_end < timeout:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    return round(pulse_duration * 17000, 2)


def find_dist_ult(pin_ult1=13, pin_ult2=19):
    ult_dist1 = measure_dist(pin_ult1)
    ult_dist2 = measure_dist(pin_ult2)

    if ult_dist1 < ult_dist2:
        distance = ult_dist1
    else:
        distance = ult_dist2
    return distance

def find_dist_ult_sd(pin_ult3=23):
    GPIO.setup(24 , GPIO.OUT)
    GPIO.output(24, True)
    distance_sd = measure_dist(pin_ult3)
    return distance_sd

if __name__ == "__main__":
    import RPi.GPIO as GPIO
    import time
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    while 1:
        distance = find_dist_ult()
        distance_sd = find_dist_ult_sd()
        print(distance)
        print(distance_sd)
        time.sleep(.3)