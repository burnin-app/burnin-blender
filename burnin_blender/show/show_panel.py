from burnin import show
from ..utils import buildEnumOptions
from ..api import fetch_version_list_as_enum_option

import bpy
import os
from burnin.show.asset import BU_asset
from burnin.show.shot import BU_shot

def on_asset_change(self, context):
    print("Asset changed")


def on_version_type_change(self, context):
    print(f"🔹 Selected API item: {self.bu_version_type}")

def on_component_path_change(self, context):
    scene = context.scene
    root_id = os.getenv("BURNIN_ROOT_ID")
    bu_show = scene.bu_show
    bu_asset = scene.bu_asset
    bu_asset_entity = scene.bu_asset_entity
    bu_asset_entity_component = scene.bu_asset_entity_component
    component_path = f"@/show:{bu_show}/asset/{bu_asset}/publishes/{bu_asset_entity}/{bu_asset_entity_component}"
    version_items = fetch_version_list_as_enum_option(root_id, component_path)

    if len(bu_asset_entity_component) > 0:
        bpy.types.Scene.bu_version_type = bpy.props.EnumProperty(
            name="Version",
            description="Select Version Type",
            items= version_items,
            update=on_version_type_change 
        )

def version_type_update(self, context):
    scene = context.scene
    root_id = os.getenv("BURNIN_ROOT_ID")
    bu_show = scene.bu_show
    bu_asset = scene.bu_asset
    bu_asset_entity = scene.bu_asset_entity
    bu_asset_entity_component = scene.bu_asset_entity_component
    component_path = f"@/show:{bu_show}/asset/{bu_asset}/publishes/{bu_asset_entity}/{bu_asset_entity_component}"
    version_items = fetch_version_list_as_enum_option(root_id, component_path)

    if len(bu_asset_entity_component) > 0:
        return version_items



## SHOT

def on_seq_init_load(slef, context):
    scene = context.scene
    root_id = os.getenv("BURNIN_ROOT_ID")
    bu_show = scene.bu_show
    bu_seq = scene.bu_seq

    bu_shot_cls = BU_shot(root_id, bu_show)
    bu_shot_cls.load_shot_list(bu_seq)
    if len(bu_shot_cls.shot_names_list) > 0:
        return  buildEnumOptions(bu_shot_cls.shot_names_list)
    else:
        return []


def on_seq_change(self, context):
    scene = context.scene
    root_id = os.getenv("BURNIN_ROOT_ID")
    bu_show = scene.bu_show
    bu_seq = scene.bu_seq

    bu_shot_cls = BU_shot(root_id, bu_show)
    bu_shot_cls.load_shot_list(bu_seq)
    if len(bu_shot_cls.shot_names_list) > 0:
        bu_shot_list = buildEnumOptions(bu_shot_cls.shot_names_list)
        bpy.types.Scene.bu_shot = bpy.props.EnumProperty(
            name="BU_shot",
            description="Shot List",
            items=bu_shot_list,
            update=on_asset_change
        )


