import bpy
import os
from burnin.entity.utils import buildDirPathFromVersionNode
from burnin.entity.surreal import Thing
from burnin.api import BurninClient
from burnin.entity.node import Node
from burnin.entity.version import Version
from burnin.entity.filetype import Geometry
from ..structure import init_collections


class BU_SHOT_BUILD(bpy.types.Operator):
    bl_idname = "burnin.bu_shot_build"
    bl_label = "Build Shot Entity"
    bl_description = "Build Selected Shot Asset Entity"

    def execute(self, context):
        scene = context.scene
        root_id = os.getenv("BURNIN_ROOT_ID")
        root_path = os.getenv("BURNIN_ROOT_PATH")
        root_name = os.getenv("BURNIN_ROOT_NAME")
        show_name = scene.bu_show

        seq = "seq:" + scene.bu_seq
        shot = "shot:" + scene.bu_shot
        shot_entity = scene.bu_shot_entity
        shot_asset_type_var = scene.bu_shot_asset
        shot_asset_type_var_split = shot_asset_type_var.split(":")
        shot_asset_type = shot_asset_type_var_split[0]
        shot_asset_name = shot_asset_type_var_split[1]
        version_type = scene.bu_shot_asset_version_type

        component_name = shot_asset_type + "_" + shot_asset_name

        component_full_path = f"@/show:{show_name}/sequences/{seq}/{shot}/publishes/{shot_entity}/{component_name}"
        scene.bu_shot_component_path

        component_id = Thing.from_ids(root_id, component_full_path + "/" + version_type)

        try: 
            burnin_client = BurninClient()

            version_node: Node = burnin_client.get_version_node(component_id) 
            if not version_node.node_type.variant_name == "Version":
                message = f"Invalid node type: {version_node.node_type.variant_name}"
                self.report({"ERROR"}, message)
                raise Exception(message)

            node_file_path  = buildDirPathFromVersionNode(version_node, root_path, root_name)

            node_type: Version = version_node.node_type.data
            scene.bu_shot_comment = node_type.comment

            if not node_type.file_type.variant_name == "Geometry":
                message = f"Invalid file type: {node_type.file_type.variant_name}"
                self.report({"ERROR"}, message)
                raise Exception(message)
            
            file_type: Geometry = node_type.file_type.data
            file_name = file_type.file_name
            file_format = file_type.file_format

            if file_format not in [".usdc", ".usd", ".usdz", ".usda"]:
                message = f"Invalid file format: Does not support the file format: {file_format}."
                self.report({"ERROR"}, message)
                raise Exception(message)
            
            file_name_with_format = file_name + file_format
            file_path = node_file_path / file_name_with_format
            print(file_path)

            init_collections(shot_asset_type, shot_asset_name)

            asset_col = bpy.data.collections.get(shot_asset_name)
            if asset_col:
                if len(asset_col.objects) > 0:
                    bpy.ops.object.select_all(action='DESELECT')
                    for obj in asset_col.objects:
                        obj.select_set(True)
                    bpy.ops.object.delete()
                    print(f"All objects deleted from '{asset_col.name}'.")
                
                for layer_col in bpy.context.view_layer.layer_collection.children:
                    if layer_col.collection == asset_col:
                        bpy.context.view_layer.active_layer_collection = layer_col
                        print(f"'{asset_col.name}' is now active.")
                        break

                bpy.ops.wm.usd_import(filepath=str(file_path))
                # force_sync_object_and_mesh_names_sanitized()

            
        except Exception as e:
            print(e)
            self.report({"ERROR"}, e)
            raise Exception(e)

        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)