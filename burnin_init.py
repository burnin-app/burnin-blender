def register():
    import sys

    paths = [
        "Z:/burnin/python/burninpy",
        "Z:/burnin/python/burnin-blender",
    ]

    for p in paths:
        if p not in sys.path:
            sys.path.append(p)
            print("Adding", p)

    import burnin
    import burnin_blender
    burnin_blender.enable("burnin-blender")

def unregister():
    import burnin_blender
    if hasattr(burnin_blender, "disable"):
        burnin_blender.disable("burnin-blender")

if __name__ == "__main__":
    register()