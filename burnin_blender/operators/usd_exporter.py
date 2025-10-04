import bpy
import os

class BURNIN_OT_export_usd(bpy.types.Operator):
    bl_idname = "burnin.export_usd"
    bl_label = "Export Selected as USD"
    bl_description = "Export selected objects to USD using a custom root prim"

    prim_path: bpy.props.StringProperty(
        name="USD Prim Path",
        description="Prim path for USD filename, e.g. /asset/character/ch_hero",
        default="/untitled"
    )

    root_name: bpy.props.StringProperty(
        name="Root Prim Name",
        description="Name of root empty for USD export",
        default="World"
    )

    def execute(self, context):

        scene = context.scene
        root_name = scene.burnin_root_name
        root_id = scene.burnin_root_id


        selected_objects = context.selected_objects
        if not selected_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}

        # Create an empty root object
        root_empty = bpy.data.objects.new(self.root_name, None)
        context.collection.objects.link(root_empty)

        # Parent selected objects to the root
        for obj in selected_objects:
            obj.parent = root_empty

        # Hard-coded export folder
        export_folder = r"X:\tmp"
        os.makedirs(export_folder, exist_ok=True)

        # Create filename from prim path
        filename = self.prim_path.lstrip("/").replace("/", "_") + ".usd"
        filepath = os.path.join(export_folder, filename)

        try:
            bpy.ops.wm.usd_export(
                filepath=filepath,
                selected_objects_only=True,
            )
            self.report({'INFO'}, f"USD exported: {filepath} with root {self.root_name}")
            print(f"✅ USD exported to: {filepath} with root {self.root_name}")
        finally:
            # Unparent objects and remove the temporary root
            for obj in selected_objects:
                obj.parent = None
            bpy.data.objects.remove(root_empty)

        return {'FINISHED'}

    def invoke(self, context, event):
        # Directly run execute when called from UI
        return self.execute(context)
