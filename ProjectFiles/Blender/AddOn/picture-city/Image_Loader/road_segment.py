from shapely.geometry import LineString
import math

class RoadSegment():
    def __init__(self, linestring: LineString):
        self.line = linestring
        self.point_0 = self.line.coords[0]
        self.point_1 = self.line.coords[1]
        self.neighbours_0 = []
        self.neighbours_1 = []

    def switch_points(self):
        temp = self.point_0
        self.point_0 = self.point_1
        self.point_1 = temp

class Intersection():
    def __init__(self, point, adjacent_segments):
        self.point = point
        self.adjacent_segments = adjacent_segments
        self.adjacent_roads = []

class Road():
    def __init__(self, road_segments, start_point, end_point, start_intersection, end_intersection):
        self.road_segments = road_segments
        self.start_point = start_point
        self.end_point = end_point
        self.start_intersection = start_intersection
        self.end_intersection = end_intersection
        self.length = self.calculate_length()

    def calculate_length(self):
        length = 0
        for segment in self.road_segments:
            x_dist_squared = math.pow(segment.point_0[0] - segment.point_1[0], 2)
            y_dist_squared = math.pow(segment.point_0[1] - segment.point_1[1], 2)
            dist = math.sqrt(x_dist_squared + y_dist_squared)
            length = length + dist
        self.length = length
        return length
    
    def order_segments(self):
        if self.road_segments[0].point_0 != self.start_point:
            self.road_segments[0].switch_points()
        
        for index in range (0, len(self.road_segments) - 1):
            if self.road_segments[index].point_1 != self.road_segments[index + 1].point_0:
                self.road_segments[index + 1].switch_points()


    def reverse(self):

        self.road_segments.reverse()
        temp = self.start_point
        self.start_point = self.end_point
        self.end_point = temp
        temp = self.start_intersection
        self.start_intersection = self.end_intersection
        self.end_intersection = temp

    def set_start_intersection(self, intersection: Intersection):
        old_point = self.start_intersection.point
        self.start_intersection = intersection
        self.start_point = intersection.point
        if self.road_segments[0].point_0 == old_point:
            self.road_segments[0].point_0 = intersection.point
        if self.road_segments[0].point_1 == old_point:
            self.road_segments[0].point_1 = intersection.point
        
        self.calculate_length()

    def set_end_intersection(self, intersection: Intersection):
        old_point = self.end_intersection.point
        self.end_intersection = intersection
        self.end_point = intersection.point
        if self.road_segments[-1].point_0 == old_point:
            self.road_segments[-1].point_0 = intersection.point
        if self.road_segments[-1].point_1 == old_point:
            self.road_segments[-1].point_1 = intersection.point
        self.calculate_length()