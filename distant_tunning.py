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

    l_h = 130 # cv2.getTrackbarPos('lh', 'Trackbars') # 100
    l_s = 140 # cv2.getTrackbarPos('ls', 'Trackbars') # 140
    l_v = 60 # cv2.getTrackbarPos('lv', 'Trackbars') # 72
    u_h = 255 # cv2.getTrackbarPos('uh', 'Trackbars') # 210
    u_s = 255 # cv2.getTrackbarPos('us', 'Trackbars') # 225
    u_v = 255 # cv2.getTrackbarPos('uv', 'Trackbars') # 180 #

    lower_green = np.array([l_h, l_s, l_v])
    upper_green = np.array([u_h, u_s, u_v])
    mask =  cv2.inRange(hsv, lower_green, upper_green)
    mask_color = cv2.bitwise_and(image, image, mask=mask)
     

    kernel = np.ones((5, 5), np.uint8)
    erode = cv2.erode(mask, kernel)
    dilation = cv2.dilate(erode, kernel, iterations = 1)
    cv2.imshow('mask', mask_color)
    # cv2.imshow('erode', erode) 
    cv2.imshow('dilation', dilation) 

    return dilation

def calculate_real_distant(LENGTH_REAL, LENGTH_PX, f):
    return LENGTH_REAL*f/LENGTH_PX

def find_dist_cam(image):
    mask = find_mask(image.copy())
    contours = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    if len(contours)>0:
        contour = max(contours, key = cv2.contourArea)
        approx = cv2.approxPolyDP(contour, 0.03*cv2.arcLength(contour, True), True)
        marker = cv2.minAreaRect(approx)
        area = marker[1][0] * marker[1][1]

        cv2.drawContours(image, [approx], 0, (255, 0, 0), 2)
        # cv2.drawContours(image, [contour], 0, (0, 0, 255), 2)
        # distant = calculate_real_distant(LENGTH_REAL, area, f)

        # conversion = -3.304*(10**-4)*(distant**2) + 0.39999*distant + 28.371
        conversion = 645.626199 - 55.8438111*np.log(area)
        box = cv2.cv.BoxPoints(marker) if imutils.is_cv2() else cv2.boxPoints(marker)
        box = np.int0(box)
        cv2.drawContours(image, [box], -1, (0, 255, 0), 2)

        cv2.putText(image, str(round(area, 1)),(image.shape[1] - 300, image.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 255, 0), 3)
        
        cv2.imshow('final', image)
        return area
        # return distance, marker[1][0]
    

LENGTH_REAL = 312
DISTANCE_REAL = 50
LENGTH_PX = 54000
f = (LENGTH_PX*DISTANCE_REAL)/LENGTH_REAL

if __name__ == "__main__":
    # image1 = cv2.imread("./images/home80.jpg")
    # image2 = cv2.imread("./images/home80-left.jpg")
    # image3 = cv2.imread("./images/home80-right.jpg")
    # image4 = cv2.imread("./images/home200.jpg")
    # image5 = cv2.imread("./images/home200-left.jpg")
    # image6 = cv2.imread("./images/home200-right.jpg")
    # image7 = cv2.hconcat([image1, image2, image3])
    # image8 = cv2.hconcat([image4, image5, image6])
    # image9 = cv2.vconcat([image7, image8])
    image10 = cv2.imread("./images/tune1.jpg")
    image11 = cv2.imread("./images/tune2.jpg")
    image12 = cv2.hconcat([image10, image11])
    # cv2.imshow('vis', vis)

    image = image12
    while True:
        copy = image.copy()
        print(find_dist_cam(copy))

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

