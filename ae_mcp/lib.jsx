// lib.jsx: ExtendScript helpers for the AE MCP server (AP-1077). ES3 only (no let/const/arrow/JSON).
// Loaded before the agent's code in every ae_run call. Globals the server defines first:
//   JOB  = the job folder (forward slashes)      DATA = the "data" object of the call (any JSON)
//   path(rel) -> absolute path inside JOB         log(s) -> line in the call's result
// Traps (from the 2026-11-11 AE test): addProperty() invalidates older references in the same group (fetch again);
// point-text origin is unreliable (text() anchors on the ink box); a font can come up as Times on the first
// setValue (text() retries); add keyframes to a parent null only after its children are parented;
// never call app.newProject() (it crashes AE 2025 in -noui with 0xC0000409; the server opens or reuses the project).

function rgb(hex) {
    return [parseInt(hex.substr(1, 2), 16) / 255, parseInt(hex.substr(3, 2), 16) / 255, parseInt(hex.substr(5, 2), 16) / 255];
}
function rgba(hex) { var c = rgb(hex); return [c[0], c[1], c[2], 1]; }

var STAGE = "init"; var KEYN = 0;

// ---------- comps ----------
// Find a comp by name, or create it: comp("MAIN", 1080, 1920, 30, 12.5)
function comp(name, w, h, fps, dur) {
    var i, it;
    for (i = 1; i <= app.project.numItems; i++) {
        it = app.project.item(i);
        if (it instanceof CompItem && it.name === name) return it;
    }
    if (!w) throw new Error("comp not found: " + name);
    return app.project.items.addComp(name, w, h, 1, dur, fps || 30);
}
function layerByName(c, name) {
    for (var i = 1; i <= c.numLayers; i++) if (c.layer(i).name === name) return c.layer(i);
    return null;
}

// ---------- keyframes ----------
// keys: [[t, value, ease], ...]; ease names the segment that STARTS at this key:
// "lin" | "out" (fast start, soft landing) | "in" (soft start, fast end) | "inout" | "hold" | "soft" (gentle inout)
function _infOut(e) { return e === "out" ? 0.1 : e === "in" ? 85 : e === "soft" ? 50 : 70; }
function _infIn(e) { return e === "out" ? 92 : e === "in" ? 0.1 : e === "soft" ? 50 : 70; }
function keys(prop, ks) {
    var i, k, d, dims, a, b; KEYN++;
    try { var nm = prop.name; } catch (eInv) { throw new Error("invalid property in keys() #" + KEYN + " stage " + STAGE); }
    for (i = 0; i < ks.length; i++) prop.setValueAtTime(ks[i][0], ks[i][1]);
    dims = prop.isSpatial ? 1 : ((prop.value instanceof Array) ? prop.value.length : 1);
    for (i = 0; i < ks.length; i++) {
        k = prop.nearestKeyIndex(ks[i][0]);
        var eo = ks[i][2] || "inout", ei = i > 0 ? (ks[i - 1][2] || "inout") : "inout";
        var tin = ei === "lin" ? KeyframeInterpolationType.LINEAR : ei === "hold" ? KeyframeInterpolationType.HOLD : KeyframeInterpolationType.BEZIER;
        var tout = eo === "lin" ? KeyframeInterpolationType.LINEAR : eo === "hold" ? KeyframeInterpolationType.HOLD : KeyframeInterpolationType.BEZIER;
        if (i === 0) tin = (tout === KeyframeInterpolationType.HOLD) ? KeyframeInterpolationType.LINEAR : tout;
        prop.setInterpolationTypeAtKey(k, tin, tout);
        if (tin === KeyframeInterpolationType.BEZIER || tout === KeyframeInterpolationType.BEZIER) {
            a = []; b = [];
            for (d = 0; d < dims; d++) { a.push(new KeyframeEase(0, _infIn(ei))); b.push(new KeyframeEase(0, _infOut(eo))); }
            try { prop.setTemporalEaseAtKey(k, a, b); } catch (e1) { log("ease fail " + prop.name + ": " + e1.toString()); }
        }
        if (prop.isSpatial) {
            try {
                prop.setSpatialAutoBezierAtKey(k, false);
                var z = []; for (d = 0; d < prop.value.length; d++) z.push(0);
                prop.setSpatialTangentsAtKey(k, z, z);
            } catch (e2) {}
        }
    }
    return prop;
}
function tr(layer, name) {
    var map = { pos: "ADBE Position", scale: "ADBE Scale", rot: "ADBE Rotate Z", op: "ADBE Opacity", anchor: "ADBE Anchor Point" };
    return layer.property("ADBE Transform Group").property(map[name]);
}
function span(layer, t0, t1) { layer.inPoint = t0; layer.outPoint = t1; return layer; }

