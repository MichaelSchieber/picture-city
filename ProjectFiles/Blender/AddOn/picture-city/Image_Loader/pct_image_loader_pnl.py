import bpy
from bpy.props import PointerProperty, IntProperty, BoolProperty, StringProperty

class PCT_PT_ImageLoader_PNL(bpy.types.Panel):
    bl_label = "Image Loader"
    bl_category = "PCity"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    bpy.types.WindowManager.city_length_x = IntProperty(name= "City Length", default=1000)
    bpy.types.WindowManager.city_length_y = IntProperty(name= "City Width", default=1000)
    bpy.types.WindowManager.save_imgs = BoolProperty(name="Save Intermediate imgs", default=False)
    bpy.types.WindowManager.image_filepath = StringProperty(name="Image Filepath", description="Choose an input image", default="", maxlen=1024, subtype='FILE_PATH')

    def draw(self, context):
        wm = context.window_manager
        layout = self.layout
        layout.prop(wm, "image_filepath", text="")
        layout.label(text="City Size")
        row = layout.row(align=True)

        row.prop(wm, "city_length_x", text="")
        #row.label(text="m")
        row.prop(wm, "city_length_y", text="")
        #row.label(text="m")
        layout.prop(wm, "save_imgs")
        layout.operator("object.load_image")
        layout.operator("object.load_roads")
