from shutil import ExecError
from sys import version
import bpy
import os
from ..api import get_root_names, fetch_version_list_as_enum_option
from burnin.entity.surreal import Thing
from burnin.entity.node import Node
from burnin.entity.version import Version
from burnin.entity.filetype import Geometry
from burnin.entity.utils import buildDirPathFromVersionNode
from burnin.api import BurninClient


def on_root_name_change(self, context):
    print(f"🔹 Selected API item: {self.burnin_import_root_name}")


def on_version_type_change(self, context):
    print(f"🔹 Selected API item: {self.burnin_import_version_type}")

def on_component_path_change(self, context):
    scene = context.scene
    root_id = scene.burnin_import_root_id
    component_path = scene.burnin_import_component_path
    version_items = fetch_version_list_as_enum_option(root_id, component_path)

    bpy.types.Scene.burnin_import_version_type = bpy.props.EnumProperty(
        name="Version Type",
        description="Select Version Type",
        items= version_items,
        update=on_version_type_change 
    )

def fetch_version_list_enum(self, context):
    scene = context.scene
    root_id = scene.burnin_import_root_id
    component_path = scene.burnin_import_component_path
    return fetch_version_list_as_enum_option(root_id, component_path)

def register_import_properties():
    _burnin_root_name = os.getenv("BURNIN_ROOT_NAME")
    burnin_root_id = os.getenv("BURNIN_ROOT_ID")
    burnin_root_path = os.getenv("BURNIN_ROOT_PATH")

    # burnin roots
    bpy.types.Scene.burnin_import_root_id = bpy.props.StringProperty(
        name="Burnin Import RootID",
        default=burnin_root_id
    )

    bpy.types.Scene.burnin_import_root_path = bpy.props.StringProperty(
        name="Burnin Import Root Path",
        default=burnin_root_path
    )

    bpy.types.Scene.burnin_import_root_name = bpy.props.EnumProperty(
        name="Root Name",
        description="Select Burnin Root",
        items=get_root_names,  # ← dynamic items callback
        update=on_root_name_change,
    )

    # Import user data
    bpy.types.Scene.burnin_import_component_path = bpy.props.StringProperty(
        name="Burnin Import Component Path",
        default="",
        update=on_component_path_change
    )

    bpy.types.Scene.burnin_import_version_type = bpy.props.EnumProperty(
        name="Version Type",
        description="Select Version Type",
        items=[],
        update=on_version_type_change
    )

def unregister_import_properties():
    del bpy.types.Scene.burnin_import_root_id
    del bpy.types.Scene.burnin_import_root_path
    del bpy.types.Scene.burnin_import_root_name
    del bpy.types.Scene.burnin_import_component_path



class BURNIN_IMPORTER(bpy.types.Operator):
    bl_idname = "burnin.importer"
    bl_label = "Burnin Importer"
    bl_description = "Import Files using burnin component path"

    def execute(self, context):
        scene = context.scene
        root_id = scene.burnin_import_root_id
        root_path = scene.burnin_import_root_path
        root_name = str(scene.burnin_import_root_name).split(".")[-1]
        component_path = scene.burnin_import_component_path

        version_type = scene.burnin_import_version_type

        component_id = Thing.from_ids(root_id, component_path + "/" + version_type)

        try:
            burnin_client = BurninClient()

            version_node: Node = burnin_client.get_version_node(component_id) 
            if not version_node.node_type.variant_name == "Version":
                message = f"Invalid node type: {version_node.node_type.variant_name}"
                self.report({"ERROR"}, message)
                raise Exception(message)


            node_file_path = buildDirPathFromVersionNode(version_node, root_path, root_name)
        
            
            node_type: Version = version_node.node_type.data
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
            bpy.ops.wm.usd_import(filepath=str(file_path))



            ## blender operations to put the asset in the right place
            imported_objects = bpy.context.selected_objects

            def get_top_parent(obj):
                """Return the highest parent in the hierarchy."""
                while obj.parent is not None:
                    obj = obj.parent
                return obj
            
            top_parents = {get_top_parent(obj) for obj in imported_objects}

            print("IMPORTED OBJECTS", top_parents)

            for top in top_parents:
                parent_name = top.name.split(".")[0]
                if parent_name in ["character", "prop", "env"]:
                    prop_root = bpy.data.objects.get(parent_name)
                    if prop_root:
                        print(f"🔹 Parenting '{top.name}' under existing prop '{prop_root.name}'")

                        # Re-parent all children of the imported top to the prop_root
                        for obj in top.children:
                            obj.parent = prop_root

                        # Delete the top parent itself
                        bpy.data.objects.remove(top, do_unlink=True)
                    else:
                        print(f"⚠️ No existing prop object found to parent '{top.name}'")
                else:
                    pass


        except Exception as e:
            print(e)
            self.report({"ERROR"}, e)
            raise Exception(e)

        return {"FINISHED"}

    
    def invoke(self, context, event):
        return self.execute(context)


class BurninImporterPanel(bpy.types.Panel):
    bl_label = "Burnin Importer"
    bl_idname = "VIEW3D_PT_burnin_importer_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Burnin"  
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "burnin_import_root_name", text="Root Name")
        layout.label(text=f"Root ID: {scene.burnin_import_root_id}")
        layout.label(text=f"Root Path: {scene.burnin_import_root_path}")

        layout.prop(scene, "burnin_import_component_path", text="Component Path")
        layout.prop(scene, "burnin_import_version_type", text="Version Type")

        layout.operator("burnin.importer", text="Import")
