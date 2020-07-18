from pathlib import Path
import cv2
import numpy as np
import math
from collections import deque
import json
from object_directions import direction_to_action, check_direction_to_move
from open_file_with_hsv_sample import load_last_sample

import urllib.request
import cv2
import numpy as np
import time

pixel = (0,0,0)
image_hsv = None
lower_hsv = [0, 0, 0]
upper_hsv = [0, 0, 0]

def check_boundaries(value, tolerance, ranges, upper_or_lower):
    if ranges == 0:
        # set the boundary for hue
        boundary = 180
    elif ranges == 1:
        # set the boundary for saturation and value
        boundary = 255

    if(value + tolerance > boundary):
        value = boundary
    elif (value - tolerance < 0):
        value = 0
    else:
        if upper_or_lower == 1:
            value = value + tolerance
        else:
            value = value - tolerance
    return value

def mouse_pick_color(event, x, y, flags, param):
    
    if event == cv2.EVENT_LBUTTONDOWN:
        
        global upper_hsv, lower_hsv, image_hsv
        
        pixel = image_hsv[y, x]

        #HUE, SATURATION, AND VALUE (BRIGHTNESS) RANGES. TOLERANCE COULD BE ADJUSTED.
        # Set range = 0 for hue and range = 1 for saturation and brightness
        # set upper_or_lower = 1 for upper and upper_or_lower = 0 for lower
        hue_upper = check_boundaries(pixel[0], 20, 0, 1)
        hue_lower = check_boundaries(pixel[0], 20, 0, 0)
        saturation_upper = check_boundaries(pixel[1], 20, 1, 1)
        saturation_lower = check_boundaries(pixel[1], 20, 1, 0)
        value_upper = check_boundaries(pixel[2], 25, 1, 1)
        value_lower = check_boundaries(pixel[2], 25, 1, 0)
        
        upper_hsv = np.array([hue_upper, saturation_upper, value_upper])
        lower_hsv = np.array([hue_lower, saturation_lower, value_lower])

        sample_data = {'upper':upper_hsv.tolist(),
                       'lower':lower_hsv.tolist()}

        with open('last_sample.json', 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=4)

def find_object_contour(image):
    global lower_hsv, upper_hsv

    def create_retangles(im):
        im = cv2.rectangle(im, (0,100), (155,380), (225,225,225), 1) # left box
        im = cv2.rectangle(im, (480,100), (640,380), (225,255,225), 1) # right box
        im = cv2.rectangle(im, (155,0), (480,100), (225,255,225), 1) # upper box
        im = cv2.rectangle(im, (155,380), (480,640), (225,255,225), 1) # lower box
        
    def get_contour(im, lower, upper):
        converted = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        skinMask = cv2.inRange(converted, lower, upper) 
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        skinMask = cv2.morphologyEx(skinMask,cv2.MORPH_OPEN, kernel)
        skinMask = cv2.morphologyEx(skinMask,cv2.MORPH_CLOSE, kernel)
        skinMask = cv2.dilate(skinMask, kernel, iterations = 4)
        skinMask = cv2.GaussianBlur(skinMask, (7,7), 0)
        contours, _ = cv2.findContours(skinMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return skinMask, contours
    
    im = cv2.flip(image, flipCode=1)
    create_retangles(im)
    image_hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

    skinMask, contours = get_contour(im, np.array(lower_hsv), np.array(upper_hsv))
    
    skin = cv2.bitwise_and(im, im, mask=skinMask)
    
    return im, image_hsv, skin, contours

def main():       
    global image_hsv
    global lower_hsv, upper_hsv

    pts = deque(maxlen=32)
    counter = 0

    cv2.namedWindow('live feed')

    my_file = Path("last_sample.json")
    if my_file.is_file():
        lower_hsv, upper_hsv = load_last_sample()
    
    cv2.setMouseCallback('live feed', mouse_pick_color)

    cap = cv2.VideoCapture(0)
    
    #print(cap.get(10))
    #print(cap.get(11))
    #print(cap.get(12))
    #print(cap.get(17))
    #cap.set(10, 100) # brightness     min: 0   , max: 255 , increment:1
    #cap.set(11, 130) # contrast       min: 0   , max: 255 , increment:1
    #cap.set(12, 100) # saturation     min: 0   , max: 255 , increment:1
    #cap.set(17, 4000) # white_balance  min: 4000, max: 7000, increment:1
    while(1):
        #use this 2 lines if cellphone camera
        #img_arr = np.array(bytearray(urllib.request.urlopen(URL).read()),dtype=np.uint8)
        #img = cv2.imdecode(img_arr,-1)
        
        #use line below if webcam
        _, img = cap.read()

        im, image_hsv, skin, contours = find_object_contour(img)
        
        try:
            cnt = max(contours, key=lambda x: cv2.contourArea(x))
            
            if len(contours) == 1:
                M=cv2.moments(cnt)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                pts.appendleft(center)
                moved_direction = check_direction_to_move(center)
                direction_to_action(moved_direction)
                
        except ValueError:
            pass
        
        cv2.imshow('live feed',im)
        #cv2.imshow('live feed', im)
        cv2.imshow('object track', skin)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.waitKey(1) & 0xFF == ord('r'):
            pass
        counter += 1
        
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()