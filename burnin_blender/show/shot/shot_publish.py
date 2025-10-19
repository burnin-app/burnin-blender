import bpy
import os

class BU_SHOT_PUBLISH(bpy.types.Operator):
    bl_idname = "burnin.bu_shot_publish"
    bl_label = "Publish Shot Entity"
    bl_description = "Publish Selected Shot Asset Entity"

    def execute(self, context):
        scene = context.scene
        root_id = os.getenv("BURNIN_ROOT_ID")
        root_path = os.getenv("BURNIN_ROOT_PATH")
        root_name = os.getenv("BURNIN_ROOT_NAME")
        show_name = scene.bu_show

        return {"FINISHED"}
    
    def invoke(self, context, event):
        return self.execute(context)