// ---------- effects ----------
function fx(layer, matchName) { return layer.property("ADBE Effect Parade").addProperty(matchName); }
function blurFx(layer, ks) {
    var e = fx(layer, "ADBE Gaussian Blur 2");
    try { e.property("ADBE Gaussian Blur 2-0003").setValue(1); } catch (x) {}   // repeat edge pixels
    if (ks.length === 1) e.property("ADBE Gaussian Blur 2-0001").setValue(ks[0]);
    else keys(e.property("ADBE Gaussian Blur 2-0001"), ks);
    return e;
}
function glowFx(layer, radius, intensity, threshold) {
    var e = fx(layer, "ADBE Glo2");
    e.property("ADBE Glo2-0002").setValue(threshold === undefined ? 55 : threshold);
    e.property("ADBE Glo2-0003").setValue(radius);
    e.property("ADBE Glo2-0004").setValue(intensity);
    return e;
}
// Motion blur on a layer (and switched on for its comp).
function motionBlur(layer) { layer.motionBlur = true; layer.containingComp.motionBlur = true; return layer; }

// ---------- layers ----------
function solid(c, hex, name, t0, t1) {
    var L = c.layers.addSolid(rgb(hex), name, c.width, c.height, 1, c.duration);
    return span(L, t0, t1);
}
function adjustment(c, name, t0, t1) {
    var L = c.layers.addSolid([1, 1, 1], name, c.width, c.height, 1, c.duration);
    L.adjustmentLayer = true;
    return span(L, t0, t1);
}
function nullAt(c, name, x, y, t0, t1) {
    var L = c.layers.addNull(c.duration);
    L.name = name;
    tr(L, "anchor").setValue([50, 50]);
    tr(L, "pos").setValue([x, y]);
    return span(L, t0, t1);
}
// rounded rectangle / ellipse shape layer centred on (x, y)
function shapeRect(c, name, x, y, w, h, radius, fillHex, t0, t1, strokeHex, strokeW) {
    var L = c.layers.addShape(); L.name = name;
    var g = L.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
    var v = g.property("ADBE Vectors Group");
    var r = v.addProperty("ADBE Vector Shape - Rect");
    r.property("ADBE Vector Rect Size").setValue([w, h]);
    r.property("ADBE Vector Rect Roundness").setValue(radius);
    if (strokeHex) {
        var s = v.addProperty("ADBE Vector Graphic - Stroke");
        s.property("ADBE Vector Stroke Color").setValue(rgba(strokeHex));
        s.property("ADBE Vector Stroke Width").setValue(strokeW || 4);
    }
    if (fillHex) v.addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(rgba(fillHex));
    tr(L, "anchor").setValue([0, 0]);
    tr(L, "pos").setValue([x, y]);
    return span(L, t0, t1);
}
function rectSize(L) {
    return L.property("ADBE Root Vectors Group").property(1).property("ADBE Vectors Group").property("ADBE Vector Shape - Rect").property("ADBE Vector Rect Size");
}
function shapeEllipse(c, name, x, y, d, fillHex, t0, t1) {
    var L = c.layers.addShape(); L.name = name;
    var g = L.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
    var v = g.property("ADBE Vectors Group");
    v.addProperty("ADBE Vector Shape - Ellipse").property("ADBE Vector Ellipse Size").setValue([d, d]);
    v.addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(rgba(fillHex));
    tr(L, "anchor").setValue([0, 0]);
    tr(L, "pos").setValue([x, y]);
    return span(L, t0, t1);
}

// ---------- text ----------
// o: {font (PostScript name), size, color, just: "l"|"c"|"r", tracking, leading, x, y, anchor: "c"|"base", name}
function text(c, str, o, t0, t1) {
    var L = c.layers.addText(str);
    var sp = L.property("ADBE Text Properties").property("ADBE Text Document");
    var d = sp.value;
    d.resetCharStyle(); d.resetParagraphStyle();
    d.font = o.font; d.fontSize = o.size; d.applyFill = true; d.fillColor = rgb(o.color); d.applyStroke = false;
    d.tracking = o.tracking || 0;
    d.justification = o.just === "l" ? ParagraphJustification.LEFT_JUSTIFY : o.just === "r" ? ParagraphJustification.RIGHT_JUSTIFY : ParagraphJustification.CENTER_JUSTIFY;
    if (o.leading) { d.autoLeading = false; d.leading = o.leading; }
    sp.setValue(d);
    var got = sp.value.font;
    if (got !== o.font) { var d2 = sp.value; d2.font = o.font; d2.fontSize = o.size; sp.setValue(d2); got = sp.value.font; }
    if (got !== o.font) log("FONT MISMATCH want " + o.font + " got " + got);
    var r = L.sourceRectAtTime(0, false);
    // anchor "base": position = (left edge | right edge | centre) of the ink box on the baseline
    if (o.anchor === "base") tr(L, "anchor").setValue([o.just === "r" ? r.left + r.width : o.just === "l" ? r.left : r.left + r.width / 2, 0]);
    else tr(L, "anchor").setValue([r.left + r.width / 2, r.top + r.height / 2]);
    tr(L, "pos").setValue([o.x, o.y]);
    L.name = o.name || str.substr(0, 24);
    return span(L, t0, t1);
}
function textRect(L) { return L.sourceRectAtTime(L.inPoint, false); }

