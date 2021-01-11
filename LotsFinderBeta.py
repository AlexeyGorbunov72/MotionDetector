import cv2 as open_cv
import numpy as np
import sys
import os
from time import gmtime, strftime
# from colors import COLOR_WHITE
# from drawing_utils import draw_contours

class LotsDetector:
    KEY_RESET = ord("r")
    KEY_QUIT = ord("q")
    visited = {}
    canny = None
    storeFolderPath = ""
    rectangels = []
    countFree = 0
    countOccupated = 0
    rawImage = None
    def __init__(self, image, output, path):
        os.makedirs(f'{path}/{strftime("%Y-%m-%d %H:%M:%S", gmtime())}')
        self.storeFolderPath = f'{path}/{strftime("%Y-%m-%d %H:%M:%S", gmtime())}'
        self.output = output
        self.caption = image
        self.image = open_cv.imread(image).copy()
        self.rawImage = self.image.copy()
        self.testPic = self.image.copy()
        self.click_count = 0
        self.ids = 0
        self.coordinates = []
        self.color = (255, 0, 0)

        open_cv.namedWindow(self.caption, open_cv.WINDOW_GUI_EXPANDED)
        open_cv.setMouseCallback(self.caption, self.__mouse_callback)

    def generate(self):
        while True:
            open_cv.imshow(self.caption, self.image)
            key = open_cv.waitKey(0)

            if key == LotsDetector.KEY_RESET:
                self.image = self.image.copy()
            elif key == LotsDetector.KEY_QUIT:
                break
        open_cv.destroyWindow(self.caption)

    def __mouse_callback(self, event, x, y, flags, params):

        if event == open_cv.EVENT_LBUTTONDOWN:
            self.coordinates.append((x, y))
            self.click_count += 1

        if event == open_cv.EVENT_RBUTTONDOWN:
            blur = open_cv.blur(self.image, (6, 6))
            self.canny = open_cv.Canny(blur, 100, 2500, apertureSize=5)
            open_cv.imwrite(f"{self.storeFolderPath}/cannyMapImage.jpg", self.canny)
            self.bfs(self.coordinates[-1][0], self.coordinates[-1][1])
            self.findLots()
            return
        open_cv.imshow(self.caption, self.image)

    def __handle_click_progress(self):
        open_cv.line(self.image, self.coordinates[-1], self.coordinates[-2], (255, 0, 0), 1)

    def bfs(self, vertexX, vertexY):
        queue = [(vertexY, vertexX)]
        while len(queue) > 0:
            position = queue.pop()
            if self.canny[position[0]][position[1]] != 0:
                continue
            if self.visited.get(position) is not None:
                continue
            self.visited.update({position: True})
            try:
                self.testPic[position[0]][position[1]] = (255, 0, 0)
            except:
                continue
            if self.checkIfBorderNeer(position):
                queue.append((position[0] + 1, position[1]))
                queue.append((position[0] - 1, position[1]))
                queue.append((position[0], position[1] + 1))
                queue.append((position[0], position[1] - 1))
        for i in range(len(self.testPic)):
            for j in range(len(self.testPic[i])):
                if self.testPic[i][j][0] != 255 and self.testPic[i][j][1] != 0 and self.testPic[i][j][2] != 0:
                    self.testPic[i][j] = (0, 0, 0)

        open_cv.imwrite("hui.jpg", self.testPic)

    def checkIfBorderNeer(self, position):
        for i in range(2):
            if self.canny[position[0]][position[1] + i] != 0:
                return False
            if self.canny[position[0]][position[1] - i] != 0:
                return False
            if self.canny[position[0] + i][position[1] + i] != 0:
                return False
            if self.canny[position[0] - i][position[1] + i] != 0:
                return False
            if self.canny[position[0] + i][position[1] - i] != 0:
                return False
            if self.canny[position[0] - i][position[1] - i] != 0:
                return False
            if self.canny[position[0] - i][position[1]] != 0:
                return False
            if self.canny[position[0] + i][position[1]] != 0:
                return False
        return True
    def colorize(self, rectangle):
        min_y = min(rectangle[0][1], rectangle[1][1])
        min_x = min(rectangle[0][0], rectangle[1][0])
        max_x = max(rectangle[0][0], rectangle[1][0])
        max_y = max(rectangle[0][1], rectangle[1][1])
        total = 0

        for i in range(min_y, max_y):
            for j in range(min_x, max_x):
                total += self.canny[i][j]
        total = total / ((max_x - min_x) * (max_y - min_y))
        print(min_x, max_x, min_y, max_y)
        print(self.canny[min_y : max_y, min_x : max_x])

        isOccupated = False
        if total > 7:
            self.countOccupated += 1
            color = (0, 0, 255)
            isOccupated = True
        else:
            self.countFree += 1
            color = (0, 255, 0)

        font = open_cv.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        open_cv.putText(self.image, f"{total//1}", (min_x // 2 + max_x // 2, min_y // 2 + max_y// 2), font,
                            fontScale, color, 1, open_cv.LINE_AA)
        open_cv.rectangle(self.image, (min_x, min_y), (max_x, max_y), color, 3)
        return isOccupated

    def findLots(self):
        max_top = 0
        oldx_max = -1000
        min_button = 0
        oldx_min = -1000
        listOfTopVertex = []
        listOfBottomVertex = []
        for key in self.visited:
            max_top = max(max_top, key[0])
            min_button = min(min_button, key[0])
        print(max_top)
        for key in self.visited:
            if abs(key[0] - max_top) < 20 and abs(oldx_max - key[1]) > 50:
                oldx_max = key[1]
                listOfTopVertex.append(key)

            if abs(key[0] - min_button) < 20 and abs(oldx_min - key[1]) > 50:
                oldx_min = key[1]
                listOfBottomVertex.append(key)

        listOfTopVertex.sort(key= lambda x: x[1])
        listOfBottomVertex.sort(key=lambda x: x[1])
        middleYvalue = self.coordinates[-1][1]
        for i in range(0, len(listOfTopVertex) - 1, 1):
            leftVertex = listOfTopVertex[i]
            rightVertex = listOfTopVertex[i + 1]
            self.rectangels.append(((leftVertex[1], middleYvalue), (rightVertex[1], rightVertex[0])))

        for i in range(0, len(listOfBottomVertex) - 1, 1):
            leftVertex = listOfBottomVertex[i]
            rightVertex = listOfBottomVertex[i + 1]
            self.rectangels.append(((leftVertex[1], middleYvalue), (rightVertex[1], rightVertex[0])))
        for rect in self.rectangels:
            if self.colorize(rect):
                self.createLogRect(rect, True)
            else:
                self.createLogRect(rect, False)

    def createLogRect(self, rectangle, isOccupated):
        if isOccupated:
            prefix = "occupatedLot"
        else:
            prefix = "freeLot"
        min_y = min(rectangle[0][1], rectangle[1][1])
        min_x = min(rectangle[0][0], rectangle[1][0])
        max_x = max(rectangle[0][0], rectangle[1][0])
        max_y = max(rectangle[0][1], rectangle[1][1])
        name = f"{prefix}:{rectangle}"
        os.makedirs(f"{self.storeFolderPath}/{name}")
        cannyRect = self.canny[min_y : max_y, min_x : max_x]
        originalImageRect = self.rawImage[min_y : max_y, min_x : max_x]
        open_cv.imwrite(f"{self.storeFolderPath}/{name}/canny.bmp", cannyRect)
        open_cv.imwrite(f"{self.storeFolderPath}/{name}/orig.jpg", originalImageRect)


a = LotsDetector("/Users/Retard/PycharmProjects/MotionDetector/testpICS/test7.jpg",
                 open("/Users/Retard/PycharmProjects/MotionDetector/pics/log.txt", 'w'),
                         "/Users/Retard/PycharmProjects/MotionDetector/logs")
a.generate()
