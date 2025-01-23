import cv2
import numpy as np
import random
import bpy
import bmesh

from. import utility_functions as utils
from .road_segment import RoadSegment, Intersection, Road
from .road_grid import RoadGrid
from shapely.geometry import MultiPolygon
from centerline.geometry import Centerline

class RoadProcessor():
    marked_scale = 4.0
    def __init__(self, road_img):

        self.road_img = road_img
        dim = (int(road_img.shape[1] * self.marked_scale), int(road_img.shape[0] * self.marked_scale))

        self.road_img_marked = cv2.resize(np.copy(road_img), dim)
        self.road_img_unmarked = cv2.resize(np.copy(road_img), dim)
        self.x_res, self.y_res, channels = road_img.shape
        self.marked_images = []
        self.contour_img = np.copy(road_img)

    def process_roads(self):
        #self.road_img = cv2.blur(self.road_img, (3,3))
        roads_gray = cv2.cvtColor(self.road_img, cv2.COLOR_BGR2GRAY)

        self.road_contours, hierarchy = cv2.findContours(roads_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)
        hierarchy = hierarchy[0]
        #cv2.imshow('gray', roads_gray)

        index = 0
        polygon_array = []
        for contour in self.road_contours:
            point_array = []
            for point in contour:
                point_array.append(tuple(point[0]))
            if hierarchy[index][3] < 0:
                cv2.drawContours(self.contour_img, [contour], 0, (0, 0, 255), 2)
            
                shell = tuple(map(tuple, point_array))
            else: 
                cv2.drawContours(self.contour_img, [contour], 0, (255, 200, 127), 2)
                polygon_array.append(tuple(map(tuple, point_array)))
            index = index + 1

        #print(shell)
        #print(polygon_array)
        
        multipolygon = MultiPolygon([(shell, polygon_array)])
        attributes = {"id": 1, "name": "Multipolygon", "vaild": True}
        centerline = Centerline(multipolygon, interpolation_distance= 1, **attributes)

        road_segments = []

        for linestring in centerline.geometry.geoms:
            road_segments.append(RoadSegment(linestring))
        amount = len(road_segments)
        print("Length: " + str(amount))

        grid = RoadGrid(0, 0, 3, road_segments)

        #Way faster now through grid accelleration structure

        #road_segments_compare = road_segments.copy()
        #index = 0
        #for segment in road_segments:
        #    print('\r', end='', flush=True)
        #    print(" - Comparing: " + str(index) + "/" + str(amount), end = ' ',flush=True)
        #    index +=1
        #    road_segments_compare.remove(segment)
        #    print("Compare length: " + str(len(road_segments_compare)) + "   ", end = ' ', flush=True)
        #    for compare_segment in road_segments_compare:
        #        if segment.line.coords[0] == compare_segment.line.coords[0]:
        #            segment.neighbours_0.append(compare_segment)
        #            compare_segment.neighbours_0.append(segment)
        #        if segment.line.coords[1] == compare_segment.line.coords[0]:
        #            segment.neighbours_1.append(compare_segment)
        #            compare_segment.neighbours_0.append(segment)
        #        if segment.line.coords[0] == compare_segment.line.coords[1]:
        #            segment.neighbours_0.append(compare_segment)
        #            compare_segment.neighbours_1.append(segment)
        #        if segment.line.coords[1] == compare_segment.line.coords[1]:
        #            segment.neighbours_1.append(compare_segment)
        #            compare_segment.neighbours_1.append(segment)
        #print("")

        self.road_img_marked_after = self.road_img_marked.copy()

        self.intersections = self.find_intersections(road_segments)
        self.roads = self.calculate_roads(self.intersections)
        


        for linestring in centerline.geometry.geoms:
            #print("linestart")
            co1 = linestring.coords[0]
            point1 = (round(co1[0] * self.marked_scale), round(co1[1] * self.marked_scale))
            cv2.circle(self.road_img_marked, point1, radius = 1, color=(0, 255, 0), thickness=-1)
            
            
            #if self.is_intersection(co1, linestring, centerline.geometry.geoms):
            #    cv2.circle(self.road_img_marked, point1, radius=3, color=(0,0,255), thickness = 1)
            
            
            co2 = linestring.coords[1]
            point2 = (round(co2[0] * self.marked_scale), round(co2[1] * self.marked_scale))
            cv2.circle(self.road_img_marked, point2, radius = 1, color=(255, 0, 0), thickness=-1)

            #if self.is_intersection(co2, linestring, centerline.geometry.geoms):
            #    cv2.circle(self.road_img_marked, point2, radius=3, color=(0,0,255), thickness = 1)

            cv2.line(self.road_img_marked, point1, point2, (0,0,255), thickness=1)
            for co in linestring.coords:
                #print("point: " + str(co[0]) + " " + str(co[1]))
                point = (round(co[0]), round(co[1]))
                
            #print("lineend")
        self.marked_images.append(self.mark_road_img(self.road_img_unmarked.copy()))
        self.del_short_dead_ends()

        self.merge_short_roads()
        #needs to run multiple times to get rid of all the bad things

        #self.mark_road_img(self.road_img_marked_after)
