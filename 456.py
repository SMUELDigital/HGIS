import os, hou

try:
    plugin_root = hou.expandString("$HOUDINI_USER_PREF_DIR/houdini20.5/houdinigis")
    otls_dir = os.path.join(plugin_root, "otls")
    nodes_dir = os.path.join(plugin_root, "nodes")
    os.makedirs(otls_dir, exist_ok=True)
    hda_path = os.path.join(otls_dir, "HoudiniGIS.hda")

    type_name = "hgis::import_shp::1.0"
    # Rebuild definition if missing
    need_build = True
    if os.path.exists(hda_path):
        for d in hou.hda.definitionsInFile(hda_path):
            if d.nodeTypeName() == type_name:
                need_build = False
                break

    if need_build:
        # Build temp Python SOP
        obj = hou.node("/obj") or hou.node("/").createNode("obj")
        geo = obj.createNode("geo", "HGIS_AUTOINSTALL_tmp", run_init_scripts=False)
        pysop = geo.createNode("python", "impl")

        # Load internal SOP code
        with open(os.path.join(nodes_dir, "hgis_import_shp_sop_code.py"), "r", encoding="utf-8") as f:
            pysop.parm("python").set(f.read())

        # Parameters
        ptg = pysop.parmTemplateGroup()
        from hou import StringParmTemplate, ToggleParmTemplate
        spt = StringParmTemplate("shp_path", "Shapefile (.shp)", 1, string_type=hou.stringParmType.FileReference)
        spt.setFileType(hou.fileType.Any)
        ptg.append(spt)
        ptg.append(StringParmTemplate("target_epsg", "Target CRS (EPSG)", 1, default_value=("EPSG:3857",)))
        ptg.append(StringParmTemplate("attr_prefix", "Attribute Prefix", 1, default_value=("shp_",)))
        ptg.append(ToggleParmTemplate("import_z", "Import Z/M", default_value=False))
        ptg.append(ToggleParmTemplate("swap_yz", "Swap Y/Z", default_value=False))
        ptg.append(StringParmTemplate("group_by", "Group by DBF Field", 1, default_value=("")))
        pysop.setParmTemplateGroup(ptg)

        # Create digital asset
        # Remove any old definition from file
        for d in hou.hda.definitionsInFile(hda_path):
            if d.nodeTypeName() == type_name:
                d.removeFromFile()

        hda_def = pysop.createDigitalAsset(name=type_name, hda_file_name=hda_path, description="HGIS Shapefile Import")

        # Inject PythonModule
        with open(os.path.join(nodes_dir, "hgis_pythonmodule.py"), "r", encoding="utf-8") as f:
            py_mod = f.read()
        # Prefer the Sections API
        try:
            secs = hda_def.sections()
            if "PythonModule" in secs:
                secs["PythonModule"].setContents(py_mod)
            else:
                hda_def.addSection("PythonModule", py_mod)
        except Exception:
            # Fallback in weird builds
            hda_def.addSection("PythonModule", py_mod)

        # Tab menu folder
        opts = hda_def.options()
        opts.setTabSubmenuPath("HoudiniGIS")
        hda_def.setOptions(opts)

        # Icon and Help
        hda_def.setIcon("MISC_python")
        hda_def.setHelp("Import ESRI Shapefiles (.shp) with attributes.\\n"
                        "Groups: hgis_exterior / hgis_hole for Boolean holes.\\n"
                        "Part of HoudiniGIS.")

        # Refresh and cleanup
        hou.hda.reloadAllFiles()
        geo.destroy()

except Exception as e:
    import traceback
    traceback.print_exc()
