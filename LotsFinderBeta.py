import cv2 as open_cv
import numpy as np
import sys
#from colors import COLOR_WHITE
#from drawing_utils import draw_contours

class CoordinatesGenerator:
    KEY_RESET = ord("r")
    KEY_QUIT = ord("q")
    visited = {}
    canny = None
    rectangels = []
    def __init__(self, image, output):
        sys.setrecursionlimit(10000000)
        self.output = output
        self.caption = image
        self.image = open_cv.imread(image).copy()
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

            if key == CoordinatesGenerator.KEY_RESET:
                self.image = self.image.copy()
            elif key == CoordinatesGenerator.KEY_QUIT:
                break
        open_cv.destroyWindow(self.caption)

    def __mouse_callback(self, event, x, y, flags, params):

        if event == open_cv.EVENT_LBUTTONDOWN:
            self.coordinates.append((x, y))
            self.click_count += 1
            if self.click_count % 2 == 0:
                #self.__handle_click_progress()
                pass
        if event == open_cv.EVENT_RBUTTONDOWN:
            print(self.coordinates)
            threshold1 = 100
            threshold2 = 2500
            self.canny = open_cv.Canny(self.image, 100, 2500, apertureSize=5)

            self.dfs(self.coordinates[-1][0], self.coordinates[-1][1])
            open_cv.imwrite("fuck.jpg", self.canny)
            self.findLots()
            return
        open_cv.imshow(self.caption, self.image)

    def __handle_click_progress(self):
        open_cv.line(self.image, self.coordinates[-1], self.coordinates[-2], (255, 0, 0), 1)

    def __handle_done(self):
        open_cv.line(self.image,
                     self.coordinates[2],
                     self.coordinates[3],
                     self.color,
                     1)
        open_cv.line(self.image,
                     self.coordinates[3],
                     self.coordinates[0],
                     self.color,
                     1)

        self.click_count = 0

        coordinates = np.array(self.coordinates)

        self.output.write("-\n          id: " + str(self.ids) + "\n          coordinates: [" +
                          "[" + str(self.coordinates[0][0]) + "," + str(self.coordinates[0][1]) + "]," +
                          "[" + str(self.coordinates[1][0]) + "," + str(self.coordinates[1][1]) + "]," +
                          "[" + str(self.coordinates[2][0]) + "," + str(self.coordinates[2][1]) + "]," +
                          "[" + str(self.coordinates[3][0]) + "," + str(self.coordinates[3][1]) + "]]\n")

        self.ids += 1

    def dfs(self, vertexX, vertexY):
        try:
            print(self.canny[vertexY][vertexX])
            if self.canny[vertexY][vertexX] != 0:
                return
            if self.visited.get((vertexY, vertexX)) is not None:
                return
        except:
            return
        self.visited.update({(vertexY, vertexX): True})
        self.image[vertexY][vertexX] = (255, 0, 0)
        self.dfs(vertexX + 1, vertexY)
        self.dfs(vertexX - 1, vertexY)
        self.dfs(vertexX, vertexY + 1)
        self.dfs(vertexX, vertexY - 1)

    def colorize(self, rectangle):
        min_y = min(rectangle[0][1], rectangle[1][1])
        min_x = min(rectangle[0][0], rectangle[1][0])
        max_x = max(rectangle[0][0], rectangle[1][0])
        max_y = max(rectangle[0][1], rectangle[1][1])
        total = 0
        for i in range(min_y, max_y):
            for j in range(min_x, max_x):
                total += self.canny[i][j]
        total = total / ((max_x - min_x)*(max_y - min_y))
        print("total: ", total)
        if total > 7:
            color =  (0, 0, 255)
        else:
            color =  (0, 255, 0)
        open_cv.rectangle(self.image, (min_x, min_y), (max_x, max_y), color, 3)
    def findLots(self):
        max_top = 0
        oldx_max = -1000
        min_button = 0
        oldx_min = -1000
        listOfTopVertex = []
        listOfBottomVertex = []
        print(1488)
        for key in self.visited:
            max_top = max(max_top, key[0])
            min_button = min(min_button, key[0])
        print(max_top)
        for key in self.visited:
            if abs(key[0] - max_top) < 20 and abs(oldx_max - key[1]) > 50:
                #max_top = max(key[0], max_top)
                oldx_max = key[1]
                listOfTopVertex.append(key)
            if abs(key[0] - min_button) < 20 and abs(oldx_min - key[1]) > 50:
                #min_button = min(key[0], min_button)
                oldx_min = key[1]
                listOfBottomVertex.append(key)
        middley = self.coordinates[-1][1]

        print(self.coordinates[-1])

        for i in range(0, len(listOfTopVertex), 2):
            try:
                print(i)
                fuck = listOfTopVertex[i]
                fuck1 = listOfTopVertex[i + 1]
                print(fuck, fuck1)
                #open_cv.rectangle(self.image, (fuck[1], middley), (fuck1[1], fuck1[0]), (255, 0, 0), 3)
                self.rectangels.append(((fuck[1], middley), (fuck1[1], fuck1[0])))
            except:
                print(i)
                fuck = listOfTopVertex[i]
                fuck1 = listOfTopVertex[i - 1]
                print(fuck, fuck1)
                #open_cv.rectangle(self.image, (fuck[1], middley), (fuck1[1], fuck1[0]), (255, 0, 0), 3)
                self.rectangels.append(((fuck[1], middley), (fuck1[1], fuck1[0])))

        for i in range(0, len(listOfBottomVertex), 2):
            try:
                print(i)
                fuck = listOfBottomVertex[i]
                fuck1 = listOfBottomVertex[i + 1]
                print(fuck, fuck1)
                #open_cv.rectangle(self.image, (fuck[1], middley), (fuck1[1], fuck1[0]), (255, 0, 0), 3)
                self.rectangels.append(((fuck[1], middley), (fuck1[1], fuck1[0])))
            except:
                print(i)
                fuck = listOfBottomVertex[i]
                fuck1 = listOfBottomVertex[i - 1]
                #open_cv.rectangle(self.image, (fuck[1], middley), (fuck1[1], fuck1[0]), (255, 0, 0), 3)
                self.rectangels.append(((fuck[1], middley), (fuck1[1], fuck1[0])))
        #exit(1488)
        for fuck in listOfTopVertex:
            print(fuck)
            self.image[fuck[0]][fuck[1] + 1] = (255, 0, 0)
            self.image[fuck[0]][fuck[1] - 1] = (255, 0, 0)
            self.image[fuck[0] + 1][fuck[1]] = (255, 0, 0)
            self.image[fuck[0] - 1][fuck[1]] = (255, 0, 0)
        for fuck in listOfBottomVertex:
            print(fuck)
            self.image[fuck[0]][fuck[1] + 1] = (255, 0, 0)
            self.image[fuck[0]][fuck[1] - 1] = (255, 0, 0)
            self.image[fuck[0] + 1][fuck[1]] = (255, 0, 0)
            self.image[fuck[0] - 1][fuck[1]] = (255, 0, 0)
        for rect in self.rectangels:
            self.colorize(rect)
a = CoordinatesGenerator("/Users/Retard/PycharmProjects/MotionDetector/pics/pic1.png", open("/Users/Retard/PycharmProjects/MotionDetector/pics/fuck.txt", 'w'), )
a.generate()
