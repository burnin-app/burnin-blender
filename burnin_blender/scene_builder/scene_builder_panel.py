import bpy


class BurninScenePanel(bpy.types.Panel):
    bl_label = "Scene Builder"
    bl_idname = "VIEW3D_PT_burnin_scene_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Burnin"  # Creates a separate tab

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.operator("burnin.build_scene", text="Initialize Scene")