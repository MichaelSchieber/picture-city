import cv2
import numpy as np
import math
from . import utility_functions as utils
import bpy

class Building():
    def __init__(self, point, radius):
        self.point = point
        self.radius = radius
        self.side_len = 2 * (radius / math.sqrt(2))

class Lot():

    def __init__(self, lot_stencil, b_box, contour):

        self.building_radii = [10, 7 , 5]
        self.current_building_radius_index = 0

        self.lot_stencil = lot_stencil
        
        
        self.b_box = b_box
        self.contour = contour
        
        self.lot_distance_map = np.ones(lot_stencil.shape)
        self.buildings = []
        self.intermediate_building_stencil_map = np.ones(lot_stencil.shape)

        #Test - Remove later
        #self.intermediate_building_stencil_map = self.calc_intermediate_building_map((20, 300), 10)
        #self.intermediate_building_stencil_map = self.calc_intermediate_building_map((50, 100), 7)

        self.building_stencil_map = np.ones(lot_stencil.shape)
        
        self.distance_map = self.calc_dist_map()
        self.norm_distance_map = self.calc_norm_dist_map()
        self.inverse_distance_map = self.calc_inverse_distance_map()
        self.edge_stencil_map = self.calc_edge_stencil_map(10)


        
        self.lot_placement_map = lot_stencil

        self.int_map_save = np.ones(lot_stencil.shape)
        self.build_map_save = np.ones(lot_stencil.shape)
        self.placement_map_save = np.ones(lot_stencil.shape)
        
        
        

    def place_buildings(self):

        self.lot_placement_map = cv2.multiply(self.edge_stencil_map, self.inverse_distance_map)
        radius_index = 0
        i = 0
        for j in range(0, 1000):
            
            self.recalculate_placement_map(self.building_radii[radius_index])
            if i == 8:
                self.int_map_save = np.copy(self.intermediate_building_stencil_map)
                self.build_map_save = np.copy(self.building_stencil_map)
                self.placement_map_save = np.copy(self.lot_placement_map)

            point, max = self.find_place()
            if max > 0.0:
                self.buildings.append(Building(point, self.building_radii[radius_index]))
                self.intermediate_building_stencil_map = self.calc_intermediate_building_map(point, self.building_radii[radius_index])
                print("Building: " + str(i))
                print("Max: " + str(max))
                i +=1

            else:
                radius_index +=1

                if radius_index >= len(self.building_radii):
                    return

        #for i in range(0, 10):
        #    self.calculate_distance_map()
        #    self.lot_placement_map = cv2.multiply(self.lot_distance_map, self.lot_stencil)
        #    #cv2.imshow("DistanceMap_" + str(i), self.lot_distance_map)
        #    #cv2.imshow("PlacementMap_" + str(i), self.lot_placement_map)
        #    point, max = self.find_place()
        #    if max < 0.3:
        #        return
        #    self.building_points.append(point)

        

        #cv2.imshow("DistanceMap", self.lot_distance_map)
        #cv2.imshow("PlacementMap", self.lot_placement_map)

    def recalculate_placement_map(self, radius):
        self.edge_stencil_map = self.calc_edge_stencil_map(radius)
        self.building_stencil_map = self.calc_building_stencil_map(radius)
        self.lot_placement_map = cv2.multiply(self.edge_stencil_map, self.inverse_distance_map)
        self.lot_placement_map = cv2.multiply(self.lot_placement_map, self.building_stencil_map)


    def find_place(self):
        max = 0.0
        best_point = (-1, -1)
        
        for y in range(self.b_box[0][0], self.b_box[1][0] + 1):
            for x in range(self.b_box[0][1], self.b_box[1][1] + 1):
                if self.lot_placement_map[x][y][0] > max:
                    max = self.lot_placement_map[x][y][0]
                    best_point = (x, y)
        
        return best_point, max

    def calculate_distance_map(self):
        if len(self.building_points) == 0:
            return
        max = 0
        for y in range(self.b_box[0][0], self.b_box[1][0] + 1):
            for x in range(self.b_box[0][1], self.b_box[1][1] + 1):
                min_dist = float('inf')
                for point in self.building_points:
                    dist = math.sqrt(math.pow(point[0] - x, 2) + math.pow(point[1] - y, 2))
                    min_dist = dist if dist < min_dist else min_dist
                max = min_dist if min_dist > max else max
                self.lot_distance_map[x][y] = (min_dist, min_dist, min_dist)
        
        for y in range(self.b_box[0][0], self.b_box[1][0] + 1):
            for x in range(self.b_box[0][1], self.b_box[1][1] + 1):
                value = utils.reMap(self.lot_distance_map[x][y][0], max, 0.0, 1.0, 0.0)
                self.lot_distance_map[x][y] = (value, value, value)

    def calc_inverse_distance_map(self):

        return (1.0 - self.norm_distance_map)

    
    def calc_dist_map(self):
        stencil_8bit = np.copy(self.lot_stencil)
        stencil_8bit *= 255
        stencil_8bit = stencil_8bit.astype('uint8')
        stencil_8bit = cv2.cvtColor(stencil_8bit, cv2.COLOR_BGR2GRAY)
        return cv2.distanceTransform(stencil_8bit, cv2.DIST_L2, 3)
    
    def calc_norm_dist_map(self):

        map = cv2.normalize(self.distance_map, None, 0, 1, cv2.NORM_MINMAX)
        map = cv2.merge((map, map, map))
        map = map.astype(np.float64)
        return map
    
    def calc_edge_stencil_map(self, radius):

        _, map = cv2.threshold(self.distance_map, radius, 1.0, cv2.THRESH_BINARY)
        map = cv2.merge((map, map, map))
        map = map.astype(np.float64)
        return map
    
    def calc_intermediate_building_map(self, building_point, radius):
        temp_map = np.ones(self.lot_stencil.shape)
        temp_map[building_point[0]][building_point[1]] = (0, 0, 0)
        temp_map *= 255
        temp_map = temp_map.astype(np.uint8)
        temp_map = cv2.cvtColor(temp_map, cv2.COLOR_BGR2GRAY)
        temp_map = cv2.distanceTransform(temp_map, cv2.DIST_L2, 3)
        _, temp_map = cv2.threshold(temp_map, radius, 1.0, cv2.THRESH_BINARY)
        temp_map = cv2.merge((temp_map, temp_map, temp_map))
        temp_map = temp_map.astype(np.float64)
        temp_map = cv2.multiply(temp_map, self.intermediate_building_stencil_map)
        return temp_map


    def calc_building_stencil_map(self, radius):
        map = np.copy(self.intermediate_building_stencil_map)
        map *= 255
        map = map.astype(np.uint8)
        map = cv2.cvtColor(map, cv2.COLOR_BGR2GRAY)
        map = cv2.distanceTransform(map, cv2.DIST_L2, 3)
        _, map = cv2.threshold(map, radius, 1.0, cv2.THRESH_BINARY)
        map = cv2.merge((map, map, map))
        map = map.astype(np.float64)
        return map
