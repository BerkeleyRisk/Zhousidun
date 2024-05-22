import bpy

# Instructions on how to use this script:
# 1) Run this script within blender's text editor (play button)
# 2) Set up your scene by having these objects. This project should already have all of this:
#       - Camera target (in this case, a ship)
#       - A hemisphere (Or any shape with at least 1 vertex, the script will generate cameras on every single vertex)
#       - A collection called "targetItems", which contains the colored version (use some colorful emission material!) of each TARGET item
# 3) Clear any existing cameras you have in the scene. Simply select them and delete. Select the collection named "Collection" (which contains the hemisphere), select your hemisphere, and click "Generate Cameras" button in the script panel.
# 4) Click "Render All Cameras" button in the script panel. the images should be saved in ./render_output/
# 5) run the python script at ./render_output/_GenerateBoundingBoxTxtFiles.py


generated_cameras = [] # list of newly generated cameras 

# User interface 
class MainPanel(bpy.types.Panel):
    bl_label = "Hemisphere Camera Generator"
    bl_idname = "PT_CamGenPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    bl_category = "CamGen"
    def draw(self, context):
        layout = self.layout
        # Panel only shows if an object to generate cameras on is selected in viewport
        if bpy.context.active_object:
            layout.prop(context.scene, "camera_target", text="Camera Target")
            layout.operator("object.generate_cameras", text="Generate Cameras")
            layout.operator("object.render_all_cameras", text="Render All Cameras")
        else:
            layout.label(text="No object selected")

# Button action for generating cameras
class GenerateCameras(bpy.types.Operator):
    bl_idname = "object.generate_cameras"
    bl_label = "Generate Cameras"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        global generated_cameras
        generated_cameras = []
        if bpy.context.active_object:
            obj = bpy.context.active_object
            # Create a camera for each vertex on the selected mesh
            for vert in obj.data.vertices:
                bpy.ops.object.camera_add(location=obj.matrix_world @ vert.co, rotation=(0, 0, 0))
                camera = bpy.context.active_object
                camera.data.lens = 50 # adjustable !
                generated_cameras.append(camera)
            # Parent each camera to the selected object
            for cam in generated_cameras:
                cam.location = obj.matrix_world.inverted() @ cam.location
                cam.rotation_euler = (0, 0, 0)
                cam.parent = obj
                constraint = cam.constraints.new(type='TRACK_TO')
                constraint.target = context.scene.camera_target
                constraint.track_axis = 'TRACK_NEGATIVE_Z'
                constraint.up_axis = 'UP_Y'
        return {'FINISHED'}

# Button action for rendering all cameras
class RenderAllCameras(bpy.types.Operator):
    bl_idname = "object.render_all_cameras"
    bl_label = "Render All Cameras"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        global generated_cameras
        if generated_cameras and context.scene.camera_target:
            for index, cam in enumerate(generated_cameras):
                distance_x = cam.location.x - context.scene.camera_target.location.x
                distance_y = cam.location.y - context.scene.camera_target.location.y
                distance_z = cam.location.z - context.scene.camera_target.location.z
                
                context.scene.camera = cam

                # RENDER COLOR LAYER FIRST ! show colored objects and hide actual render items, and disable any lighting
                # These show/hide operations are SCENE-SPECIFIC: everything is hardcoded here, such as show/hiding the ocean,
                # which means if you modify names or add new objects, you'll have to manually update this accordingly.
                bpy.data.collections["targetItems"].hide_render = False
                bpy.data.collections["targetItems"].hide_viewport = False
                bpy.context.scene.view_settings.view_transform = 'Raw'
                bpy.data.objects["large ocean"].hide_render = True
                bpy.context.scene.world.use_nodes = False
                bpy.data.collections["Lights"].hide_render = True
                
                filepath = f"//render_output/TARGETS_camera_{distance_x:.2f}_{distance_y:.2f}_{distance_z:.2f}.png"
                context.scene.render.filepath = filepath
                
                bpy.ops.render.render(write_still=True)

                # RENDER MAIN IMAGE ! show actual render items and hide colored objects from earlier
                bpy.data.collections["targetItems"].hide_render = True
                bpy.data.collections["targetItems"].hide_viewport = True
                bpy.context.scene.view_settings.view_transform = 'Filmic'
                bpy.data.objects["large ocean"].hide_render = False
                bpy.context.scene.world.use_nodes = True
                bpy.data.collections["Lights"].hide_render = False
                
                filepath = f"//render_output/camera_{distance_x:.2f}_{distance_y:.2f}_{distance_z:.2f}.png"
                context.scene.render.filepath = filepath
                
                bpy.ops.render.render(write_still=True)
        elif not context.scene.camera_target:
            self.report({'ERROR'}, "Please select a Camera Target.")
        else:
            self.report({'INFO'}, "No cameras generated to render.")

        return {'FINISHED'}



# register and unregister commands for blender to display the GUI and read operations
def register():
    bpy.types.Scene.camera_target = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.utils.register_class(MainPanel)
    bpy.utils.register_class(GenerateCameras)
    bpy.utils.register_class(RenderAllCameras)

def unregister():
    bpy.utils.unregister_class(MainPanel)
    bpy.utils.unregister_class(GenerateCameras)
    bpy.utils.unregister_class(RenderAllCameras)
    del bpy.types.Scene.camera_target
    
if __name__ == "__main__":
    register()



