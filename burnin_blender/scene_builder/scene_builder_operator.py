
import bpy

class BURNIN_SCENE_BUILDER(bpy.types.Operator):
    bl_idname = "burnin.build_scene"
    bl_label = "Build Burnin Scene"
    bl_description = "Build clean Burnin Scene Layout"


    def execute(self, context):
        print("Building Scene")

        # --- Step 1: Clear the current scene ---
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        # Optional: clear orphan data for a completely clean file
        for block_type in (
            bpy.data.meshes, bpy.data.materials, bpy.data.textures, bpy.data.images,
            bpy.data.curves, bpy.data.cameras, bpy.data.lights
        ):
            for block in block_type:
                bpy.data.batch_remove([block])

        # --- Step 2: Create a root hierarchy ---
        def create_empty(name, parent=None):
            empty = bpy.data.objects.new(name, None)
            empty.empty_display_size = 0.01
            empty.empty_display_type = 'PLAIN_AXES'
            if parent:
                empty.parent = parent
            return empty

        # Check if the asset collection already exists
        asset_collection = bpy.data.collections.get("asset")
        if not asset_collection:
            asset_collection = bpy.data.collections.new("asset")
            bpy.context.scene.collection.children.link(asset_collection)

        # Create subcategory empties and link only to the asset collection
        for name in ["character", "prop", "env"]:
            if name not in asset_collection.objects:
                empty = create_empty(name)
                empty.hide_select = True
                asset_collection.objects.link(empty)

        return {"FINISHED"}
    


    def invoke(self, context, event):
        return self.execute(context)
