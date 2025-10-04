import bpy

class BurninPanel(bpy.types.Panel):
    bl_label = "Burnin Tools"
    bl_idname = "VIEW3D_PT_burnin_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Burnin"  # Creates a separate tab

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Burnin Tools")
        layout.prop(scene, "burnin_root_id", text="Root ID")
        layout.prop(scene, "burnin_root_name", text="Root Name")
        layout.prop(scene, "burnin_api_option")
        layout.operator("burnin.export_usd", text="Export USD")