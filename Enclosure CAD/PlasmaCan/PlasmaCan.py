# PlasmaCan v0 - parametric two-tier enclosure for the Plasma Donut
# Run from Fusion: Utilities > Add-Ins > Scripts and Add-Ins > + (add this folder) > Run
# Every key size is a User Parameter: Modify > Change Parameters to edit.
import adsk.core, adsk.fusion, traceback

PARAMS = [  # name, expression, comment
    ('torus_od',      '8 in',     'Glass torus outside diameter'),
    ('torus_tube_d',  '1.5 in',   'Glass tube (minor) diameter - GUESS, confirm'),
    ('base_w',        '12 in',    'Electronics bay width (X)'),
    ('base_d',        '12 in',    'Electronics bay depth (Y)'),
    ('base_h',        '4 in',     'Electronics bay height'),
    ('wall',          '0.125 in', 'Bay wall thickness'),
    ('tube_od',       '10 in',    'Clear acrylic tube OD (stock size)'),
    ('tube_wall',     '0.125 in', 'Acrylic tube wall'),
    ('tube_h',        '8 in',     'Acrylic tube height'),
    ('cradle_lift',   '3 in',     'Gap from deck to torus bottom (keeps metal away from RF)'),
    ('cradle_margin', '0.25 in',  'Cradle lip past torus on each side'),
    ('torus_zc',      'base_h + cradle_lift + torus_tube_d / 2', 'Torus center height (derived)'),
    ('hh_r',          '5.5 in',   'Helmholtz coil radius (spacing = radius)'),
    ('hh_w',          '0.5 in',   'Helmholtz winding bundle size'),
    ('lcd_w',         '2.4 in',   'LCD window width - verify vs NHD-C12832A1Z datasheet'),
    ('lcd_h',         '1.2 in',   'LCD window height - verify'),
]

V = adsk.core.ValueInput.createByString
P3 = adsk.core.Point3D.create
NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
IN = 2.54  # Fusion internal units are cm

def new_comp(root, name):
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ.component

def xy_plane(comp, expr):
    pi = comp.constructionPlanes.createInput()
    pi.setByOffset(comp.xYConstructionPlane, V(expr))
    return comp.constructionPlanes.add(pi)

def annulus(comp, plane, od_expr, id_expr, height_expr, op=NEW):
    sk = comp.sketches.add(plane)
    o = sk.originPoint
    c1 = sk.sketchCurves.sketchCircles.addByCenterRadius(o, 5)
    c2 = sk.sketchCurves.sketchCircles.addByCenterRadius(o, 4)
    d1 = sk.sketchDimensions.addDiameterDimension(c1, P3(6, 6, 0)); d1.parameter.expression = od_expr
    d2 = sk.sketchDimensions.addDiameterDimension(c2, P3(3, 3, 0)); d2.parameter.expression = id_expr
    prof = [p for p in sk.profiles if p.profileLoops.count == 2][0]
    return comp.features.extrudeFeatures.addSimple(prof, V(height_expr), op)

def disk(comp, plane, d_expr, height_expr, op=NEW, direction_neg=False):
    sk = comp.sketches.add(plane)
    c = sk.sketchCurves.sketchCircles.addByCenterRadius(sk.originPoint, 2)
    d = sk.sketchDimensions.addDiameterDimension(c, P3(3, 3, 0)); d.parameter.expression = d_expr
    ext = comp.features.extrudeFeatures
    ei = ext.createInput(sk.profiles.item(0), op)
    dirn = adsk.fusion.ExtentDirections.NegativeExtentDirection if direction_neg else adsk.fusion.ExtentDirections.PositiveExtentDirection
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V(height_expr)), dirn)
    return ext.add(ei)

def normal_of(face):
    ok, n = face.evaluator.getNormalAtPoint(face.pointOnFace)
    return n

