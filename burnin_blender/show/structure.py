import bpy

def init_collections(asset_type, asset_name):
    """Ensure proper hierarchy: asset > asset_type > asset_name (true parenting) and make final active"""

    scene = bpy.context.scene
    root = scene.collection

    # --- 1. Get or create 'asset' ---
    asset_col = bpy.data.collections.get("asset")
    if not asset_col:
        asset_col = bpy.data.collections.new("asset")
        root.children.link(asset_col)
        print("Created: asset")

    # --- 2. Get or create 'asset_type' ---
    type_col = bpy.data.collections.get(asset_type)
    if not type_col:
        type_col = bpy.data.collections.new(asset_type)
        asset_col.children.link(type_col)
        print(f"Created: {asset_type}")
    else:
        # unlink from all wrong parents
        for parent in bpy.data.collections:
            if type_col.name in parent.children and parent != asset_col:
                parent.children.unlink(type_col)
        if type_col.name not in asset_col.children:
            asset_col.children.link(type_col)

    # --- 3. Get or create 'asset_name' ---
    name_col = bpy.data.collections.get(asset_name)
    if not name_col:
        name_col = bpy.data.collections.new(asset_name)
        type_col.children.link(name_col)
        print(f"Created: {asset_name}")
    else:
        # unlink from all wrong parents (including root)
        if name_col.name in root.children:
            root.children.unlink(name_col)
        for parent in bpy.data.collections:
            if name_col.name in parent.children and parent != type_col:
                parent.children.unlink(name_col)
        if name_col.name not in type_col.children:
            type_col.children.link(name_col)

    # --- 4. Make the final collection active ---
    def find_layer_collection(layer_col, target_col):
        if layer_col.collection == target_col:
            return layer_col
        for child in layer_col.children:
            found = find_layer_collection(child, target_col)
            if found:
                return found
        return None

    layer_col = find_layer_collection(bpy.context.view_layer.layer_collection, name_col)
    if layer_col:
        bpy.context.view_layer.active_layer_collection = layer_col
        print(f"✅ Active collection set to '{name_col.name}'")

    print(f"✅ Hierarchy ready: asset > {asset_type} > {asset_name}")
    return name_col
