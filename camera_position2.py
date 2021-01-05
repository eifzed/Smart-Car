import numpy as np
import cv2
import time



with open('wrap.txt', 'r') as f:
    points = f.read().split(',')
points = [ int(x) for x in points ]

with open('lane_lines.txt', 'r') as f:
    color_range = f.read().split(',')
color_range = [ int(x) for x in color_range ]

with open('camera_settings.txt', 'r') as f:
    camera_settings = f.read().split(',')
camera_settings = [ int(x) for x in camera_settings ]

image_w = camera_settings[0]
image_h = camera_settings[1]
nwindows = 10
window_height = np.int(image_h / nwindows)
margin = 75 # 100
minpix = 25 # 50
midpoint = np.int(image_w / 2)
image_size = (image_w, image_h)


def perspectiveWarp(inpImage):
    pts1 = np.float32([points[:2], points[2:4], points[4:6] , points[6:]])
    pts2 = np.float32([[0, 480], [0, 0], [640, 0], [640, 480]])


    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    minv = cv2.getPerspectiveTransform(pts2, pts1)
    
    result = cv2.warpPerspective(inpImage, matrix, image_size, flags=cv2.INTER_NEAREST)
    return result, minv

def filter_image(image):
    blur = cv2.GaussianBlur(image, (5, 5), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    lower_color = np.array(color_range[:3])
    upper_color = np.array(color_range[3:])
    mask = cv2.inRange(hsv, lower_color, upper_color)
    # cv2.imshow('mask', mask)
    return mask


def plotHistogram(inpImage):
    return np.sum(inpImage[inpImage.shape[0] // 2:, :], axis = 0)


def slide_window_search(binary_warped, histogram, show_result):
    plt.plot(histogram[:320])
    # Find the start of left and right lane lines using histogram info
    out_img = np.dstack((binary_warped, binary_warped, binary_warped)) * 255
    
    leftx_base = np.argmax(histogram[:midpoint])
    rightx_base = np.argmax(histogram[midpoint:]) + midpoint

    # using 15 window search
    
    nonzero = binary_warped.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])
    leftx_current = leftx_base
    rightx_current = rightx_base
    
    left_lane_inds = []
    right_lane_inds = []

    #### START - Loop to iterate through windows and search for lane lines #####
    for window in range(nwindows):
        win_y_low = binary_warped.shape[0] - (window + 1) * window_height
        win_y_high = binary_warped.shape[0] - window * window_height
        win_xleft_low = leftx_current - margin
        win_xleft_high = leftx_current + margin
        win_xright_low = rightx_current - margin
        win_xright_high = rightx_current + margin

        if show_result == True:
            cv2.rectangle(out_img, (win_xleft_low, win_y_low), (win_xleft_high, win_y_high), (0,255,0), 2)
            cv2.rectangle(out_img, (win_xright_low,win_y_low), (win_xright_high,win_y_high), (0,255,0), 2)
            cv2.imshow('rectangles', out_img)

        good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
        (nonzerox >= win_xleft_low) &  (nonzerox < win_xleft_high)).nonzero()[0]
        good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
        (nonzerox >= win_xright_low) &  (nonzerox < win_xright_high)).nonzero()[0]
        left_lane_inds.append(good_left_inds)
        right_lane_inds.append(good_right_inds)
        if len(good_left_inds) > minpix:
            leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
        if len(good_right_inds) > minpix:
            rightx_current = np.int(np.mean(nonzerox[good_right_inds]))
    #### END - Loop to iterate through windows and search for lane lines #######

    left_lane_inds = np.concatenate(left_lane_inds)
    right_lane_inds = np.concatenate(right_lane_inds)

    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds]
    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds]

    # Apply 2nd degree polynomial fit to fit curves
    left_fit = np.polyfit(lefty, leftx, 2)
    right_fit = np.polyfit(righty, rightx, 2)


    if show_result == True:
        ploty = np.linspace(0, binary_warped.shape[0]-1, binary_warped.shape[0])

        out_img[nonzeroy[left_lane_inds], nonzerox[left_lane_inds]] = [255, 0, 0]
        out_img[nonzeroy[right_lane_inds], nonzerox[right_lane_inds]] = [0, 0, 255]
        global im_out_img
        im_out_img = out_img
        # cv2.imshow('im_out_img',im_out_img)
#       cv2.imshow('im_out_img', im_out_img)
    # plt.imshow(out_img)
    # plt.plot(left_fitx,  ploty, color = 'yellow')
    # plt.plot(right_fitx, ploty, color = 'yellow')
    # plt.xlim(0, 1280)
    # plt.ylim(720, 0)

    return left_fit, right_fit


