import subprocess
import sys
import os

import bpy
from bpy.props import PointerProperty, IntProperty, BoolProperty
from .Image_Loader.pct_image_loader_op import PCT_OT_LoadImage_OP, PCT_OT_LoadRoads_OP
from .Image_Loader.pct_image_loader_pnl import PCT_PT_ImageLoader_PNL

bl_info = {
    "name": "pictureCity",
    "author": "Michael Schieber",
    "description": "A tool to generate Cities out of sketches",
    "blender": (3, 4, 0),
    "version": (1, 0, 0),
    "location": "3D Viewport > Properties panel (N) > PCITY Tabs",
    "category": "Object"
}

classes = (
    PCT_PT_ImageLoader_PNL, PCT_OT_LoadImage_OP, PCT_OT_LoadRoads_OP
)

def register():
    python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
    target = os.path.join(sys.prefix, 'lib', 'site-packages')
#
    #subprocess.call([python_exe, '-m', 'ensurepip'])
    #subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'])
#
    #subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'Pillow', '-t', target])
    #subprocess.call([python_exe, '-m', 'pip', 'install', 'opencv-python', '-t', target])
    bpy.types.WindowManager.city_image = PointerProperty(name= "City Sketch", type = bpy.types.Image)
    bpy.types.WindowManager.city_length_x = IntProperty(name= "City Length", default=1000)
    bpy.types.WindowManager.city_length_y = IntProperty(name= "City Width", default=1000)
    bpy.types.WindowManager.save_imgs = BoolProperty(name="Save Intermediate imgs", default=False)
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)