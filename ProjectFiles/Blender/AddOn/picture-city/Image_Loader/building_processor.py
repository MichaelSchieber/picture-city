import cv2
import numpy as np
from . import utility_functions as utils
from .lot import Lot

class BuildingProcessor():

    def __init__(self, building_img):

        self.building_img = building_img
        self.building_img_marked = np.copy(building_img)
        self.building_img_contours = np.copy(building_img)
        self.building_img_bbox = np.copy(building_img)
        self.x_res, self.y_res, channels = building_img.shape

    def process_lots(self):

        buildings_gray = cv2.cvtColor(self.building_img, cv2.COLOR_BGR2GRAY)
        self.lot_contours, _  = cv2.findContours(buildings_gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        self.lots_overview_img = np.zeros(self.building_img.shape)
        self.lots_imgs = []
        self.lots = []
        
        i=0
        for contour in self.lot_contours:
            if i == 0:
                i = i+1
                continue
            # Create an Array Representation of a picture of a lot. Initialized with negative values.
            # They symbolize the pixels outside the lot (Could be maybe made more efficient by making the size only as
            # big as the Bounding Box)
            lot = np.zeros((self.x_res, self.y_res, 3))
            max = 0.0

            BBox = [[self.x_res-1, self.y_res-1], [0, 0]]
            # Calculate the Bounding Box of the lot so further operations have to only be calculated inside
            # the Bounding Box and not over the whole picture
            for point in contour:
                if point[0][0] < BBox[0][0]:
                    BBox[0][0] = point[0][0]
                if point[0][0] > BBox[1][0]:
                    BBox[1][0] = point[0][0]
                if point[0][1] < BBox[0][1]:
                    BBox[0][1] = point[0][1]
                if point[0][1] > BBox[1][1]:
                    BBox[1][1] = point[0][1]
            
            # Test the distance between each pixel in the Bounding Box and the Contour of the lot
            # Indices have to be strangely moved around - I suspect the pointPolygonTest method has those the worng way around somehow
            for y in range(BBox[0][0], BBox[1][0] + 1):
                for x in range(BBox[0][1], BBox[1][1] + 1):
                    dist = cv2.pointPolygonTest(contour, (y, x), True)
                    if dist > 0.0:
                        lot[x][y] = (1, 1, 1)
                    else:
                        lot[x][y] = (0, 0, 0)
                    if dist > max:
                        max = dist
            
#            for y in range(BBox[0][0], BBox[1][0] + 1):
#                for x in range(BBox[0][1], BBox[1][1] + 1):
#                    value = 1.0 - utils.reMap(lot[x][y][0], max, 0, 1.0, 0, negativeAsMax=True)
#                    lot[x][y] = (value, value, value)
#                    #print(array[x][y])
            self.lots_imgs.append(lot)
            self.lots_overview_img = cv2.add(self.lots_overview_img, lot)
            self.lots.append(Lot(lot, BBox, contour))

            cv2.drawContours(self.building_img_contours, [contour], 0, (0, 0, 255), 5)    
            cv2.drawContours(self.building_img_bbox, [contour], 0, (0, 0, 255), 5)    
            cv2.rectangle(self.building_img_bbox, (BBox[0][0],BBox[0][1]), (BBox[1][0], BBox[1][1]), (255, 255, 0), 2)

    def fill_lots(self):
        #self.lots[0].place_buildings()
        
        for lot in self.lots:
            #print("lot fill started")
            lot.place_buildings()
            #print("lot filled")

