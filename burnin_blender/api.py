from burnin.api import BurninClient
from burnin.entity.surreal import Thing
from burnin.entity.node import Node
from .utils import buildEnumOptions

_root_names = []

def get_root_names(self, context):
    global _root_names
    _root_names = []

    burnin_client = BurninClient()
    roots = burnin_client.get_local_root_names()
    i = 1
    for  root in roots:
        k = (str(i) + "." + root, root, "")
        i = 1 + 1
        _root_names.append(k)
    
    return _root_names


def fetch_version_list(root_id, component_path) -> list[str]:
    burnin_client = BurninClient()
    component_id: Thing = Thing.from_ids(root_id, component_path)
    try:
        component_node: Node = burnin_client.get_component_version_node(component_id)
        version_type_list = ["Latest", "Atop"]
        version_list = component_node.get_segment_names()
        version_list = list(reversed(version_list))
        print(version_list, "FROM FETCH VERSION LIST")
        version_type_list.extend(version_list)
        return version_type_list
    except Exception as e:
        print(e)
        return []


def fetch_version_list_as_enum_option(root_id, component_path) -> list[(str, str, str)]:
    version_list = fetch_version_list(root_id, component_path)
    return buildEnumOptions(version_list)