def set_appearance(design, body, names):
    lib = None
    for l in adsk.core.Application.get().materialLibraries:
        if 'Appearance' in l.name:
            lib = l; break
    if not lib: return
    for nm in names:
        try:
            a = lib.appearances.itemByName(nm)
            if a:
                body.appearance = design.appearances.itemByName(nm) or design.appearances.addByCopy(a, nm)
                return
        except: pass

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get(); ui = app.userInterface
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.InchDistanceUnits
        for n, e, c in PARAMS:
            design.userParameters.add(n, V(e), 'in', c)
        root = design.rootComponent
        pv = lambda n: design.userParameters.itemByName(n).value  # cm

        # ---------- BASE (electronics bay / Faraday cage) ----------
        base = new_comp(root, 'Base - Electronics Bay')
        sk = base.sketches.add(base.xYConstructionPlane)
        w, d = pv('base_w'), pv('base_d')
        L = sk.sketchCurves.sketchLines.addTwoPointRectangle(P3(-w/2, -d/2, 0), P3(w/2, d/2, 0))
        diag = sk.sketchCurves.sketchLines.addByTwoPoints(L.item(0).startSketchPoint, L.item(2).startSketchPoint)
        diag.isConstruction = True
        sk.geometricConstraints.addMidPoint(sk.originPoint, diag)
        for ln in L:
            s, t = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
            if abs(s.y - t.y) < 1e-6 and s.y < 0:
                dm = sk.sketchDimensions.addDistanceDimension(ln.startSketchPoint, ln.endSketchPoint,
                        adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, P3(0, -d/2 - 2, 0))
                dm.parameter.expression = 'base_w'
            if abs(s.x - t.x) < 1e-6 and s.x > 0:
                dm = sk.sketchDimensions.addDistanceDimension(ln.startSketchPoint, ln.endSketchPoint,
                        adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, P3(w/2 + 2, 0, 0))
                dm.parameter.expression = 'base_d'
        box = base.features.extrudeFeatures.addSimple(sk.profiles.item(0), V('base_h'), NEW)
        body = box.bodies.item(0); body.name = 'Bay shell'
        bottom = [f for f in body.faces if normal_of(f).z < -0.99][0]
        fc = adsk.core.ObjectCollection.create(); fc.add(bottom)
        si = base.features.shellFeatures.createInput(fc, False)
        si.insideThickness = V('wall')
        base.features.shellFeatures.add(si)

        # cable pass-through in the deck
        deck = xy_plane(base, 'base_h')
        disk(base, deck, '1 in', 'wall * 2', CUT, direction_neg=True)

        # front panel cutouts (sketch on the outer -Y face)
        fronts = [f for f in body.faces if normal_of(f).y < -0.99]
        front = min(fronts, key=lambda f: f.pointOnFace.y)
        fs = base.sketches.add(front)
        ms = lambda x, z: fs.modelToSketchSpace(P3(x * IN, -d/2, z * IN))
        hz = pv('base_h') / IN
        lw, lh = pv('lcd_w') / IN, pv('lcd_h') / IN
        lcx, lcz = -2.6, hz * 0.62
        fs.sketchCurves.sketchLines.addTwoPointRectangle(ms(lcx - lw/2, lcz - lh/2), ms(lcx + lw/2, lcz + lh/2))
        holes = [  # (x in, z in, dia in, what)
            (0.3,  lcz, 0.47, 'button 1 (12 mm)'),
            (1.2,  lcz, 0.47, 'button 2 (12 mm)'),
            (-3.3, hz * 0.25, 0.30, 'coil 1 VDD pot'),
            (-1.9, hz * 0.25, 0.30, 'coil 2 VDD pot'),
            (4.0,  hz * 0.5, 0.50, 'ON/OFF switch (guarded)'),
        ]
        for x, z, dia, _ in holes:
            fs.sketchCurves.sketchCircles.addByCenterRadius(ms(x, z), dia * IN / 2)
        profs = adsk.core.ObjectCollection.create()
        for p in fs.profiles: profs.add(p)
        ext = base.features.extrudeFeatures
        ei = ext.createInput(profs, CUT)
        ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V('wall * 2')),
                            adsk.fusion.ExtentDirections.NegativeExtentDirection)
        ext.add(ei)

        # bottom plate
        bot = base.sketches.add(base.xYConstructionPlane)
        bot.sketchCurves.sketchLines.addTwoPointRectangle(P3(-w/2, -d/2, 0), P3(w/2, d/2, 0))
        ei = ext.createInput(bot.profiles.item(0), NEW)
        ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V('wall')),
                            adsk.fusion.ExtentDirections.NegativeExtentDirection)
        bp = ext.add(ei); bp.bodies.item(0).name = 'Bottom plate'

        # ---------- CHAMBER (acrylic tube, cradle, torus) ----------
        ch = new_comp(root, 'Chamber')
        cdeck = xy_plane(ch, 'base_h')
        tube = annulus(ch, cdeck, 'tube_od', 'tube_od - 2 * tube_wall', 'tube_h').bodies.item(0)
        tube.name = 'Acrylic tube'
        set_appearance(design, tube, ['Glass - Light', 'Glass (Clear)', 'Plastic - Transparent Clear', 'Acrylic - Clear'])
        cap = disk(ch, xy_plane(ch, 'base_h + tube_h'), 'tube_od + 0.25 in', '0.25 in').bodies.item(0)
        cap.name = 'Top cap (print)'
        cradle = annulus(ch, cdeck, 'torus_od + 2 * cradle_margin',
                         'torus_od - 2 * torus_tube_d - 2 * cradle_margin',
                         'cradle_lift + torus_tube_d / 2').bodies.item(0)
        cradle.name = 'Cradle pedestal (print)'

        # torus: revolve a circle drawn on XZ about Z
        ts = ch.sketches.add(ch.xZConstructionPlane)
        R = (pv('torus_od') - pv('torus_tube_d')) / 2
        cpt = ts.modelToSketchSpace(P3(R, 0, pv('torus_zc')))
        tc = ts.sketchCurves.sketchCircles.addByCenterRadius(cpt, pv('torus_tube_d') / 2)
        dm = ts.sketchDimensions.addDiameterDimension(tc, P3(cpt.x + 3, cpt.y + 3, 0)); dm.parameter.expression = 'torus_tube_d'
        dh = ts.sketchDimensions.addDistanceDimension(ts.originPoint, tc.centerSketchPoint,
                adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, P3(cpt.x / 2, cpt.y - 2, 0))
        dh.parameter.expression = 'torus_od / 2 - torus_tube_d / 2'
        dv = ts.sketchDimensions.addDistanceDimension(ts.originPoint, tc.centerSketchPoint,
                adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, P3(cpt.x + 4, cpt.y / 2, 0))
        dv.parameter.expression = 'torus_zc'
        rv = ch.features.revolveFeatures
        ri = rv.createInput(ts.profiles.item(0), ch.zConstructionAxis, NEW)
        ri.setAngleExtent(False, V('360 deg'))
        torus = rv.add(ri).bodies.item(0); torus.name = 'Xenon torus (glass)'
        set_appearance(design, torus, ['Glass - Light', 'Glass (Clear)', 'Plastic - Transparent Clear'])

        # saddle the cradle to the torus
        tools = adsk.core.ObjectCollection.create(); tools.add(torus)
        cbi = ch.features.combineFeatures.createInput(cradle, tools)
        cbi.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        cbi.isKeepToolBodies = True
        ch.features.combineFeatures.add(cbi)

        # ---------- HELMHOLTZ placeholders (reach goal) ----------
        hh = new_comp(root, 'Helmholtz Coils (reach)')
        for tag, off in (('lower', 'torus_zc - hh_r / 2 - hh_w / 2'), ('upper', 'torus_zc + hh_r / 2 - hh_w / 2')):
            b = annulus(hh, xy_plane(hh, off), '2 * hh_r + hh_w', '2 * hh_r - hh_w', 'hh_w').bodies.item(0)
            b.name = 'Coil ' + tag

        app.activeViewport.fit()
        ui.messageBox('PlasmaCan v0 built.\nEdit sizes in Modify > Change Parameters.')
    except:
        if ui: ui.messageBox('PlasmaCan failed:\n' + traceback.format_exc())
