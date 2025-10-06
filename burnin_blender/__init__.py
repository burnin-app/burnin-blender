import bpy
# from .ui import panel
from .exporter import exporter_panel
from .exporter.exporter_operator import BURNIN_EXPORTER
from .exporter import exporter_properties

from .scene_builder import scene_builder_panel
from .scene_builder.scene_builder_operator import BURNIN_SCENE_BUILDER

from .importer.importer_panel import BURNIN_IMPORTER, BurninImporterPanel, register_import_properties, unregister_import_properties

# Collect all classes to register
classes = (
    exporter_panel.BurninPanel,
    BURNIN_EXPORTER,

    scene_builder_panel.BurninScenePanel,
    BURNIN_SCENE_BUILDER,

    BurninImporterPanel,
    BURNIN_IMPORTER
)



def enable(addon_name="burnin-blender"):
    """Registers all Blender classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    exporter_properties.register_properties()
    register_import_properties()
    print(f"✅ {addon_name} enabled")


def disable(addon_name="burnin-blender"):
    """Unregisters all Blender classes"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Unregister scene properties
    exporter_properties.unregister_properties()
    unregister_import_properties()
    print(f"✅ {addon_name} disabled")