from pathlib import Path
from sys import version
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




def buildEnumOptions(items: list[str]) -> list[(str, str, str)]:
    output = []
    for item in items:
        k = (str(item), str(item), "")
        output.append(k)
    return output