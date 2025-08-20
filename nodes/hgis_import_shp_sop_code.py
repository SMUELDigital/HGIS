node = hou.pwd()
geo  = node.geometry()
geo.clear()
mod  = node.parent().type().hdaModule()  # PythonModule on the HDA
parms = {
    "shp_path": node.evalParm("shp_path"),
    "target_epsg": node.evalParm("target_epsg"),
    "attr_prefix": node.evalParm("attr_prefix"),
    "import_z": bool(node.evalParm("import_z")),
    "group_by": node.evalParm("group_by"),
}
mod.import_shp(geo, parms)
