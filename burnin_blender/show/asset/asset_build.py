import bpy
import os
from burnin.entity.surreal import Thing
from burnin.entity.node import Node
from burnin.entity.version import Version
from burnin.entity.filetype import Geometry
from burnin.entity.utils import buildDirPathFromVersionNode
from burnin.api import BurninClient

from ...utils import meshNamesSanitized
from ..structure import init_collections
import bpy




class BU_ASSET_BUILD(bpy.types.Operator):
    bl_idname = "burnin.bu_asset_build"
    bl_label = "Build Asset Entity"
    bl_description = "Build Selected Asset Entity"

    def execute(self, context):
        scene = context.scene
        root_id = os.getenv("BURNIN_ROOT_ID")
        root_path = os.getenv("BURNIN_ROOT_PATH")
        root_name = os.getenv("BURNIN_ROOT_NAME")
        show_name = scene.bu_show
        asset_type_name = scene.bu_asset
        asset_type_name_split = asset_type_name.split(":")
        asset_type = asset_type_name_split[0]
        asset_name = asset_type_name_split[1]
        asset_entity = scene.bu_asset_entity
        component = scene.bu_asset_entity_component
        version_type = scene.bu_version_type

        component_full_path = f"@/show:{show_name}/asset/{asset_type_name}/publishes/{asset_entity}/{component}" 
        scene.bu_component_path

        component_id = Thing.from_ids(root_id, component_full_path + "/" + version_type)

        try:
            burnin_client = BurninClient()

            version_node: Node = burnin_client.get_version_node(component_id) 
            if not version_node.node_type.variant_name == "Version":
                message = f"Invalid node type: {version_node.node_type.variant_name}"
                self.report({"ERROR"}, message)
                raise Exception(message)


            node_file_path = buildDirPathFromVersionNode(version_node, root_path, root_name)
        
            
            node_type: Version = version_node.node_type.data
            scene.bu_comment = node_type.comment

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


            # pre import
            init_collections(asset_type, asset_name)

            asset_col = bpy.data.collections.get(asset_name)
            if asset_col:
                # Check if it has any objects
                if len(asset_col.objects) > 0:
                #     answer = input(f"Collection '{asset_col.name}' has {len(asset_col.objects)} objects. Delete them? (y/n): ").lower()

                #     if answer == 'y':
                #         # Select and delete all objects
                #         bpy.ops.object.select_all(action='DESELECT')
                #         for obj in asset_col.objects:
                #             obj.select_set(True)
                #         bpy.ops.object.delete()
                #         print(f"All objects deleted from '{asset_col.name}'.")
                #     else:
                #         print("Cancelled.")
                # else:
                #     print(f"Collection '{asset_col.name}' is empty.")

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
                meshNamesSanitized()

        except Exception as e:
            print(e)
            self.report({"ERROR"}, e)
            raise Exception(e)

        return {"FINISHED"}

    
    def invoke(self, context, event):
        return self.execute(context)