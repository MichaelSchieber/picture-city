import bpy
import os
import numpy as np

#from PIL import Image as PILIM#
#from PIL import ImageFilter
import cv2

import random

from .building_processor import BuildingProcessor

from .road_processor import RoadProcessor

from .lot import Lot

from . import utility_functions as utils

from bpy.types import Operator

class PCT_OT_LoadImage_OP(Operator):
    bl_idname = "object.load_image"
    bl_label = "Process Buildings"
    bl_description = "Processes the buildings"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):

        wm = context.window_manager

        path = os.path.dirname(__file__)

        img_path = wm.image_filepath

        wm = context.window_manager
        self.length_x = float(wm.city_length_x)
        self.length_y = float(wm.city_length_y)

        plane_data = bpy.data.meshes.new(name="City_Plane")
        plane_obj = bpy.data.objects.new('City_Plane', plane_data)
        context.collection.objects.link(plane_obj)

        
        img_cv = cv2.imread(img_path)

        img_roads = utils.separate_by_color(img_cv, (0,0,0))
        img_buildings = utils.separate_by_color(img_cv, (128, 128, 128))
        img_parks = utils.separate_by_color(img_cv, (0, 255, 0))
        img_water = utils.separate_by_color(img_cv, (255, 0, 0))
        img_no_City = utils.separate_by_color(img_cv, (255, 255, 255))

        #cv2.imshow('Image', img_cv)
        #cv2.imshow('Image_2', img_buildings)

        b_proc = BuildingProcessor(img_buildings)
        print("bproc")
        b_proc.process_lots()
        print("lots processed")
        b_proc.fill_lots()
        print("lots filled")

        counter = 0
        for lot in b_proc.lots:

            #if wm.save_imgs:
            #    save_path = os.path.join(path, "Intermediate_Imgs")
            #    os.chdir(save_path)
            #    img = lot.lot_stencil * 255
            #    cv2.imwrite("Lot_" + str(counter) + ".jpg", img)
            #    img = lot.lot_placement_map * 255
            #    cv2.imwrite("Lot_" + str(counter) + "Placement.jpg", img)
            #    counter = counter + 1

            for building in lot.buildings:
                height = random.uniform(10, 100)
                point = utils.sample_coordinate(building.point, (img_cv.shape[0], img_cv.shape[1]), (self.length_x, self.length_y))
                side_lengths = utils.sample_coordinate((building.side_len, building.side_len), (img_cv.shape[0], img_cv.shape[1]), (self.length_x, self.length_y))
                bpy.ops.mesh.primitive_cube_add(size=1, location=(point[0], point[1], height/2), scale=(side_lengths[0], side_lengths[1], height))
        
        #cv2.imshow('lot1', b_proc.lots_imgs[0])
        #cv2.imshow('lot1_distance', b_proc.lots[0].norm_distance_map)
        #cv2.imshow('lot1 inverse', b_proc.lots[0].inverse_distance_map)
        #cv2.imshow('lot1 edge', b_proc.lots[0].edge_stencil_map)
        #cv2.imshow('lot1 building intermediate', b_proc.lots[0].intermediate_building_stencil_map)
        #cv2.imshow('lot1 building stencil', b_proc.lots[0].building_stencil_map)
        #cv2.imshow('lot 1 placement map', b_proc.lots[0].lot_placement_map)
        #cv2.imshow('Image_Contour_Dist', b_proc.lots_overview_img)
