import bpy

bpy.types.Scene.select_tool = bpy.props.EnumProperty(
    name="Select Tool",
    description="Choose a selection tool",
    items=[
        ('BOX', "Box", "Box Select"),
        ('CIRCLE', "Circle", "Circle Select"),
        ('LASSO', "Lasso", "Lasso Select")
    ],
    default='BOX'
)

class BurninScenePanel(bpy.types.Panel):
    bl_label = "Scene Builder"
    bl_idname = "VIEW3D_PT_burnin_scene_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Burnin"  # Creates a separate tab

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "select_tool", expand=True)  
        layout.operator("burnin.build_scene", text="Build Scene")