def register_properties():
    bu_show = os.getenv("BU_show")

    if bu_show:
        bpy.types.Scene.bu_show = bpy.props.StringProperty(
            name="BU_show",
            default=bu_show
        )

        # get assets
        burnin_root_id = os.getenv("BURNIN_ROOT_ID")
        bu_asset = BU_asset(burnin_root_id, bu_show)
        bu_asset_list = buildEnumOptions(bu_asset.assets)

        bpy.types.Scene.bu_asset = bpy.props.EnumProperty(
            name="BU_asset",
            description="Asset List",
            items=bu_asset_list,
            update=on_asset_change
        )

        bu_asset_entity_type_list = buildEnumOptions(bu_asset.get_asset_entity_types("blender"))

        bpy.types.Scene.bu_asset_entity = bpy.props.EnumProperty(
            name="BU_asset_entity",
            description="Asset Entity Type",
            items=bu_asset_entity_type_list,
            update=on_component_path_change
        )

        bpy.types.Scene.bu_asset_entity_component = bpy.props.StringProperty(
            name="BU_asset_entity_component",
            default="",
            update=on_component_path_change
        )

        # component_full_path = f"@/show:{bu_show}/asset/{bu_asset}/publishes/model/{component}" 

        bpy.types.Scene.bu_component_path = bpy.props.StringProperty(
            name="Burnin Show Component Path",
            default="",
            update=on_component_path_change
        )

        bpy.types.Scene.bu_version_type = bpy.props.EnumProperty(
            name="Version",
            description="Select Version Type",
            items=[("Latest", "Latest", "Latest"), ("Atop", "Atop", "Atop")],
            update=on_version_type_change
        )

        bpy.types.Scene.bu_comment = bpy.props.StringProperty(
            name="BU_comment",
            default=""
        )


        ## SHOT VARIABLES

        bu_shot = BU_shot(burnin_root_id, bu_show)
        bu_seq_list = buildEnumOptions(bu_shot.seq_name_list)

        bpy.types.Scene.bu_seq = bpy.props.EnumProperty(
            name="BU_seq",
            description="Sequence List",
            items=bu_seq_list,
            update=on_seq_change
        )

        # load shot list

        bpy.types.Scene.bu_shot = bpy.props.EnumProperty(
            name="BU_shot",
            description="Shot List",
            items=on_seq_init_load,
            # update=on_asset_change
        )

        bu_shot_entity_type_list = buildEnumOptions(bu_shot.get_shot_entity_types("blender"))

        bpy.types.Scene.bu_shot_entity = bpy.props.EnumProperty(
            name="BU_shot_entity",
            description="Shot Entity Type",
            items=bu_shot_entity_type_list,
            # update=on_asset_change
        )

        bu_shot_asset_list = bu_asset_list
        bu_shot_asset_list.append(("render:Camera", "render:Camera", ""))
        

        bpy.types.Scene.bu_shot_asset = bpy.props.EnumProperty(
            name="BU_shot",
            description="Shot Asset List",
            items=bu_shot_asset_list,
            # update=on_asset_change
        )

        bpy.types.Scene.bu_shot_asset_version_type = bpy.props.EnumProperty(
            name="Version",
            description="Select Version Type",
            items=[("Latest", "Latest", "Latest"), ("Atop", "Atop", "Atop")],
            # update=on_version_type_change
        )

        bpy.types.Scene.bu_shot_comment = bpy.props.StringProperty(
            name="BU_comment",
            default=""
        )

        bpy.types.Scene.bu_shot_component_path = bpy.props.StringProperty(
            name="Shot Component Path",
            default="",
            # update=on_component_path_change
        )


def unregister_properties():
    if bpy.types.Scene.bu_show:
        del bpy.types.Scene.bu_show
        del bpy.types.Scene.bu_asset


class BURNIN_SHOW(bpy.types.Operator):
    bl_idname = "burnin.show"
    bl_label = "Burnin Show"
    bl_description = "Burnin Show for multishot workflow"


    def execute(self, context):
        scene = context.scene
    
        return {"FINISHED"}
    
    def invoke(self, context, event):
        return self.execute(context)

    



class BurninShowPanel(bpy.types.Panel):
    bl_label = "Burnin Show"
    bl_idname = "VIEW3D_PT_burnin_show_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Burnin"  

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # asset
        layout.label(text=f"show: {scene.bu_show}")
        layout.prop(scene, "bu_asset", text="Asset")
        layout.prop(scene, "bu_asset_entity", text="Entity")
        layout.prop(scene, "bu_asset_entity_component", text="Component")
        layout.prop(scene, "bu_version_type", text="Version")

        layout.operator("burnin.bu_asset_build", text="Build")
        layout.prop(scene, "bu_comment", text="Comment")
        layout.operator("burnin.bu_asset_publish", text="Publish")

        # shot
        layout.label(text=f"Shot Workflow")
        layout.prop(scene, "bu_seq", text="Sequence")
        layout.prop(scene, "bu_shot", text="Shot")
        layout.prop(scene, "bu_shot_entity", text="Entity")
        layout.prop(scene, "bu_shot_asset", text="Asset")
        layout.prop(scene, "bu_shot_asset_version_type", text="Version")

        layout.operator("burnin.bu_shot_build", text="Build")
        layout.prop(scene, "bu_shot_comment", text="Comment")
        layout.operator("burnin.bu_shot_publish", text="Publish")