import bpy
import os
from ..api import get_root_names

def on_combobox_change(self, context):
    print(f"🔹 Selected API item: {self.burnin_root_name}")

def on_file_type_change(self, context):
    print(f"🔹 Selected API item: {self.burnin_export_file_type}")

def register_properties():
    # burnin environ
    burnin_root_name = os.getenv("BURNIN_ROOT_NAME")
    burnin_root_id = os.getenv("BURNIN_ROOT_ID")
    burnin_root_path = os.getenv("BURNIN_ROOT_PATH")

    # burnin roots
    bpy.types.Scene.burnin_root_id = bpy.props.StringProperty(
        name="BURNIN ROOT ID",
        default=burnin_root_id
    )

    bpy.types.Scene.burnin_root_path = bpy.props.StringProperty(
        name="BURNIN ROOT PATH",
        default=burnin_root_path
    )

    bpy.types.Scene.burnin_root_name = bpy.props.EnumProperty(
        name="Root Name",
        description="Select Burnin Root",
        items=get_root_names,  # ← dynamic items callback
        update=on_combobox_change,
    )

    bpy.types.Scene.burnin_export_file_type = bpy.props.EnumProperty(
        name="File Type",
        description="Select Export File Type",
        items=[(".usd", "usd", "Universal Scene Description"), (".abc", "abc", "Alembic")], 
        update=on_file_type_change,
    )

    # Export data
    bpy.types.Scene.burnin_export_component_path = bpy.props.StringProperty(
        name="Burnin Export Component Path",
        default=""
    )

    bpy.types.Scene.burnin_export_comment = bpy.props.StringProperty(
        name="Burnin Export Comment",
        default=""
    )

    bpy.types.Scene.burnin_export_version_number = bpy.props.StringProperty(
        name="Burnin Export Version Number",
        default=""
    )

    bpy.types.Scene.burnin_export_status = bpy.props.StringProperty(
        name="Burnin Export Status",
        default=""
    )

    bpy.types.Scene.burnin_export_usd_prim_path = bpy.props.StringProperty(
        name="Primitive Path",
        default="/asset"
    )

    bpy.types.Scene.burnin_export_type = bpy.props.EnumProperty(
        name="Export Type",
        description="Choose a export type",
        items=[
            ('MESH', "MESH", "Export Mesh"),
            ('CAMERA', "CAMERA", "Export Camera"),
        ],
        default='MESH'
    )

def unregister_properties():
    del bpy.types.Scene.burnin_usd_primpath
    del bpy.types.Scene.burnin_usd_root
    del bpy.types.Scene.burnin_root_name
    del bpy.types.Scene.burnin_root_id