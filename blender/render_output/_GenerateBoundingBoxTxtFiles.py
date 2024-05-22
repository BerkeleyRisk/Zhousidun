import cv2
import numpy as np
import os 

# This script reads images in its root folder that starts with "TARGETS_" and generates a .txt file containing 
# the bounding box locations and labels for each ship target. 
# It does this using openCV (color masking and bounding boxes).
# The output is formatted for use for YOLO model training data. 
def __main__():
    # gets this script's full file path
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
    print(dir_path)

    # generates (r,g,b) numpy array
    def rgbArr(r, g, b):
        return np.array([r, g, b], dtype=np.uint8)
    
    # get the bounding rectangle in (x, y, w, h) form. lower and upper are bounds for color detection
    def getCoordsForColor(image, lower, upper):
        mask = cv2.inRange(image, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            x, y, w, h = cv2.boundingRect(contours[0])
            print(x, y, w, h)
            return x, y, w, h
        else:
            print("No pixels found for color")
            return None
        
    # iterate through each file that starts with TARGETS_, and generate txt file containing bounding boxes
    filenames = [f for f in os.listdir(dir_path) if f.startswith('TARGETS_')]
    for filename in filenames:
        image_path = dir_path + filename   

        # read and fix image colors
        image = cv2.imread(image_path)
        height, width = image.shape[:2]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # get bounding box coordinates, each a tuple of x, y, w, h
        red = getCoordsForColor(image, rgbArr(200, 0, 0), rgbArr(255, 50, 50))
        green = getCoordsForColor(image, rgbArr(0, 200, 0), rgbArr(50, 255, 50))
        blue = getCoordsForColor(image, rgbArr(0, 0, 200), rgbArr(50, 50, 255))
        cyan = getCoordsForColor(image, rgbArr(0, 200, 200), rgbArr(50, 255, 255))
        purple = getCoordsForColor(image, rgbArr(200, 0, 200), rgbArr(255, 50, 255))
        yellow = getCoordsForColor(image, rgbArr(200, 200, 0), rgbArr(255, 255, 50))

        # normalizes coordinates, then format the coordinate tuple into a string
        def formatCoords(coords):
            cx = (coords[0] + coords[2]/2)/width
            cy = (coords[0] + coords[3]/2)/height
            w = coords[2]/width
            h = coords[3]/height
            return str(cx) + " " + str(cy) + " " + str(w) + " " + str(h)
        
        # Generate text file 
        writeout = ""
        if red:
            writeout += "aegis-aft " + formatCoords(red) + "\n"
        if green:
            writeout += "aegis-starboard-bow " + formatCoords(green) + "\n"
        if blue:
            writeout += "aegis-bow " + formatCoords(blue) + "\n"
        if cyan:
            writeout += "aegis-starboard-aft " + formatCoords(cyan) + "\n"
        if purple:
            writeout += "aegis-port-aft " + formatCoords(purple) + "\n"
        if yellow:
            writeout += "aegis-port-bow " + formatCoords(yellow) + "\n" 
        txt_filepath = dir_path + os.path.splitext(filename[8:])[0] + ".txt"
        with open(txt_filepath, 'w') as f:
            f.write(writeout)

__main__()