#
        buildings = img_buildings.astype(np.float64)
        buildings /= 255
        buildings_inner_contour = cv2.multiply(buildings, b_proc.lots_overview_img)
        #cv2.imshow('Buidlings_Stencil', buildings_inner_contour)
        #cv2.imshow('Image_Contours', b_proc.building_img_marked)
        
        if wm.save_imgs:
            save_path = os.path.join(path, "Intermediate_Imgs")
            os.chdir(save_path)
            cv2.imwrite("roads.jpg", img_roads)
            cv2.imwrite("buildings.jpg", img_buildings)
            cv2.imwrite("parks.jpg", img_parks)
            cv2.imwrite("water.jpg", img_water)
            cv2.imwrite("no_city.jpg", img_no_City)
            cv2.imwrite("Lot_Overview.jpg", b_proc.lots_overview_img * 255)
            cv2.imwrite('Buildings_stencil.jpg', buildings_inner_contour * 255)
            #cv2.imwrite("Image_Contours.jpg", b_proc.building_img_marked)
            cv2.imwrite("Image_Contours.jpg", b_proc.building_img_contours)
            cv2.imwrite("Image_BBox.jpg", b_proc.building_img_bbox)
            cv2.imwrite("Lot_0_Stencil.jpg", b_proc.lots[0].lot_stencil*255)
            cv2.imwrite("Lot_0_Edge_Stencil.jpg", b_proc.lots[0].edge_stencil_map*255)
            cv2.imwrite("Lot_0_NormDist.jpg", b_proc.lots[0].norm_distance_map*255)
            cv2.imwrite("Lot_0_InverseDist.jpg", b_proc.lots[0].inverse_distance_map*255)
            cv2.imwrite("Lot_0_Pass8_intermediateBuilding.jpg", b_proc.lots[0].int_map_save * 255)
            cv2.imwrite("Lot_0_Pass8_BuildingStencil.jpg", b_proc.lots[0].build_map_save * 255)
            cv2.imwrite("Lot_0_Pass8_PlacementMap.jpg", b_proc.lots[0].placement_map_save * 255)
            
            
        
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return {'FINISHED'}


class PCT_OT_LoadRoads_OP(Operator):
    bl_idname = "object.load_roads"
    bl_label = "Process Roads"
    bl_description = "Creates the Road network out of the input image"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        wm = context.window_manager
        path = os.path.dirname(__file__)
        img_path = wm.image_filepath
        img_cv = cv2.imread(img_path)
        img_roads = utils.separate_by_color(img_cv, (0,0,0))
        #img_roads = cv2.resize(img_roads, (1024, 1024), interpolation=cv2.INTER_CUBIC)
        img_roads = cv2.medianBlur(img_roads, 5)
        _, img_roads = cv2.threshold(img_roads, 127, 255, 0)

        r_proc = RoadProcessor(img_roads)
        r_proc.process_roads()

        #roads_gray = cv2.cvtColor(img_roads, cv2.COLOR_BGR2GRAY)
        #road_contours, _ = cv2.findContours(roads_gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        #contour_img = img_roads.copy()
        #for contour in road_contours:
        #    cv2.drawContours(contour_img, [contour], 0, (random.randint(0, 255), random.randint(0, 255), random.randint(0,255)), 2)
        #roads_gray = np.float32(roads_gray)
        #dst = cv2.cornerHarris(roads_gray, 2, 3, 0.04)
        #dst = cv2.dilate(dst, None)
        #corner_img = img_roads.copy()
        #corner_img[dst>0.05*dst.max()] = [0, 0, 255]

        if wm.save_imgs:
            save_path = os.path.join(path, "Intermediate_Imgs")
            os.chdir(save_path)
            cv2.imwrite("roads.jpg", img_roads)
            cv2.imwrite("roadcenterline.jpg", r_proc.road_img_marked)
            cv2.imwrite("roadcenterline_after_clean.jpg", r_proc.road_img_marked_after)
            cv2.imwrite("RoadContours.jpg", r_proc.contour_img)
            i = 0
            for img in r_proc.marked_images:
                cv2.imwrite('Marked_image' + str(i) + '.jpg', img)
                i=i+1
            #cv2.imwrite("Road_Contours.jpg", contour_img)
            #cv2.imwrite("Road_Corners.jpg", corner_img)

        #cv2.imshow("Roads", img_roads)
        #cv2.imshow("Contours", contour_img)
        #cv2.imshow("Corners", corner_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return {'FINISHED'}
