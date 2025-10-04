import bpy
import os
from burnin.api import BurninClient

_root_names = []

def get_root_names(self, context):
    global _root_names
    _root_names = []

    client = BurninClient()
    roots = client.get_local_root_names()
    i = 1
    for  root in roots:
        k = (str(i), root, "")
        i = 1 + 1
        _root_names.append(k)
    
    return _root_names

def on_combobox_change(self, context):
    print(f"🔹 Selected API item: {self.burnin_api_option}")
    selected = self.burnin_api_option
    enum = self.bl_rna.properties['burnin_api_option']
    print(enum.enum_items)
    print(enum)

def register_properties():
    bpy.types.Scene.burnin_usd_primpath = bpy.props.StringProperty(
        name="USD Prim Path",
        default="/asset/character/ch_hero"
    )
    bpy.types.Scene.burnin_usd_root = bpy.props.StringProperty(
        name="Root Prim",
        default="/World"
    )


    # burnin environ
    burnin_root_name = os.getenv("BURNIN_ROOT_NAME")
    burnin_root_id = os.getenv("BURNIN_ROOT_ID")
    burnin_root_path = os.getenv("BURNIN_ROOT_PATH")

    bpy.types.Scene.burnin_root_name = bpy.props.StringProperty(
        name="BURNIN ROOT NAME",
        default="Test"
    )

    bpy.types.Scene.burnin_root_id = bpy.props.StringProperty(
        name="BURNIN ROOT ID",
        default=burnin_root_id
    )

    # burnin roots
    bpy.types.Scene.burnin_api_option = bpy.props.EnumProperty(
        name="API Options",
        description="Fetched dynamically from external API",
        items=get_root_names,  # ← dynamic items callback
        update=on_combobox_change,
    )


def unregister_properties():
    del bpy.types.Scene.burnin_usd_primpath
    del bpy.types.Scene.burnin_usd_root
    del bpy.types.Scene.burnin_root_name
    del bpy.types.Scene.burnin_root_id