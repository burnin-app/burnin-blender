from pathlib import Path
import bpy
import os
from burnin.entity.utils import parse_node_path, os_slash

def buildFilePath(context, include_file_name: bool = False, component_path: str = None) -> Path:
    scene = context.scene
    root_name = (scene.burnin_root_name).split(".")[1]
    root_path = scene.burnin_root_path
    root_path = Path(root_path)

    if component_path is None:
        component_path = scene.burnin_export_component_path

    component_path = parse_node_path(component_path)

    if component_path.startswith(os_slash()):
        component_path = component_path[1:]
    
    version_number = scene.burnin_export_version_number

    print(root_path, root_name, component_path)
    file_path = Path(root_path) / root_name / component_path/ version_number

    if include_file_name:
        file_type = scene.burnin_export_file_type

        file_name = component_path.split("/")[-1] + "_" + version_number + file_type
        return file_path / file_name
    else:
        return file_path


def buildFilePathFromEnv(component_path: str , version_number: str) -> Path:
    root_path = os.getenv("BURNIN_ROOT_PATH")
    root_name = os.getenv("BURNIN_ROOT_NAME")

    component_path = parse_node_path(component_path)

    if component_path.startswith(os_slash()):
        component_path = component_path[1:]

    file_path = Path(root_path) / root_name / component_path / version_number

    return file_path


def buildEnumOptions(items: list[str]) -> list[(str, str, str)]:
    output = []
    for item in items:
        k = (str(item), str(item), "")
        output.append(k)
    return output


def selectObjectsInCollection(collection):
    """Select all objects inside the given collection (including all nested children)."""
    for obj in collection.objects:
        obj.select_set(True)
    for child in collection.children:
        selectObjectsInCollection(child)



def findLayerCollection(layer_collection, target_collection):
    """Recursively find the LayerCollection corresponding to a bpy.data.collection"""
    if layer_collection.collection == target_collection:
        return layer_collection
    for child in layer_collection.children:
        found = findLayerCollection(child, target_collection)
        if found:
            return found
    return None


def makeCollectionActive(collection):
    """Make the given collection active in the current view layer."""
    layer_collection = findLayerCollection(bpy.context.view_layer.layer_collection, collection)
    layer_collection = bpy.data.collections.get(collection)
    if layer_collection:
        bpy.context.view_layer.active_layer_collection = layer_collection
        print(f"'{collection.name}' is now the active collection.")
    else:
        print(f"Could not find LayerCollection for '{collection.name}'.")

def meshNamesSanitized():
    print("RUNNING FORCE SYNC OBJ NAMES WITH SANITIZATION")
    
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            # Sanitize object name (replace . with _)
            new_obj_name = obj.name.replace('.', '_')
            if obj.name != new_obj_name:
                print(f"Renaming object '{obj.name}' -> '{new_obj_name}'")
                obj.name = new_obj_name
            
            # Check for existing meshes with the same name
            for mesh in bpy.data.meshes:
                if mesh.name == obj.name and mesh != obj.data:
                    print(f"Renaming existing mesh '{mesh.name}' to avoid conflict")
                    mesh.name = mesh.name + "_old"  # temporary rename to free the name
            
            # Force mesh rename to match sanitized object name
            obj.data.name = obj.name
            print(f"Updated: Object '{obj.name}' -> Mesh '{obj.data.name}'")