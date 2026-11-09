import bpy
import os
from ..utils import buildEnumOptions
from ..api import fetch_version_list_as_enum_option
from burnin.entity.surreal import Thing
from burnin.api import BurninClient
from burnin.entity.filetype import FileType
from burnin.entity.node import Node
from burnin.entity.version import Version, VersionStatus
import bpy
import os
from burnin.show.asset import BU_asset
from burnin.path import build_path_from_node
from burnin.show.shot import BU_shot
from burnin.entity.utils import (
    TypeWrapper,
    buildDirPathFromVersionNode,
    node_name_from_component_path,
)

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
        )

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


def update_render_settings(scene, context):


    pass

# shot_id = Thing.from_ids(root_id, shot_path)
# if scene.bu_render_animation:
#     bpy.ops.render.render(animation=True)
# else:
#     bpy.ops.render.render(animation=False)


class BU_OT_Render(bpy.types.Operator):
    bl_idname = "bu.render"
    bl_label = "Start Render"

    def execute(self, context):
        scene = context.scene
        # Set frame range
        scene.frame_start = scene.bu_render_frame_start
        scene.frame_end = scene.bu_render_frame_end

        # Set output image format to OpenEXR
        scene.render.image_settings.file_format = 'OPEN_EXR'

        # Set color mode
        scene.render.image_settings.color_mode = 'RGBA'

        # Set EXR color depth
        scene.render.image_settings.color_depth = '32'

        # Set output path
        scene.render.filepath = "//renders/"
        # scene.render.file_extension = False

        # Set frame step
        scene.frame_step = 1

        show = scene.bu_show
        seq = scene.bu_render_seq
        shot = scene.bu_render_shot
        component = scene.bu_render_shot_component
        comment = scene.bu_render_shot_comment
        print(show, seq, shot, "publishes/light", component)


        root_id = os.getenv("BURNIN_ROOT_ID")
        if root_id:
            component_path = f"@/show:{show}/sequences/seq:{seq}/shot:{shot}/publishes/light/{component}/v000"
            component_id = Thing.from_ids(root_id, component_path)
            print(component_id)
            version_node: Node = Node.new_version(component_id, FileType.Image)

            burnin_client = BurninClient()
            try:
                version_node: Node = burnin_client.create_or_update_component_version(
                    version_node
                )

                render_animation = scene.bu_render_animation
                ext = ".exr"
                if render_animation:
                    ext = ".####.exr"

                if version_node:
                    file_path = build_path_from_node(version_node)
                    file_name = (
                        node_name_from_component_path(version_node.id.id.String) + ext
                    )

                    print(file_path)
                    print(file_name)

                    full_path = file_path / file_name
                    scene.render.filepath = str(full_path)

                    print("STARTING RENDER...")
                    print("Output:", scene.render.filepath)
                    result = bpy.ops.render.render(
                        animation=scene.bu_render_animation,
                        write_still=True
                    )
                    print(result)

                    # # update node type data: Version
                    version_type: Version = version_node.node_type.data
                    version_type.comment = scene.bu_render_shot_comment
                    version_type.software = "blender"

                    version_type.head_file = file_name
                    version_type.status = VersionStatus.Published

                    # update node type data: FileType
                    file_type: FileType = version_type.file_type.data
                    file_type.file_name = file_name.split(".")[-2]
                    file_type.file_format = ".exr"
                    # TODO: FINISH FILE TYPE

                    version_type.file_type = TypeWrapper(file_type)
                    version_node.node_type = TypeWrapper(version_type)
                    version_node.created_at = None

                    # Execute commit
                    version_node: Node = burnin_client.commit_component_version(
                        version_node
                    )

                    self.report({"INFO"}, "Render completed successfully!")
                    print("RENDER FINISHED!")
            except Exception as e:
                self.report({"ERROR"}, str(e))

            finally:
                pass

        return {"FINISHED"}