#
        #inter_no_roads, inter_one_road, inter_two_roads = self.get_invalid_intersections()
#
        #if len(inter_no_roads) > 0 or len(inter_one_road) > 0 or len(inter_two_roads) > 0:
        #    self.remove_invalid_intersections(inter_no_roads, inter_one_road, inter_two_roads)
#
        #self.marked_images.append(self.mark_road_img(self.road_img_unmarked.copy()))

        self.create_roads()


        i = 0
        for img in self.marked_images:
            #cv2.imshow('Marked_image' + str(i), img)
            i = i + 1

        #cv2.imshow('Contours', self.road_img_marked)
        #cv2.imshow('After cleanup', self.road_img_marked_after)
        dst = cv2.cornerHarris(np.float32(roads_gray), 2, 3, 0.04)
        #dst = cv2.dilate(dst, None)
        #cv2.imshow('dst', dst)
        img = np.copy(self.road_img)
        img[dst>0.05*dst.max()]=[0,0,255]

        #cv2.imshow('Corners', img)

    def is_intersection(self, point, self_linestring, multilinestring):
        intersecting_lines = []
        for linestring in multilinestring:

            if linestring == self_linestring:
                continue
            else:
                if point == linestring.coords[0] or point == linestring.coords[1]:
                    intersecting_lines.append(linestring)
        
        if len(intersecting_lines) > 1:
            print("Intersection at: " + str(point))
            return True
        
        else: 
            return False

    def find_intersections(self, road_segments: list[RoadSegment]):
        intersections = []
        for segment in road_segments:
            if len(segment.neighbours_0) > 1:

                adjacent_segments = segment.neighbours_0.copy()
                adjacent_segments.append(segment)
                intersection = Intersection(segment.line.coords[0], adjacent_segments)
                if self.is_unique_intersection(intersection, intersections):
                    intersections.append(intersection)

                    point = (round(segment.line.coords[0][0] * self.marked_scale), round(segment.line.coords[0][1] * self.marked_scale))
                    cv2.circle(self.road_img_marked, point, radius=5, color=(0,0,255), thickness=1)
                    print("Intersection at: " + str(point))

            if len(segment.neighbours_1) > 1:
                adjacent_segments = segment.neighbours_1.copy()
                adjacent_segments.append(segment)
                intersection = Intersection(segment.line.coords[1], adjacent_segments)
                if self.is_unique_intersection(intersection, intersections):                
                    intersections.append(intersection)

                    point = (round(segment.line.coords[1][0] * self.marked_scale), round(segment.line.coords[1][1] * self.marked_scale))
                    cv2.circle(self.road_img_marked, point, radius=5, color=(0,0,255), thickness=1)
                    print("Intersection at: " + str(point))

        return intersections

    def is_unique_intersection(self, intersection: Intersection, intersections: list[Intersection]):
        for inter in intersections:
            if inter.point == intersection.point:
                return False
        
        return True

    def get_intersection(self, point):

        for intersection in self.intersections:
            if intersection.point == point:
                return intersection
        return None

    def calculate_roads(self, intersections: list[Intersection]):
        roads = []
        for intersection in intersections:
            for segment in intersection.adjacent_segments:

                if not self.is_segment_in_roads(segment, roads):

                    start_intersection = intersection
                    start_point = intersection.point
                    end_point, end_intersection, road_segments = self.traverse_road(segment, start_point, road_segments=[])
                    road = Road(road_segments, start_point, end_point, start_intersection, end_intersection)
                    #print(road)
                    
                    start_intersection.adjacent_roads.append(road)
                    if end_intersection:
                        end_intersection.adjacent_roads.append(road)
                    roads.append(road)
        return roads


    def is_segment_in_roads(self, road_segment, roads):

        for road in roads:
            if road.road_segments[0] == road_segment or road.road_segments[-1] == road_segment:
                return True
        return False

    def traverse_road(self, road_segment: RoadSegment, start_point, road_segments: list[RoadSegment] = []):
        
        road_segments.append(road_segment)

        if start_point == road_segment.line.coords[0]:
            end_point = road_segment.line.coords[1]
            neighbours = road_segment.neighbours_1

        if start_point == road_segment.line.coords[1]:
            end_point = road_segment.line.coords[0]
            neighbours = road_segment.neighbours_0

        if len(neighbours) == 0:
            return end_point, None, road_segments
        if len(neighbours) > 1:
            intersection = self.get_intersection(end_point)
            return end_point, intersection, road_segments
        if len(neighbours) == 1:
            return self.traverse_road(neighbours[0], end_point, road_segments)
        
    def del_short_dead_ends(self):
        while True:
            print("----------------------")
            print(len(self.roads))
            roads_to_remove = []
            for road in self.roads:
                print(road.length)
                if road.start_intersection == None or road.end_intersection == None:
                    #print("before: " + str(road.length))
                    road.calculate_length()
                    #print("after: " + str(road.length))
                    if road.length < 30:
                        if road.start_intersection:
                            road.start_intersection.adjacent_roads.remove(road)
                        if road.end_intersection:
                            road.end_intersection.adjacent_roads.remove(road)
                        print("Removed")
                        roads_to_remove.append(road)
            if len(roads_to_remove) == 0:
                break

            for road in roads_to_remove:
                self.roads.remove(road)
            print(len(self.roads))
            self.marked_images.append(self.mark_road_img(self.road_img_unmarked.copy()))

            inter_no_roads, inter_one_road, inter_two_roads = self.get_invalid_intersections()

            if len(inter_no_roads) > 0 or len(inter_one_road) > 0 or len(inter_two_roads) > 0:
                self.remove_invalid_intersections(inter_no_roads, inter_one_road, inter_two_roads)

            self.marked_images.append(self.mark_road_img(self.road_img_unmarked.copy()))

    def mark_road_img(self, img):
        for intersection in self.intersections:
            
            point = (round(intersection.point[0] * self.marked_scale), round(intersection.point[1] * self.marked_scale))
            cv2.circle(img, point, radius=5, color=(0,0,255), thickness=1)

        for road in self.roads:
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            for segment in road.road_segments:

                point1 = (round(segment.point_0[0] * self.marked_scale), round(segment.point_0[1] * self.marked_scale))
                cv2.circle(img, point1, radius = 1, color=color, thickness=-1)
            
            
                point2 = (round(segment.point_1[0] * self.marked_scale), round(segment.point_1[1] * self.marked_scale))
                cv2.circle(img, point2, radius = 1, color=color, thickness=-1)

                cv2.line(img, point1, point2, color, thickness=1)
        return img

    def get_invalid_intersections(self):
        intersections_no_road = []
        intersections_one_road = []
        intersections_two_roads = []
        
        for intersection in self.intersections:
            if len(intersection.adjacent_roads) == 0:
                intersections_no_road.append(intersection)
            if len(intersection.adjacent_roads) == 1:
                intersections_one_road.append(intersection)
            if len(intersection.adjacent_roads) == 2:
                intersections_two_roads.append(intersection)
        return intersections_no_road, intersections_one_road, intersections_two_roads

    def remove_invalid_intersections(self, intersections_no_road, intersections_one_road, intersections_two_roads):
        
        for intersection in intersections_no_road:
            self.intersections.remove(intersection)

        for intersection in intersections_one_road:
            self.intersections.remove(intersection)
            road = intersection.adjacent_roads[0]
            if road.start_intersection == intersection:
                road.start_intersection = None
            if road.end_intersection == intersection:
                road.end_intersection = None

        for intersection in intersections_two_roads:
            adjacent_roads = intersection.adjacent_roads
            self.intersections.remove(intersection)
            self.fuse_roads(adjacent_roads[0], adjacent_roads[1])

    def fuse_roads(self, road_a: Road, road_b: Road):

        if road_a.start_point == road_b.end_point:
            road_b.road_segments.extend(road_a.road_segments)
            road_b.end_point = road_a.end_point
            road_b.end_intersection = road_a.end_intersection
            road_b.calculate_length()
            self.roads.remove(road_a)
            if road_a.end_intersection:
                road_a.end_intersection.adjacent_roads.remove(road_a)
                road_a.end_intersection.adjacent_roads.append(road_b)
            return
        
        if road_a.end_point == road_b.start_point:
            road_a.road_segments.extend(road_b.road_segments)
            road_a.end_point = road_b.end_point
            road_a.end_intersection = road_b.end_intersection
            road_a.calculate_length()
            self.roads.remove(road_b)
            if road_b.end_intersection:
                road_b.end_intersection.adjacent_roads.remove(road_b)
                road_b.end_intersection.adjacent_roads.append(road_a)
            
            return

        if road_a.start_point == road_b.start_point:
            road_a.reverse()
            road_a.road_segments.extend(road_b.road_segments)
            road_a.end_point = road_b.end_point
            road_a.end_intersection = road_b.end_intersection
            road_a.calculate_length()
            self.roads.remove(road_b)
            if road_b.end_intersection:
                road_b.end_intersection.adjacent_roads.remove(road_b)
                road_b.end_intersection.adjacent_roads.append(road_a)
            return

        if road_a.end_point == road_b.end_point:
            self.roads.remove(road_b)
            road_b.reverse()
            road_a.road_segments.extend(road_b.road_segments)
            road_a.end_point = road_b.end_point
            road_a.end_intersection = road_b.end_intersection
            road_a.calculate_length()
            if road_b.end_intersection:
                road_b.end_intersection.adjacent_roads.remove(road_b)
                road_b.end_intersection.adjacent_roads.append(road_a)
            return

        return
    
    def merge_short_roads(self):
        
        roads_to_merge = []
        for road in self.roads:
            print(road.length)
            if road.length < 30:
                if road.start_intersection and road.end_intersection:
                    roads_to_merge.append(road)
                    print("merge")

        for road in roads_to_merge:
            self.roads.remove(road)
            mid_x = (road.start_point[0] + road.end_point[0]) / 2
            mid_y = (road.start_point[1] + road.end_point[1]) / 2
            mid_point = (mid_x, mid_y)
            new_inter = Intersection(mid_point, [])
            
            self.intersections.append(new_inter)
            self.intersections.remove(road.start_intersection)
            self.intersections.remove(road.end_intersection)

            for adj_road in road.start_intersection.adjacent_roads:
                if adj_road == road:
                    continue
                new_inter.adjacent_roads.append(adj_road)
                    
                if adj_road.start_intersection == road.start_intersection:
                    new_inter.adjacent_segments.append(adj_road.road_segments[0])
                    adj_road.set_start_intersection(new_inter)
                
                if adj_road.end_intersection == road.start_intersection:
                    new_inter.adjacent_segments.append(adj_road.road_segments[-1])
                    adj_road.set_end_intersection(new_inter)

            for adj_road in road.end_intersection.adjacent_roads:
                if adj_road == road:
                    continue
                new_inter.adjacent_roads.append(adj_road)
                    
                if adj_road.start_intersection == road.end_intersection:
                    new_inter.adjacent_segments.append(adj_road.road_segments[0])
                    adj_road.set_start_intersection(new_inter)
                
                if adj_road.end_intersection == road.end_intersection:
                    new_inter.adjacent_segments.append(adj_road.road_segments[-1])
                    adj_road.set_end_intersection(new_inter)
        
        self.marked_images.append(self.mark_road_img(self.road_img_unmarked.copy()))

    def create_roads(self):
        wm = bpy.context.window_manager
        city_size = (float(wm.city_length_x), float(wm.city_length_y))
        img_res = (self.x_res, self.y_res)

        index = 0
        for road in self.roads:
            coords = []
            road.order_segments()
            for segment in road.road_segments:
                
                city_point = utils.sample_coordinate(segment.point_0, img_res, city_size)
                coords.append((city_point[1], city_point[0], 0))
                
            city_point = utils.sample_coordinate(road.road_segments[-1].point_1, img_res, city_size)
            coords.append((city_point[1], city_point[0], 0))
            
            curveData = bpy.data.curves.new('Road_' + str(index), type='CURVE')
            curveData.dimensions = '3D'
            curveData.resolution_u = 2

            polyline = curveData.splines.new('BEZIER')
            polyline.bezier_points.add(len(coords) - 1)
            for i, coord in enumerate(coords):
                x,y,z = coord
                polyline.bezier_points[i].co = (x, y, z)
                polyline.bezier_points[i].handle_left = polyline.bezier_points[i].co
                polyline.bezier_points[i].handle_right = polyline.bezier_points[i].co
            curveOB = bpy.data.objects.new('myCurve', curveData)

            scn = bpy.context.scene
            bpy.context.collection.objects.link(curveOB)
            #bpy.context.collection.active = curveOB
            #curveOB.select = True

            self.add_road_plane(curveOB)

            index += 1

    def add_road_plane(self, curve_obj):
        mesh = bpy.data.meshes.new("Road_Plane")
        obj = bpy.data.objects.new("Road_Plane", mesh)

        bpy.context.collection.objects.link(obj)

        bm = bmesh.new()
        bm.from_object(obj, bpy.context.view_layer.depsgraph)

        s = 2
        bm.verts.new((s,s,0))
        bm.verts.new((s,-s,0))
        bm.verts.new((-s,s,0))
        bm.verts.new((-s,-s,0))

        bmesh.ops.contextual_create(bm, geom=bm.verts)

        bm.to_mesh(mesh)

        array_mod = obj.modifiers.new("Array", 'ARRAY')
        array_mod.fit_type = 'FIT_CURVE'
        array_mod.curve = curve_obj
        curve_mod = obj.modifiers.new("Curve", 'CURVE')
        curve_mod.object = curve_obj
