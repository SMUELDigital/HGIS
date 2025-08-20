# HoudiniGIS PythonModule (embedded in HDA)
# Minimal Shapefile importer using pyshp + optional pyproj

def _is_ccw(coords):
    a = 0.0
    n = len(coords)
    for i in range(n):
        x1,y1 = coords[i]
        x2,y2 = coords[(i+1) % n]
        a += (x1*y2 - x2*y1)
    return (0.5*a) > 0.0

def _make_transformer(prj_path, target_epsg):
    try:
        from pyproj import CRS, Transformer
        with open(prj_path, "r", encoding="utf-8", errors="ignore") as f:
            src_wkt = f.read()
        crs_src = CRS.from_wkt(src_wkt)
        crs_dst = CRS.from_user_input(target_epsg)
        return Transformer.from_crs(crs_src, crs_dst, always_xy=True)
    except Exception:
        return None

def import_shp(geo, parms):
    import os, hou
    try:
        import shapefile  # pyshp
    except Exception:
        raise hou.NodeError("Missing dependency 'pyshp'. Install into $HOME/houdini20.5/python3.11libs (or Windows Documents\\houdini20.5\\python3.11libs).")

    shp_path = parms.get("shp_path","")
    target_epsg = (parms.get("target_epsg","") or "").strip()
    attr_prefix = (parms.get("attr_prefix","") or "shp_")
    import_z = bool(parms.get("import_z", False))
    swap_yz = bool(parms.get("swap_yz", False))
    group_field = (parms.get("group_by","") or "").strip()

    if not shp_path or not os.path.isfile(shp_path):
        raise hou.NodeError("Set a valid .shp file")

    # Optional reprojection if .prj + target_epsg present
    prj_path = os.path.splitext(shp_path)[0] + ".prj"
    transformer = None
    if target_epsg and os.path.isfile(prj_path):
        transformer = _make_transformer(prj_path, target_epsg)

    def tx(x, y):
        if transformer:
            x, y = transformer.transform(x, y)
        return x, y

    def make_pos(x, y, z):
        return hou.Vector3(x, z, y) if swap_yz else hou.Vector3(x, y, z)

    r = shapefile.Reader(shp_path)
    fields = r.fields[1:]  # skip deletion flag
    field_meta = {f[0]: f[1] for f in fields}

    # create primitive attribs up-front
    for name, ftype in field_meta.items():
        hname = attr_prefix + name.lower()
        if hname not in [a.name() for a in geo.primAttribs()]:
            if ftype in ("N","F"):
                geo.addAttrib(hou.attribType.Prim, hname, 0.0)
            else:
                geo.addAttrib(hou.attribType.Prim, hname, "")

    # groups for hole/exterior tagging
    g_ext = geo.findPrimGroup("hgis_exterior") or geo.createPrimGroup("hgis_exterior")
    g_hol = geo.findPrimGroup("hgis_hole")     or geo.createPrimGroup("hgis_hole")

    SHP_POINT_TYPES = {1,11,21,8,18,28}
    SHP_LINE_TYPES  = {3,13,23}
    SHP_POLY_TYPES  = {5,15,25}

    def set_attrs(prim, rec_map):
        for k,ft in field_meta.items():
            hname = attr_prefix + k.lower()
            v = rec_map.get(k)
            if v is None: 
                continue
            if ft in ("N","F"):
                try:
                    vf = float(v)
                    prim.setAttribValue(hname, int(vf) if abs(vf-int(vf))<1e-9 else vf)
                except:
                    prim.setAttribValue(hname, str(v))
            else:
                prim.setAttribValue(hname, str(v))

    for shapeRec in r.iterShapeRecords():
        shp = shapeRec.shape
        rec = shapeRec.record
        rec_map = {r.fields[i+1][0]: rec[i] for i in range(len(r.fields)-1)}

        if shp.shapeType in SHP_POINT_TYPES:
            for c in shp.points:
                x,y = c[0], c[1]
                z = c[2] if (import_z and len(c)>=3) else 0.0
                x,y = tx(x,y)
                p = geo.createPoint()
                p.setPosition(make_pos(x,y,z))
                # push attributes to point for POINT
                for k,ft in field_meta.items():
                    hname = attr_prefix + k.lower()
                    val = rec_map.get(k)
                    if val is None: continue
                    if ft in ("N","F"):
                        try:
                            vf = float(val)
                            p.setAttribValue(hname, int(vf) if abs(vf-int(vf))<1e-9 else vf)
                        except:
                            p.setAttribValue(hname, str(val))
                    else:
                        p.setAttribValue(hname, str(val))

        elif shp.shapeType in SHP_LINE_TYPES:
            pts = shp.points
            parts = list(shp.parts) + [len(pts)]
            for i in range(len(parts)-1):
                seg = pts[parts[i]:parts[i+1]]
                poly = geo.createPolygon()
                poly.setIsClosed(False)
                for c in seg:
                    x,y = tx(c[0], c[1])
                    z = c[2] if (import_z and len(c)>=3) else 0.0
                    pt = geo.createPoint(); pt.setPosition(make_pos(x,y,z))
                    poly.addVertex(pt)
                set_attrs(poly, rec_map)

        elif shp.shapeType in SHP_POLY_TYPES:
            pts = shp.points
            parts = list(shp.parts) + [len(pts)]
            last_prim = None
            for i in range(len(parts)-1):
                ring = pts[parts[i]:parts[i+1]]
                if len(ring) < 3:
                    continue
                ccw = _is_ccw([(p[0],p[1]) for p in ring])
                is_outer = ccw  # adjust if your data uses opposite winding
                poly = geo.createPolygon(); poly.setIsClosed(True)
                for c in ring:
                    x,y = tx(c[0], c[1])
                    z = c[2] if (import_z and len(c)>=3) else 0.0
                    pt = geo.createPoint(); pt.setPosition(make_pos(x,y,z))
                    poly.addVertex(pt)
                set_attrs(poly, rec_map)
                if is_outer:
                    g_ext.add(poly)
                else:
                    g_hol.add(poly)
                last_prim = poly

            if group_field and group_field in rec_map and last_prim is not None:
                gname = f"{group_field}={str(rec_map[group_field]).replace(' ','_')}"
                (geo.findPrimGroup(gname) or geo.createPrimGroup(gname)).add(last_prim)

    # provenance
    if "shp_source" not in [a.name() for a in geo.globalAttribs()]:
        geo.addAttrib(hou.attribType.Global, "shp_source", "")
    import os
    geo.setGlobalAttribValue("shp_source", os.path.basename(shp_path))
