import numpy as np
import time
import cv2
import imutils


def nothing(x):
    pass


cv2.namedWindow('Trackbars')
cv2.createTrackbar('lh', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('ls', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('lv', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('uh', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('us', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('uv', 'Trackbars', 0, 255, nothing)


def find_mask(image):
    dist_real = None
    dist_px = None
    blur = cv2.GaussianBlur(image, (7, 7), 1)
    img_copy = np.copy(blur)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    l_h = cv2.getTrackbarPos('lh', 'Trackbars')  # 100
    l_s = cv2.getTrackbarPos('ls', 'Trackbars')  # 140
    l_v = cv2.getTrackbarPos('lv', 'Trackbars')  # 72
    u_h = cv2.getTrackbarPos('uh', 'Trackbars')  # 210
    u_s = cv2.getTrackbarPos('us', 'Trackbars')  # 225
    u_v = cv2.getTrackbarPos('uv', 'Trackbars')  # 180 #

    lower_color = np.array([l_h, l_s, l_v])
    upper_color = np.array([u_h, u_s, u_v])
    mask = cv2.inRange(hsv, lower_color, upper_color)

    kernel = np.ones((3, 3), np.uint8)
    erode = cv2.erode(mask, kernel)
    dilation = cv2.dilate(erode, kernel, iterations=1)
    mask_color = cv2.bitwise_and(image, image, mask=dilation)
    cv2.imshow('mask', mask_color)

    return str(l_h) + ',' + str(l_s) + ',' + str(l_v) + ',' + str(u_h) + ',' + str(u_s) + ',' + str(u_v)


num_of_pics = 1
# mode name for detecting position is 'lane_lines', for distance measurement is 'distance'
mode = 'lane_lines'
images = []


if __name__ == "__main__":

    # camera settings
    # with open('camera_settings.txt', 'r') as f:
    #     camera_settings = f.read().split(',')
    # camera_settings = [int(x) for x in camera_settings]

    # from picamera.array import PiRGBArray
    # from picamera import PiCamera
    # camera = PiCamera()
    # camera.resolution = (camera_settings[0], camera_settings[1])
    # camera.framerate = camera_settings[2]
    # camera.saturation = camera_settings[3]
    # camera.brightness = 40
    # camera.vflip = True
    # camera.hflip = True

    # rawCapture = PiRGBArray(camera, size=(
        # camera_settings[0], camera_settings[1]))

    for i in range(num_of_pics):
        while 1:
            # camera.capture(rawCapture, format="bgr", use_video_port=True)
            # image = rawCapture.array
            image = cv2.imread('./images/lane_lines-1.jpg')
            cv2.putText(image, str(i), (image.shape[1] - 50, image.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 255, 0), 3)
            cv2.imshow('image', image)
            # rawCapture.truncate(0)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                images.append(image)
                cv2.imwrite(f'./images/{mode}-{i}.jpg', image)
                break

    image_concat = cv2.hconcat(images)

    while 1:
        image_copy = image_concat.copy()
        color_range = find_mask(image_copy)
        print(str(color_range))
        cv2.imshow('image_concat', image_concat)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            if input(f'would you like to save the data for {mode}? (y/n) ').lower() == 'y':
                with open(f'{mode}.txt', 'w') as f:
                    f.write(color_range)
                print('New data has been saved')
            else:
                print('New data was not saved')
            break