def register_properties():
    bu_show = os.getenv("BU_show")
    if bu_show:
        # get assets
        burnin_root_id = os.getenv("BURNIN_ROOT_ID")
        bu_asset = BU_asset(burnin_root_id, bu_show)
        bu_asset_list = buildEnumOptions(bu_asset.assets)

        bpy.types.Scene.bu_render_asset = bpy.props.EnumProperty(
            name="BU_render_asset",
            description="Asset List",
            items=bu_asset_list,
        )

        bpy.types.Scene.bu_render_asset_component = bpy.props.StringProperty(
            name="BU_render_asset_component",
            default="",
        )

        bpy.types.Scene.bu_render_asset_comment = bpy.props.StringProperty(
            name="BU_render_asset_comment",
            default=""
        )

        # shot
        bu_shot = BU_shot(burnin_root_id, bu_show)
        bu_seq_list = buildEnumOptions(bu_shot.seq_name_list)

        bpy.types.Scene.bu_render_seq = bpy.props.EnumProperty(
            name="BU_render_seq",
            description="Sequence List",
            items=bu_seq_list,
            update=on_seq_change
        )

        # load shot list

        bpy.types.Scene.bu_render_shot = bpy.props.EnumProperty(
            name="BU_render_shot",
            description="Shot List",
            items=on_seq_init_load,
            # update=on_asset_change
        )

        bpy.types.Scene.bu_render_shot_component = bpy.props.StringProperty(
            name="BU_render_shot_component",
            default="",
        )

        bpy.types.Scene.bu_render_shot_comment = bpy.props.StringProperty(
            name="BU_render_shot_comment",
            default=""
        )

        bpy.types.Scene.bu_render_frame_start = bpy.props.IntProperty(
            name="Frame Start",
            description="Render start frame",
            default=1,
            min=0,
            update=on_render_range_change
        )

        bpy.types.Scene.bu_render_frame_end = bpy.props.IntProperty(
            name="Frame End",
            description="Render end frame",
            default=100,
            min=0,
            update=on_render_range_change
        )

        bpy.types.Scene.bu_render_animation = bpy.props.BoolProperty(
            name="Render Animation",
            description="Enable animation rendering",
            default=False
        )

def on_render_range_change(self, context):
    update_render_settings(context.scene, context)

def unregister_properties():
    del bpy.types.Scene.bu_render_asset
    del bpy.types.Scene.bu_render_asset_component
    del bpy.types.Scene.bu_render_asset_comment
    del bpy.types.Scene.bu_render_shot_comment
    del bpy.types.Scene.bu_render_shot_component
    del bpy.types.Scene.bu_render_shot_shot
    del bpy.types.Scene.bu_render_shot_seq
    del bpy.types.Scene.bu_render_frame_start
    del bpy.types.Scene.bu_render_frame_end
    del bpy.types.Scene.bu_render_animation

class BurninRenderPanel(bpy.types.Panel):
    bl_label = "Burnin Render"
    bl_idname = "VIEW3D_PT_burnin_render_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Burnin"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Render Range")
        layout.prop(scene, "bu_render_frame_start")
        layout.prop(scene, "bu_render_frame_end")
        layout.label(text="Output: EXR")
        layout.prop(scene, "bu_render_animation")
        layout.separator()

        # asset
        layout.label(text=f"show: {scene.bu_show}")
#         layout.prop(scene, "bu_render_asset", text="Asset")
#         layout.prop(scene, "bu_render_asset_component", text="Component")
#
#         layout.prop(scene, "bu_render_asset_comment", text="Comment")
#         layout.operator("burnin.bu_asset_publish", text="Publish")

        # shot
        layout.label(text=f"Shot Workflow")
        layout.prop(scene, "bu_render_seq", text="Sequence")
        layout.prop(scene, "bu_render_shot", text="Shot")
        layout.prop(scene, "bu_render_shot_component", text="Component")

        layout.prop(scene, "bu_render_shot_comment", text="Comment")
        layout.operator("bu.render", text="Render")
