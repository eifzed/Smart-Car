import time
import cv2
import imutils
import numpy as np

#raad a previously tuned hsv color range from a text
with open('distance.txt', 'r') as f:
    color_range = f.read().split(',')
color_range = [ int(x) for x in color_range ]

#camera settings
with open('camera_settings.txt', 'r') as f:
    camera_settings = f.read().split(',')
camera_settings = [ int(x) for x in camera_settings ]

image_w = camera_settings[0]
image_h = camera_settings[1]

# from picamera.array import PiRGBArray
# from picamera import PiCamera
# camera = PiCamera()
# camera.resolution = (image_w, image_h)
# camera.framerate = camera_settings[2]
# camera.saturation = camera_settings[3]
# # camera.vflip = True
# # camera.hflip = True
# rawCapture = PiRGBArray(camera, size=(image_w, image_h))
# time.sleep(1)

def take_picture():
    camera.capture(rawCapture, format="bgr", use_video_port=True)
    image = rawCapture.array
    rawCapture.truncate(0)
    return image




def find_mask(image):
    blur = cv2.GaussianBlur(image, (5, 5), 1)
    cv2.imshow('blur', blur)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    lower_color = np.array(color_range[:3])
    upper_color = np.array(color_range[3:])
    mask =  cv2.inRange(hsv, lower_color, upper_color)

    kernel = np.ones((5, 5), np.uint8)
    erode = cv2.erode(mask, kernel)
    dilation = cv2.dilate(erode, kernel, iterations = 1)
    return dilation


def calculate_real_distance(area):
    return 11342*(area**-0.46)


def find_dist_cam(show_result):
    # image = take_picture()
    image = cv2.imread('./images/distance.jpg')
    mask = find_mask(image)
    cv2.imshow('mask', mask)
    contours = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    contours = imutils.grab_contours(contours)


    global distance_image
    distance_image = None
    print(type(contours), contours)
    if len(contours) > 0:
        contour = max(contours, key = cv2.contourArea)
        approx = cv2.approxPolyDP(contour, 0.03*cv2.arcLength(contour, True), True)
        marker = cv2.minAreaRect(approx)

        # find distance from center of object to center of image
        offset_center = ((marker[0][0]-image_w/2)**2 + (marker[0][1]-image_h/2)**2)**0.5
        # object is a square, take the longest side in case one of the side is not captured
        side = max(marker[1][0], marker[1][1])
        area = side**2
        # print(area)
        # print(area, offset_center)

        # convert pixel area to real distance using power regression
        dist_cam = calculate_real_distance(area)

        
        if show_result == True:
            cv2.drawContours(image, [approx], 0, (255, 0, 0), 5)
            cv2.imshow('contour', image)
            box = cv2.cv.BoxPoints(marker) if imutils.is_cv2() else cv2.boxPoints(marker)
            box = np.int0(box)
            cv2.drawContours(image, [box], -1, (0, 0, 255), 5)
            cv2.imshow('contour2', image)
            distance_image = cv2.putText(image, str(round(dist_cam, 1))+'CM',(image.shape[1] - 300, image.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 255, 0), 3)
            # cv2.imshow('mask', mask)
            # cv2.imshow('image', image)
    else:
        dist_cam = None
        offset_center = None
    return dist_cam, offset_center, distance_image, image



if __name__ == "__main__":
    while 1:
        dist_cam, offset_center, distance_image, image = find_dist_cam(True)
        cv2.imshow('dist_image', distance_image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

