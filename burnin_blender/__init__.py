import bpy
# from .ui import panel
# EXPORTER
from .exporter import exporter_panel
from .exporter.exporter_operator import BURNIN_EXPORTER
from .exporter import exporter_properties

# SCENE BUILDER
from .scene_builder import scene_builder_panel
from .scene_builder.scene_builder_operator import BURNIN_SCENE_BUILDER

# IMPORTER
from .importer.importer_panel import BURNIN_IMPORTER, BurninImporterPanel, register_import_properties, unregister_import_properties

# BURNIN SHOW
from .show import show_panel
from .show.asset import asset_publish, asset_build
from .show.shot import shot_build, shot_publish


# Collect all classes to register
classes = (
    exporter_panel.BurninPanel,
    BURNIN_EXPORTER,

    scene_builder_panel.BurninScenePanel,
    BURNIN_SCENE_BUILDER,

    BurninImporterPanel,
    BURNIN_IMPORTER,

    show_panel.BurninShowPanel,
    show_panel.BURNIN_SHOW,
    asset_publish.BU_ASSET_PUBLISH,
    asset_build.BU_ASSET_BUILD,

    shot_publish.BU_SHOT_PUBLISH,
    shot_build.BU_SHOT_BUILD
)



def enable(addon_name="burnin-blender"):
    """Registers all Blender classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    exporter_properties.register_properties()
    register_import_properties()
    show_panel.register_properties()
    print(f"✅ {addon_name} enabled")


def disable(addon_name="burnin-blender"):
    """Unregisters all Blender classes"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Unregister scene properties
    exporter_properties.unregister_properties()
    unregister_import_properties()
    show_panel.unregister_properties()
    print(f"✅ {addon_name} disabled")