// Per-unit reveal: units "chars" | "words"; blur/opacity/offset y; t0..t1 is the sweep.
function revealIn(L, unit, t0, t1, o) {
    o = o || {};
    var an = L.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator");
    var p = an.property("ADBE Text Animator Properties");
    p.addProperty("ADBE Text Opacity").setValue(0);
    if (o.blur !== 0) p.addProperty("ADBE Text Blur").setValue([o.blur || 28, o.blur || 28]);
    if (o.dy) p.addProperty("ADBE Text Position 3D").setValue([0, o.dy, 0]);
    if (o.scale) p.addProperty("ADBE Text Scale 3D").setValue([o.scale, o.scale, 100]);
    if (o.tracking) p.addProperty("ADBE Text Tracking Amount").setValue(o.tracking);
    var sel = an.property("ADBE Text Selectors").addProperty("ADBE Text Selector");
    var adv = sel.property("ADBE Text Range Advanced");
    adv.property("ADBE Text Range Type2").setValue(unit === "words" ? 3 : 2);
    adv.property("ADBE Text Selector Smoothness").setValue(o.smooth === undefined ? 100 : o.smooth);
    keys(sel.property("ADBE Text Percent Offset"), [[t0, 0, o.ease || "out"], [t1, 100]]);
    return an;
}
// Whole-layer exit: blur up and fade.
function exitBlur(L, t0, t1, dy) {
    var e = blurFx(L, [[t0, 0, "in"], [t1, 40]]);
    keys(tr(L, "op"), [[t0, 100, "in"], [t1, 0]]);
    if (dy) { var p = tr(L, "pos").value; keys(tr(L, "pos"), [[t0, [p[0], p[1]], "in"], [t1, [p[0], p[1] + dy]]]); }
    return e;
}

// ---------- footage ----------
// Import a file once per call. `rel` is relative to JOB (or an absolute path inside JOB).
var _footage = {};
function footage(rel) {
    var p = path(rel);
    if (_footage[p]) return _footage[p];
    var i, it;
    for (i = 1; i <= app.project.numItems; i++) {           // already in the saved project
        it = app.project.item(i);
        if (it instanceof FootageItem && it.file && it.file.fsName.replace(/\\/g, "/").toLowerCase() === p.toLowerCase()) { _footage[p] = it; return it; }
    }
    var f = new File(p);
    if (!f.exists) throw new Error("file missing: " + p);
    it = app.project.importFile(new ImportOptions(f));
    _footage[p] = it;
    return it;
}
function image(c, rel, x, y, mode, w, h, t0, t1) {     // mode "cover" | "contain" | "width"
    var it = footage(rel), L = c.layers.add(it);
    var s = mode === "contain" ? Math.min(w / it.width, h / it.height) : mode === "width" ? w / it.width : Math.max(w / it.width, h / it.height);
    tr(L, "scale").setValue([s * 100, s * 100]);
    tr(L, "pos").setValue([x, y]);
    return span(L, t0, t1);
}

// ---------- masks ----------
function roundRectShape(cx, cy, w, h, r) {
    r = Math.min(r, w / 2, h / 2);
    var x0 = cx - w / 2, x1 = cx + w / 2, y0 = cy - h / 2, y1 = cy + h / 2, k = 0.5523 * r;
    var s = new Shape();
    s.vertices = [[x0 + r, y0], [x1 - r, y0], [x1, y0 + r], [x1, y1 - r], [x1 - r, y1], [x0 + r, y1], [x0, y1 - r], [x0, y0 + r]];
    s.inTangents = [[-k, 0], [0, 0], [0, -k], [0, 0], [k, 0], [0, 0], [0, k], [0, 0]];
    s.outTangents = [[0, 0], [k, 0], [0, 0], [0, k], [0, 0], [-k, 0], [0, 0], [0, -k]];
    s.closed = true;
    return s;
}
function addMask(L, shape, feather) {
    var m = L.property("ADBE Mask Parade").addProperty("ADBE Mask Atom");
    m.property("ADBE Mask Shape").setValue(shape);
    if (feather) m.property("ADBE Mask Feather").setValue([feather, feather]);
    return m;
}
