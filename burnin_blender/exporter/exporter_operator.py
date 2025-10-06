import bpy
from ..utils import buildFilePath

from burnin.api import BurninClient
from burnin.entity.node import Node
from burnin.entity.version import Version, VersionStatus
from burnin.entity.surreal import Thing
from burnin.entity.filetype import FileType
from burnin.entity.utils import TypeWrapper

class BURNIN_EXPORTER(bpy.types.Operator):
    bl_idname = "burnin.export_usd"
    bl_label = "Export Selected as USD"
    bl_description = "Export selected objects to USD using a custom root prim"


    def execute(self, context):

        scene = context.scene
        root_name = scene.burnin_root_name
        root_id = scene.burnin_root_id
        component_path = scene.burnin_export_component_path


        selected_objects = context.selected_objects
        if not selected_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}
        
        print(root_name, root_id, component_path)

        component_id: Thing = Thing.from_ids(root_id, component_path + "/v000")
        version_node: Node = Node.new_version(component_id, FileType.Geometry)
        burnin_client = BurninClient()
        print(burnin_client)

        try:
            version_node: Node = burnin_client.create_or_update_component_version(version_node)
            if version_node:
                version_node_id = version_node.get_node_id_str()
                version_number = version_node_id.split("/")[-1]
                scene.burnin_export_version_number = version_number
                print(version_number)
                print(version_node)

                file_path = buildFilePath(context=context, include_file_name=False)
                scene.burnin_export_status = VersionStatus.Incomplete.value
                file_name = component_path.split("/")[-1] + "_" + version_number + scene.burnin_export_file_type
                file_path_with_file_name  = file_path / file_name
                print(file_name, "FILE_NAME")
                print(file_path)
                print(file_path_with_file_name)

                export_mesh = False
                export_camera = False

                export_type = scene.burnin_export_type
                if export_type == "MESH":
                    export_mesh = True
                    export_camera = False

                elif export_type == "CAMERA":
                    export_camera = True
                    export_mesh = False

                # Export logic
                bpy.ops.wm.usd_export(
                    filepath=str(file_path_with_file_name),
                    root_prim_path="/asset",  
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

                    export_custom_properties=True,
                    custom_properties_namespace="userProperties",
                    evaluation_mode='RENDER'
                )

                self.report({'INFO'}, f"USD exported: {file_path_with_file_name}")
                print(f"✅ USD exported to: {file_path_with_file_name}")


                # update node type data: Version
                version_type: Version = version_node.node_type.data
                version_type.comment = scene.burnin_export_comment
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
                print(version_node)
                node_type: Version = version_node.node_type.data
                scene.burnin_export_status = node_type.status


        except Exception as e:
            self.report({'ERROR'}, str(e) )

        finally:
            pass


        return {'FINISHED'}

    def invoke(self, context, event):
        # Directly run execute when called from UI
        return self.execute(context)
