import cv2
import sys
import numpy as np
# Load the image file
image = cv2.imread('/Users/Retard/PycharmProjects/MotionDetector/pics/pic0.jpg')

# Check if image was loaded improperly and exit if so
if image is None:
    sys.exit('Failed to load image')

# Detect edges in the image. The parameters control the thresholds
edges = cv2.Canny(image, 100, 2500, apertureSize=5)
cv2.imshow('output', edges)
cv2.waitKey()
# Display the output in a window


rho = 1  # distance resolution in pixels of the Hough grid
theta = np.pi / 180  # angular resolution in radians of the Hough grid
threshold = 15  # minimum number of votes (intersections in Hough grid cell)
min_line_length = 50  # minimum number of pixels making up a line
max_line_gap = 20  # maximum gap in pixels between connectable line segments
line_image = np.copy(edges) * 0  # creating a blank to draw lines on

# Run Hough on edge detected image
# Output "lines" is an array containing endpoints of detected line segments
lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                    min_line_length, max_line_gap)

for line in lines:
    for x1,y1,x2,y2 in line:
        cv2.line(line_image,(x1,y1),(x2,y2),(255,0,0),5)
cv2.imshow('output', line_image)
cv2.waitKey()