def general_search(binary_warped, left_fit, right_fit, show_result):
    nonzero = binary_warped.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])
    margin = 25
    left_lane_inds = ((nonzerox > (left_fit[0]*(nonzeroy**2) + left_fit[1]*nonzeroy +
    left_fit[2] - margin)) & (nonzerox < (left_fit[0]*(nonzeroy**2) +
    left_fit[1]*nonzeroy + left_fit[2] + margin)))

    right_lane_inds = ((nonzerox > (right_fit[0]*(nonzeroy**2) + right_fit[1]*nonzeroy +
    right_fit[2] - margin)) & (nonzerox < (right_fit[0]*(nonzeroy**2) +
    right_fit[1]*nonzeroy + right_fit[2] + margin)))

    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds]
    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds]
    left_fit = np.polyfit(lefty, leftx, 2)
    right_fit = np.polyfit(righty, rightx, 2)
    
    ploty = np.linspace(0, binary_warped.shape[0]-1, binary_warped.shape[0])
    left_fitx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
    right_fitx = right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]


    ## VISUALIZATION ###########################################################

    if show_result == True:
        out_img = np.dstack((binary_warped, binary_warped, binary_warped))*255
        window_img = np.zeros_like(out_img)
        out_img[nonzeroy[left_lane_inds], nonzerox[left_lane_inds]] = [255, 0, 0]
        out_img[nonzeroy[right_lane_inds], nonzerox[right_lane_inds]] = [0, 0, 255]

        left_line_window1 = np.array([np.transpose(np.vstack([left_fitx-margin, ploty]))])
        left_line_window2 = np.array([np.flipud(np.transpose(np.vstack([left_fitx+margin,
                                    ploty])))])
        left_line_pts = np.hstack((left_line_window1, left_line_window2))
        right_line_window1 = np.array([np.transpose(np.vstack([right_fitx-margin, ploty]))])
        right_line_window2 = np.array([np.flipud(np.transpose(np.vstack([right_fitx+margin, ploty])))])
        right_line_pts = np.hstack((right_line_window1, right_line_window2))

        cv2.fillPoly(window_img, np.int_([left_line_pts]), (0, 255, 0))
        cv2.fillPoly(window_img, np.int_([right_line_pts]), (0, 255, 0))
        result = cv2.addWeighted(out_img, 1, window_img, 0.3, 0)
        cv2.imshow('result',result)
        global im_pillpoly
        im_pillpoly = cv2.addWeighted(out_img, 1, window_img, 0.3, 0)
        cv2.imshow('im_pillpoly',im_pillpoly)


    # plt.imshow(result)
    # plt.plot(left_fitx,  ploty, color = 'yellow')
    # plt.plot(right_fitx, ploty, color = 'yellow')
    # plt.xlim(0, 1280)
    # plt.ylim(720, 0)

    ret = {}
    # ret['leftx'] = leftx
    # ret['rightx'] = rightx
    ret['left_fitx'] = left_fitx
    ret['right_fitx'] = right_fitx
    ret['ploty'] = ploty

    return ret


def draw_lane_lines(original_image, warped_image, Minv, draw_info, show_result):
    left_fitx = draw_info['left_fitx']
    right_fitx = draw_info['right_fitx']
    ploty = draw_info['ploty']

    warp_zero = np.zeros_like(warped_image).astype(np.uint8)
    color_warp = np.dstack((warp_zero, warp_zero, warp_zero))

    pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
    pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
    pts = np.hstack((pts_left, pts_right))

    mean_x = np.mean((left_fitx, right_fitx), axis=0)
    plt.scatter(mean_x, ploty)
    plt.show()
    degree = np.arctan((ploty[0]-ploty[-1])/(mean_x[0]-mean_x[-1]))*180/3.14
    if degree <= 0:
        degree = 180 - abs(degree)
    degree = degree - 90
    pts_mean = np.array([np.flipud(np.transpose(np.vstack([mean_x, ploty])))])

    global lane_lines
    lane_lines = None
    if show_result == True:
        cv2.fillPoly(color_warp, np.int_([pts]), (0, 255, 0))
        cv2.fillPoly(color_warp, np.int_([pts_mean]), (0, 255, 255))

        
        lane_lines = cv2.warpPerspective(color_warp, Minv, (original_image.shape[1], original_image.shape[0]))
    return pts_mean, degree

def offCenter(meanPts, inpFrame):

    # Calculating deviation in meters
    mpts = meanPts[-1][-1][-2].astype(int)
    pixelDeviation = inpFrame.shape[1] / 2 - abs(mpts)
    # print(inpFrame.shape[1] / 2, abs(mpts))
    deviation = pixelDeviation * xm_per_pix
    # direction = "left" if deviation < 0 else "right"

    return deviation


ym_per_pix = 220/85
xm_per_pix = 1


def find_position(image, show_result=False):
    birdseye, minverse = perspectiveWarp(image)
    mask = filter_image(birdseye)
    hist = plotHistogram(mask)
    left_fit, right_fit = slide_window_search(mask, hist, show_result)
    draw_info = general_search(mask, left_fit, right_fit, show_result)
    meanPts, degree = draw_lane_lines(image, mask, minverse, draw_info, show_result)
    return degree, lane_lines



if __name__ == "__main__":
    import matplotlib.pyplot as plt
    # from picamera.array import PiRGBArray
    # from picamera import PiCamera
    # camera = PiCamera()
    # camera.resolution = (image_w, image_h)
    # camera.framerate = camera_settings[2]
    # camera.saturation = camera_settings[3]
    # camera.vflip = True
    # camera.hflip = True
    # rawCapture = PiRGBArray(camera, size=image_size)
    # time.sleep(1)
    show_result = True

    while 1:
        # camera.capture(rawCapture, format="bgr", use_video_port=True)
        # image = rawCapture.array
        image = cv2.imread('./images/distance-1.jpg')
        start = time.time()
        degree, lane_lines = find_position(image, show_result)
        result = cv2.addWeighted(image, 1, lane_lines, 0.3, 0)
        cv2.imshow('result', result)
        # cv2.imshow("result",lane_lines)
#         print(find_position(image, show_result))
        print(degree)
        # print(f'position took : {time.time()-start} s')
        # rawCapture.truncate(0)
        if cv2.waitKey(1) == ord('q'):
            break

