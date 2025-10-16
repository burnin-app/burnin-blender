import bpy
from ..utils import force_sync_object_and_mesh_names_sanitized, selectObjectsInCollection, buildFilePathFromEnv
from burnin.api import BurninClient
from burnin.entity.node import Node
from burnin.entity.version import Version, VersionStatus
from burnin.entity.surreal import Thing
from burnin.entity.filetype import FileType
from burnin.entity.utils import TypeWrapper


class BU_ASSET_PUBLISH(bpy.types.Operator):
    bl_idname = "burnin.bu_asset_publish"
    bl_label = "Publish Asset Entity"
    bl_description = "Publish Selected Asset Entity"

    def execute(self, context):
        print("Running Publish")
        scene = context.scene

        show_name = scene.bu_show
        asset_type_name = scene.bu_asset
        asset_entity = scene.bu_asset_entity
        component = scene.bu_asset_entity_component

        if len(component) <= 0:
            self.report({"ERROR"}, "Component Path is Empty")
            return {'CANCELLED'}

        asset_type = asset_type_name.split(":")[0]
        asset_name = asset_type_name.split(":")[1]

        print("PUBLISHING ASSET: ", asset_name)

        # asset_col = bpy.data.collections.get("asset")
        asset_col = bpy.data.collections.get(asset_name)

        bpy.ops.object.select_all(action='DESELECT')
        selectObjectsInCollection(asset_col)

        force_sync_object_and_mesh_names_sanitized()

        component_full_path = f"@/show:{show_name}/asset/{asset_type_name}/publishes/{asset_entity}/{component}" 
        scene.bu_component_path

        root_id = scene.burnin_root_id
        component_id: Thing = Thing.from_ids(root_id, component_full_path + "/v000")
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

                export_mesh = True
                # Export logic
                bpy.ops.wm.usd_export(
                    filepath=str(file_path_with_file_name),
                    root_prim_path="/" + asset_name,  
                    selected_objects_only=True,
                    convert_orientation=True,
                    export_global_forward_selection='NEGATIVE_Z',
                    export_global_up_selection='Y',
                    meters_per_unit=1.0,
                    # Object Types
                    export_meshes=export_mesh,
                    export_cameras=False,
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
                version_type.comment = scene.bu_comment
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