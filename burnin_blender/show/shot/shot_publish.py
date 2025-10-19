from burnin.entity.utils import buildDirPathFromVersionNode
import bpy
import os
from burnin.entity.surreal import Thing
from burnin.api import BurninClient
from burnin.entity.node import Node
from burnin.entity.version import Version, VersionStatus
from burnin.entity.filetype import FileType
from burnin.entity.utils import TypeWrapper

from ...utils import meshNamesSanitized, selectObjectsInCollection, buildFilePathFromEnv


class BU_SHOT_PUBLISH(bpy.types.Operator):
    bl_idname = "burnin.bu_shot_publish"
    bl_label = "Publish Shot Entity"
    bl_description = "Publish Selected Shot Asset Entity"

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



        asset_col = bpy.data.collections.get(shot_asset_name)
        if not asset_col:
            self.report({"ERROR"}, f"Asset not found in the scene to publish: {shot_asset_type}: {shot_asset_name}")
            return {"FINISHED"}

        bpy.ops.object.select_all(action='DESELECT')
        selectObjectsInCollection(asset_col)
        # meshNamesSanitized()

        component_id = Thing.from_ids(root_id, component_full_path + "/v000")
        version_node: Node = Node.new_version(component_id, FileType.Geometry)
        burnin_client = BurninClient()

        try: 
            version_node: Node = burnin_client.create_or_update_component_version(version_node)
            if version_node:
                version_node_id = version_node.get_node_id_str()
                version_number = version_node_id.split("/")[-1]
                # scene.burnin_export_version_number = version_number

                file_path = buildFilePathFromEnv(component_full_path, version_number)
                scene.burnin_export_status = VersionStatus.Incomplete.value
                file_name = component_full_path.split("/")[-1] + "_" + version_number + '.usdc'
                file_path_with_file_name  = file_path / file_name
                print(file_path)

                export_mesh = True
                export_camera = False

                if shot_asset_type == "render" and shot_asset_name =="Camera":
                    export_mesh = False
                    export_camera = True

                # Export logic
                bpy.ops.wm.usd_export(
                    filepath=str(file_path_with_file_name),
                    root_prim_path="/" + shot_asset_name,  
                    selected_objects_only=True,
                    convert_orientation=True,
                    export_global_forward_selection='NEGATIVE_Z',
                    export_global_up_selection='Y',
                    meters_per_unit=1.0,
                    # Object Types
                    export_meshes=export_mesh,
                    export_cameras=export_camera,
                    export_lights=False,
                    export_volumes=False,
                    export_curves=False,
                    export_points=False,
                    export_hair=False,
                    export_materials=False,

                    export_custom_properties=True,
                    custom_properties_namespace="userProperties",
                    evaluation_mode='RENDER'
                )

                self.report({'INFO'}, f"USD exported: {file_path_with_file_name}")
                print(f"✅ USD exported to: {file_path_with_file_name}")


                # update node type data: Version
                version_type: Version = version_node.node_type.data
                version_type.comment = scene.bu_shot_comment
                version_type.software = "blender"

                version_type.head_file = file_name
                version_type.status = VersionStatus.Published


                # update node type data: FileType
                file_type: FileType = version_type.file_type.data
                file_type.file_name = file_name.split(".")[-2]
                file_type.file_format = "." + str(file_path_with_file_name).split(".")[-1]
                # TODO: FINISH FILE TYPE

                version_type.file_type = TypeWrapper(file_type)
                version_node.node_type = TypeWrapper(version_type)
                version_node.created_at = None

                # Execute commit
                version_node: Node = burnin_client.commit_component_version(version_node)
                node_type: Version = version_node.node_type.data


        except Exception as e:
            self.report({'ERROR'}, str(e) )

        finally:
            pass

        
 
        return {"FINISHED"}
    
    def invoke(self, context, event):
        return self.execute(context)