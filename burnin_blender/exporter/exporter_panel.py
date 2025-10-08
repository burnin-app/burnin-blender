import bpy

class BurninPanel(bpy.types.Panel):
    bl_label = "Burnin Exporter"
    bl_idname = "VIEW3D_PT_burnin_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Burnin"  # Creates a separate tab

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "burnin_root_name", text="Root Name")
        layout.label(text=f"Root ID: {scene.burnin_root_id}")
        layout.label(text=f"Root Path: {scene.burnin_root_path}")

        layout.prop(scene, "burnin_export_component_path", text="Component Path")
        layout.prop(scene, "burnin_export_file_type", text="File Type")

        layout.prop(scene, "burnin_export_usd_prim_path", text="Primitive Path")

        layout.label(text=f"Version: {scene.burnin_export_version_number}")
        layout.label(text=f"Status: {scene.burnin_export_status}")

        layout.prop(scene, "burnin_export_type", expand=True)  
        layout.operator("burnin.export_usd", text="Export USD")