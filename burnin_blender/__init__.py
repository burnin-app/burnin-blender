import bpy
from .ui import panel
from .operators import usd_exporter
from . import properties

# Collect all classes to register
classes = (
    panel.BurninPanel,
    usd_exporter.BURNIN_OT_export_usd,
)

def enable(addon_name="burnin-blender"):
    """Registers all Blender classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    properties.register_properties()
    print(f"✅ {addon_name} enabled")

def disable(addon_name="burnin-blender"):
    """Unregisters all Blender classes"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Unregister scene properties
    properties.unregister_properties()
    print(f"✅ {addon_name} disabled")