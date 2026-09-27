# Little Light — stylized 3D short film (~42 s, no dialogue)
# A tiny robot with a glowing blue eye looks after a wilted sprout on a rainy day.
# Real-time 3D (WebGL2, no extra libraries). Run: streamlit run little_light.py  (no API key needed)
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Little Light", page_icon="🤖", layout="wide")
st.markdown("""
<style>
.stApp { background: #09080a; color: #f1ebe2; }
.stApp label, .stApp p, .stApp span, [data-testid="stWidgetLabel"] *, [data-testid="stMarkdownContainer"] *,
header[data-testid="stHeader"] * { color: #f1ebe2 !important; }
header[data-testid="stHeader"] { background: transparent; }
</style>
""", unsafe_allow_html=True)

st.title("Little Light")
size = st.radio("Video size", ["TikTok 9:16", "YouTube 16:9"], horizontal=True)
FORMAT = "916" if size.startswith("TikTok") else "169"

HTML_ANIMATION = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Little Light</title>
<style>
  [hidden] { display: none !important; }
  :root { color-scheme: dark; --bg: #09080a; --panel: #151318; --garis: #28252c; --teks: #f1ebe2; --redup: #9d968d; --aksen: #7fd4ff; }
  html, body { background: var(--bg); color: var(--teks); }
  body { margin: 0; font-family: system-ui, -apple-system, "Segoe UI", sans-serif; padding: 16px 16px 24px; }
  .wadah { width: min(100%, 1100px, calc((100vh - 150px) * 16 / 9)); min-width: 260px; margin: 0 auto; display: flex; flex-direction: column; gap: 10px; }
  .v916 .wadah { width: min(100%, 460px, calc((100vh - 150px) * 9 / 16)); }
  .atas { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; justify-content: space-between; }
  h1 { margin: 0; font: 600 22px/1 system-ui, sans-serif; letter-spacing: .01em; }
  .pilih { display: inline-flex; background: var(--panel); border-radius: 999px; padding: 3px; box-shadow: inset 0 0 0 1px var(--garis); }
  .pilih button { font: 600 13px/1 system-ui, sans-serif; color: var(--redup); background: none; border: 0; border-radius: 999px; padding: 8px 12px; cursor: pointer; }
  .pilih button[aria-pressed="true"] { background: var(--teks); color: #111; }
  .panggung { position: relative; width: 100%; aspect-ratio: 16 / 9; border-radius: 10px; overflow: hidden; background: #000; box-shadow: 0 0 0 1px var(--garis); }
  .v916 .panggung { aspect-ratio: 9 / 16; }
  canvas { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
  .mulai { position: absolute; inset: 0; display: grid; place-content: center; background: rgba(0,0,0,.4); }
  .mulai button { font: 600 16px/1 system-ui, sans-serif; background: var(--teks); color: #141210; border: 0; border-radius: 999px; padding: 14px 26px; cursor: pointer; }
  .kontrol { display: flex; gap: 10px; align-items: center; }
  .ikon { width: 38px; height: 38px; border-radius: 50%; border: 0; background: var(--panel); color: var(--teks); box-shadow: inset 0 0 0 1px var(--garis); cursor: pointer; font-size: 14px; flex: none; }
  .bar { flex: 1; height: 5px; border-radius: 3px; background: var(--garis); cursor: pointer; position: relative; }
  .bar div { position: absolute; inset: 0 auto 0 0; width: 0; border-radius: 3px; background: var(--aksen); }
  .waktu { font: 500 12px system-ui, sans-serif; color: var(--redup); font-variant-numeric: tabular-nums; min-width: 76px; text-align: right; }
  .galat { position: absolute; inset: 0; display: grid; place-content: center; text-align: center; padding: 24px; color: var(--redup); font-size: 14px; }
  button:focus-visible { outline: 2px solid var(--teks); outline-offset: 2px; }
</style></head><body>
<div class="wadah">
  <div class="atas">
    <h1>Little Light</h1>
    <div class="pilih" role="group" aria-label="Video size">
      <button data-format="916" aria-pressed="true">TikTok 9:16</button>
      <button data-format="169" aria-pressed="false">YouTube 16:9</button>
    </div>
  </div>
  <div class="panggung">
    <canvas id="gl" aria-label="Stylized 3D short film: a little robot with a glowing blue eye looks after a wilted sprout on a rainy day until the sun comes out"></canvas>
    <canvas id="teks" aria-hidden="true"></canvas>
    <div class="mulai" id="mulai"><button id="bMulai">▶ Play (sound on)</button></div>
    <div class="galat" id="galat" hidden>This film needs WebGL2. Please open it in a recent Chrome, Edge, Firefox or Safari.</div>
  </div>
  <div class="kontrol">
    <button class="ikon" id="bMain" aria-label="Play">▶</button>
    <button class="ikon" id="bUlang" aria-label="Restart">↺</button>
    <div class="bar" id="bar" role="slider" aria-label="Position" tabindex="0"><div id="isi"></div></div>
    <span class="waktu" id="waktu">0.0 / 50.0</span>
  </div>
</div>
<script>
(() => {
'use strict';
const KONFIG_AWAL = { format: '916' };
// =====================================================================
//  MINI 3D ENGINE (WebGL2, no libraries)
//  soft-shadowed key light + point lights + hemisphere ambient + rim,
//  HDR -> bloom + god rays -> ACES tone map, grade, vignette, grain
// =====================================================================
const M4 = {
  id: () => { const m = new Float32Array(16); m[0] = m[5] = m[10] = m[15] = 1; return m; },
  mul(a, b) { const o = new Float32Array(16); for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) { let s = 0; for (let k = 0; k < 4; k++) s += a[k * 4 + r] * b[c * 4 + k]; o[c * 4 + r] = s; } return o; },
  persp(fovy, asp, n, f) { const t = 1 / Math.tan(fovy / 2), m = new Float32Array(16); m[0] = t / asp; m[5] = t; m[10] = (f + n) / (n - f); m[11] = -1; m[14] = 2 * f * n / (n - f); return m; },
  ortho(l, r, b, t, n, f) { const m = M4.id(); m[0] = 2 / (r - l); m[5] = 2 / (t - b); m[10] = -2 / (f - n); m[12] = -(r + l) / (r - l); m[13] = -(t + b) / (t - b); m[14] = -(f + n) / (f - n); return m; },
  lookAt(e, c, up) {
    let zx = e[0] - c[0], zy = e[1] - c[1], zz = e[2] - c[2]; let l = Math.hypot(zx, zy, zz); zx /= l; zy /= l; zz /= l;
    let xx = up[1] * zz - up[2] * zy, xy = up[2] * zx - up[0] * zz, xz = up[0] * zy - up[1] * zx; l = Math.hypot(xx, xy, xz); xx /= l; xy /= l; xz /= l;
    const yx = zy * xz - zz * xy, yy = zz * xx - zx * xz, yz = zx * xy - zy * xx;
    const m = new Float32Array(16); m[0] = xx; m[1] = yx; m[2] = zx; m[4] = xy; m[5] = yy; m[6] = zy; m[8] = xz; m[9] = yz; m[10] = zz;
    m[12] = -(xx * e[0] + xy * e[1] + xz * e[2]); m[13] = -(yx * e[0] + yy * e[1] + yz * e[2]); m[14] = -(zx * e[0] + zy * e[1] + zz * e[2]); m[15] = 1; return m;
  },
  trs(t, r, s) { // rotation order: Y * X * Z
    const [x, y, z] = r, cx = Math.cos(x), sx = Math.sin(x), cy = Math.cos(y), sy = Math.sin(y), cz = Math.cos(z), sz = Math.sin(z);
    const m00 = cy * cz + sy * sx * sz, m01 = -cy * sz + sy * sx * cz, m02 = sy * cx;
    const m10 = cx * sz, m11 = cx * cz, m12 = -sx;
    const m20 = -sy * cz + cy * sx * sz, m21 = sy * sz + cy * sx * cz, m22 = cy * cx;
    const m = new Float32Array(16);
    m[0] = m00 * s[0]; m[1] = m10 * s[0]; m[2] = m20 * s[0];
    m[4] = m01 * s[1]; m[5] = m11 * s[1]; m[6] = m21 * s[1];
    m[8] = m02 * s[2]; m[9] = m12 * s[2]; m[10] = m22 * s[2];
    m[12] = t[0]; m[13] = t[1]; m[14] = t[2]; m[15] = 1; return m;
  },
  normal3(m) { // inverse-transpose of upper 3x3
    const a = m[0], b = m[1], c = m[2], d = m[4], e = m[5], f = m[6], g = m[8], h = m[9], i = m[10];
    const A = e * i - f * h, B = -(d * i - f * g), C = d * h - e * g, det = a * A + b * B + c * C || 1e-9;
    return new Float32Array([A / det, B / det, C / det, -(b * i - c * h) / det, (a * i - c * g) / det, -(a * h - b * g) / det, (b * f - c * e) / det, -(a * f - c * d) / det, (a * e - b * d) / det]);
  },
  xf(m, p) { const x = p[0], y = p[1], z = p[2], w = m[3] * x + m[7] * y + m[11] * z + m[15]; return [(m[0] * x + m[4] * y + m[8] * z + m[12]) / w, (m[1] * x + m[5] * y + m[9] * z + m[13]) / w, (m[2] * x + m[6] * y + m[10] * z + m[14]) / w]; },
};

// ---------- geometry (arrays: pos, nor, uv, idx)
const GEO = {
  // rounded box: subdivided cube pushed out from an inner box -> perfectly smooth bevels; r = min half-size gives a sphere
  roundBox(w, h, d, r, seg = 8) {
    const hx = w / 2, hy = h / 2, hz = d / 2; r = Math.min(r, hx, hy, hz);
    const ix = hx - r, iy = hy - r, iz = hz - r, pos = [], nor = [], uv = [], idx = [];
    const faces = [[0, 1, 2, 1], [0, 1, 2, -1], [1, 2, 0, 1], [1, 2, 0, -1], [2, 0, 1, 1], [2, 0, 1, -1]];
    const ext = [w, h, d];
    for (const [a, b, c, s] of faces) {
      const base = pos.length / 3;
      for (let j = 0; j <= seg; j++) for (let i = 0; i <= seg; i++) {
        const p = [0, 0, 0]; p[a] = (i / seg * 2 - 1) * (s > 0 ? 1 : -1); p[b] = j / seg * 2 - 1; p[c] = s;
        // bias samples toward the edges so bevels get more resolution
        const bend = v => Math.sign(v) * Math.pow(Math.abs(v), .8);
        const q = [bend(p[0]) * hx, bend(p[1]) * hy, bend(p[2]) * hz];
        const inner = [Math.max(-ix, Math.min(ix, q[0])), Math.max(-iy, Math.min(iy, q[1])), Math.max(-iz, Math.min(iz, q[2]))];
        let n = [q[0] - inner[0], q[1] - inner[1], q[2] - inner[2]]; let l = Math.hypot(...n);
        if (l < 1e-6) { n = [0, 0, 0]; n[c] = s; l = 1; }
        n = n.map(v => v / l);
        pos.push(inner[0] + n[0] * r, inner[1] + n[1] * r, inner[2] + n[2] * r); nor.push(...n);
        uv.push((p[a] * .5 + .5) * ext[a], (p[b] * .5 + .5) * ext[b]);
      }
      for (let j = 0; j < seg; j++) for (let i = 0; i < seg; i++) { const k = base + j * (seg + 1) + i; idx.push(k, k + 1, k + seg + 2, k, k + seg + 2, k + seg + 1); }
    }
    return { pos, nor, uv, idx };
  },
  sphere(r, seg = 10) { return GEO.roundBox(2 * r, 2 * r, 2 * r, r, seg); },
  // lathe around Y: profile [[radius, y], ...] bottom->top
  lathe(prof, seg = 32, cap = true) {
    const pos = [], nor = [], uv = [], idx = [], n = prof.length;
    const tan = prof.map((p, i) => { const a = prof[Math.max(0, i - 1)], b = prof[Math.min(n - 1, i + 1)]; const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1; return [dy / l, -dx / l]; });
    let vv = 0;
    for (let i = 0; i < n; i++) {
      if (i) vv += Math.hypot(prof[i][0] - prof[i - 1][0], prof[i][1] - prof[i - 1][1]);
      for (let j = 0; j <= seg; j++) { const a = j / seg * Math.PI * 2, c = Math.cos(a), s = Math.sin(a);
        pos.push(prof[i][0] * c, prof[i][1], prof[i][0] * s); nor.push(tan[i][0] * c, tan[i][1], tan[i][0] * s); uv.push(j / seg * 2 * Math.PI * Math.max(.05, prof[i][0]), vv); }
    }
    for (let i = 0; i < n - 1; i++) for (let j = 0; j < seg; j++) { const k = i * (seg + 1) + j; idx.push(k, k + seg + 1, k + 1, k + 1, k + seg + 1, k + seg + 2); }
    if (cap) for (const [pi, ny] of [[0, -1], [n - 1, 1]]) { if (prof[pi][0] < 1e-4) continue; const c0 = pos.length / 3; pos.push(0, prof[pi][1], 0); nor.push(0, ny, 0); uv.push(0, 0);
      for (let j = 0; j <= seg; j++) { const a = j / seg * Math.PI * 2; pos.push(prof[pi][0] * Math.cos(a), prof[pi][1], prof[pi][0] * Math.sin(a)); nor.push(0, ny, 0); uv.push(Math.cos(a) * prof[pi][0], Math.sin(a) * prof[pi][0]); }
      for (let j = 0; j < seg; j++) ny > 0 ? idx.push(c0, c0 + j + 2, c0 + j + 1) : idx.push(c0, c0 + j + 1, c0 + j + 2); }
    return { pos, nor, uv, idx };
  },
  cyl(r, h, seg = 24) { return GEO.lathe([[r, -h / 2], [r, h / 2]], seg); },
  torus(R, r, seg = 40, sides = 14) {
    const pos = [], nor = [], uv = [], idx = [];
    for (let i = 0; i <= seg; i++) { const u = i / seg * Math.PI * 2; for (let j = 0; j <= sides; j++) { const v = j / sides * Math.PI * 2, cx = Math.cos(u), sx = Math.sin(u), cv = Math.cos(v), sv = Math.sin(v);
      pos.push((R + r * cv) * cx, r * sv, (R + r * cv) * sx); nor.push(cv * cx, sv, cv * sx); uv.push(i / seg, j / sides); } }
    for (let i = 0; i < seg; i++) for (let j = 0; j < sides; j++) { const k = i * (sides + 1) + j; idx.push(k, k + 1, k + sides + 2, k, k + sides + 2, k + sides + 1); }
    return { pos, nor, uv, idx };
  },
  plane(w, h, sx = 1, sy = 1) { // facing +Z, uv 0..1
    const pos = [], nor = [], uv = [], idx = [];
    for (let j = 0; j <= sy; j++) for (let i = 0; i <= sx; i++) { pos.push((i / sx - .5) * w, (j / sy - .5) * h, 0); nor.push(0, 0, 1); uv.push(i / sx, j / sy); }
    for (let j = 0; j < sy; j++) for (let i = 0; i < sx; i++) { const k = j * (sx + 1) + i; idx.push(k, k + 1, k + sx + 2, k, k + sx + 2, k + sx + 1); }
    return { pos, nor, uv, idx };
  },
  // leaf: curved almond shape in XY, bent along Z
  leaf(len, wid, curl = .25, seg = 12) {
    const pos = [], nor = [], uv = [], idx = [];
    for (let j = 0; j <= seg; j++) { const t = j / seg, w = Math.sin(t * Math.PI) * wid * (1 - t * .25);
      for (let i = 0; i <= 4; i++) { const s = i / 4 * 2 - 1; pos.push(s * w, t * len, (s * s) * w * .35 + t * t * curl * len); nor.push(-s * .35, -.2, 1); uv.push(i / 4, t); } }
    for (let j = 0; j < seg; j++) for (let i = 0; i < 4; i++) { const k = j * 5 + i; idx.push(k, k + 1, k + 6, k, k + 6, k + 5); }
    return { pos, nor, uv, idx };
  },
};

// ---------- renderer
function buatRenderer(canvas) {
  const gl = canvas.getContext('webgl2', { antialias: false, alpha: false, premultipliedAlpha: false, preserveDrawingBuffer: true });
  if (!gl) return null;
  const F = !!gl.getExtension('EXT_color_buffer_float'); gl.getExtension('OES_texture_float_linear');
  const HDR = F ? gl.RGBA16F : gl.RGBA8, HDRT = F ? gl.HALF_FLOAT : gl.UNSIGNED_BYTE;
  const SAMPLES = Math.min(4, gl.getParameter(gl.MAX_SAMPLES) || 1);

  function sh(type, src) { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s) + '\n' + src.split('\n').map((l, i) => (i + 1) + ': ' + l).join('\n')); return s; }
  function prog(vs, fs) { const p = gl.createProgram(); gl.attachShader(p, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, fs)); gl.bindAttribLocation(p, 0, 'aP'); gl.bindAttribLocation(p, 1, 'aN'); gl.bindAttribLocation(p, 2, 'aU'); gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p)); const u = {}; const n = gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS);
    for (let i = 0; i < n; i++) { const inf = gl.getActiveUniform(p, i); u[inf.name.replace('[0]', '')] = gl.getUniformLocation(p, inf.name); } return { p, u }; }

  const VS = `#version 300 es
layout(location=0) in vec3 aP; layout(location=1) in vec3 aN; layout(location=2) in vec2 aU;
uniform mat4 uModel, uVP, uLVP; uniform mat3 uNM; uniform float uWave, uT;
out vec3 vW; out vec3 vN; out vec2 vU; out vec4 vL;
void main(){ vec3 p = aP; if (uWave > 0.) p.z += sin(p.y * 6. + uT * 1.3) * uWave * (p.x + .5);
  vec4 w = uModel * vec4(p, 1.); vW = w.xyz; vN = normalize(uNM * aN); vU = aU; vL = uLVP * w; gl_Position = uVP * w; }`;
  const FS = `#version 300 es
precision highp float; precision highp sampler2DShadow;
in vec3 vW; in vec3 vN; in vec2 vU; in vec4 vL; out vec4 o;
uniform vec3 uCol, uEmi, uCam, uSunDir, uSunCol, uSky, uGround, uFogCol, uRim;
uniform float uRough, uSpec, uFogD, uAlpha, uTexK, uTex2Mix, uTexScale, uUnlit, uRimK, uShadowK, uWrap;
uniform vec2 uUVOff;
uniform sampler2D uTex, uTex2; uniform sampler2DShadow uShadow;
uniform vec3 uPL[4]; uniform vec3 uPC[4]; uniform float uPR[4]; uniform int uNPL;
float bayang(){ vec3 p = vL.xyz / vL.w * .5 + .5; if (p.x < 0. || p.x > 1. || p.y < 0. || p.y > 1. || p.z > 1.) return 1.;
  float s = 0.; vec2 ts = vec2(1. / 2048.); float b = .0015;
  for (int i = -2; i <= 2; i++) for (int j = -2; j <= 2; j++) s += texture(uShadow, vec3(p.xy + vec2(i, j) * ts * 1.25, p.z - b));
  return s / 25.; }
void main(){
  vec2 uv = vU * uTexScale + uUVOff;
  vec4 tx = texture(uTex, uv); if (uTex2Mix > 0.) tx = mix(tx, texture(uTex2, uv), uTex2Mix);
  vec3 alb = mix(uCol, uCol * tx.rgb, uTexK); float a = uAlpha * mix(1., tx.a, uTexK);
  if (uUnlit > .5) { o = vec4(alb + uEmi, a); return; }
  vec3 N = normalize(vN); if (!gl_FrontFacing) N = -N; vec3 V = normalize(uCam - vW);
  vec3 L = normalize(-uSunDir); float nl = dot(N, L); float dif = clamp((nl + uWrap) / (1. + uWrap), 0., 1.);
  float sh = mix(1., bayang(), uShadowK); dif *= sh;
  vec3 H = normalize(L + V); float sp = pow(max(dot(N, H), 0.), mix(8., 180., 1. - uRough)) * uSpec * sh * step(0., nl);
  vec3 hemi = mix(uGround, uSky, N.y * .5 + .5);
  vec3 c = alb * (hemi + uSunCol * dif) + uSunCol * sp;
  for (int i = 0; i < 4; i++) { if (i >= uNPL) break; vec3 d = uPL[i] - vW; float r = length(d); vec3 l = d / r; float at = pow(clamp(1. - r / uPR[i], 0., 1.), 2.);
    float dd = clamp((dot(N, l) + uWrap) / (1. + uWrap), 0., 1.); vec3 h = normalize(l + V);
    c += (alb * dd + pow(max(dot(N, h), 0.), mix(8., 180., 1. - uRough)) * uSpec) * uPC[i] * at; }
  float fr = pow(1. - max(dot(N, V), 0.), 3.); c += uRim * fr * uRimK;
  c += uEmi;
  float dist = length(uCam - vW); float fg = 1. - exp(-dist * uFogD); c = mix(c, uFogCol, fg);
  o = vec4(c, a); }`;
  const VS_D = `#version 300 es
layout(location=0) in vec3 aP; uniform mat4 uModel, uLVP; void main(){ gl_Position = uLVP * uModel * vec4(aP, 1.); }`;
  const FS_D = `#version 300 es
precision mediump float; out vec4 o; void main(){ o = vec4(1.); }`;
  const VS_Q = `#version 300 es
out vec2 vU; void main(){ vec2 p = vec2((gl_VertexID << 1) & 2, gl_VertexID & 2); vU = p; gl_Position = vec4(p * 2. - 1., 0., 1.); }`;
  const FS_BRIGHT = `#version 300 es
precision highp float; in vec2 vU; out vec4 o; uniform sampler2D uT; uniform float uTh;
void main(){ vec3 c = texture(uT, vU).rgb; float l = max(max(c.r, c.g), c.b); o = vec4(c * smoothstep(uTh, uTh + .6, l), 1.); }`;
  const FS_BLUR = `#version 300 es
precision highp float; in vec2 vU; out vec4 o; uniform sampler2D uT; uniform vec2 uD;
void main(){ vec3 c = texture(uT, vU).rgb * .227; c += (texture(uT, vU + uD * 1.385).rgb + texture(uT, vU - uD * 1.385).rgb) * .316; c += (texture(uT, vU + uD * 3.231).rgb + texture(uT, vU - uD * 3.231).rgb) * .07; o = vec4(c, 1.); }`;
  const FS_RAYS = `#version 300 es
precision highp float; in vec2 vU; out vec4 o; uniform sampler2D uT; uniform vec2 uLP; uniform float uK;
void main(){ vec2 d = (vU - uLP) / 48.; vec2 p = vU; vec3 c = vec3(0.); float w = 1.; for (int i = 0; i < 48; i++) { c += texture(uT, p).rgb * w; w *= .965; p -= d; } o = vec4(c / 48. * uK, 1.); }`;
  const FS_COMP = `#version 300 es
precision highp float; in vec2 vU; out vec4 o;
uniform sampler2D uC, uB1, uB2, uB3, uR; uniform float uExp, uBloom, uT, uFade, uVig, uSat; uniform vec3 uLift, uGain;
vec3 aces(vec3 x){ return clamp((x * (2.51 * x + .03)) / (x * (2.43 * x + .59) + .14), 0., 1.); }
float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
void main(){ vec3 c = texture(uC, vU).rgb; vec3 b = texture(uB1, vU).rgb * .5 + texture(uB2, vU).rgb * .8 + texture(uB3, vU).rgb * 1.1;
  c += b * uBloom + texture(uR, vU).rgb;
  c = aces(c * uExp);
  float l = dot(c, vec3(.299, .587, .114)); c = mix(vec3(l), c, uSat);
  c = c * uGain + uLift * (1. - c);
  vec2 q = vU - .5; c *= 1. - dot(q, q) * uVig;
  c += (h(vU * 1000. + uT) - .5) * .035;
  c *= uFade; o = vec4(pow(max(c, 0.), vec3(1. / 1.0)), 1.); }`;

  const P = prog(VS, FS), PD = prog(VS_D, FS_D), PB = prog(VS_Q, FS_BRIGHT), PBL = prog(VS_Q, FS_BLUR), PR = prog(VS_Q, FS_RAYS), PC = prog(VS_Q, FS_COMP);
  const vaoKosong = gl.createVertexArray();

  function mesh(g) { const vao = gl.createVertexArray(); gl.bindVertexArray(vao);
    const buf = (d, loc, n) => { const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(d), gl.STATIC_DRAW); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, n, gl.FLOAT, false, 0, 0); };
    buf(g.pos, 0, 3); buf(g.nor, 1, 3); buf(g.uv, 2, 2); const ib = gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ib);
    const big = g.pos.length / 3 > 65535; gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, big ? new Uint32Array(g.idx) : new Uint16Array(g.idx), gl.STATIC_DRAW);
    gl.bindVertexArray(null); return { vao, n: g.idx.length, type: big ? gl.UNSIGNED_INT : gl.UNSIGNED_SHORT }; }
  function tekstur(cv, repeat = true) { const t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t); gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, cv);
    gl.generateMipmap(gl.TEXTURE_2D); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    const w = repeat ? gl.REPEAT : gl.CLAMP_TO_EDGE; gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, w); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, w);
    const an = gl.getExtension('EXT_texture_filter_anisotropic'); if (an) gl.texParameterf(gl.TEXTURE_2D, an.TEXTURE_MAX_ANISOTROPY_EXT, 8); return t; }
  const putih = (() => { const c = document.createElement('canvas'); c.width = c.height = 2; const x = c.getContext('2d'); x.fillStyle = '#fff'; x.fillRect(0, 0, 2, 2); return tekstur(c); })();

  // shadow map
  const SM = 2048, smTex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, smTex); gl.texStorage2D(gl.TEXTURE_2D, 1, gl.DEPTH_COMPONENT24, SM, SM);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_COMPARE_MODE, gl.COMPARE_REF_TO_TEXTURE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_COMPARE_FUNC, gl.LEQUAL);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  const smFB = gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, smFB); gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.DEPTH_ATTACHMENT, gl.TEXTURE_2D, smTex, 0); gl.drawBuffers([gl.NONE]); gl.readBuffer(gl.NONE);

  // render targets
  let RT = null;
  function tex2(w, h) { const t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t); gl.texImage2D(gl.TEXTURE_2D, 0, HDR, w, h, 0, gl.RGBA, HDRT, null);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    const fb = gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, fb); gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, t, 0); return { t, fb, w, h }; }
  function siapRT(w, h) {
    if (RT && RT.w === w && RT.h === h) return;
    const msFB = gl.createFramebuffer(), cRB = gl.createRenderbuffer(), dRB = gl.createRenderbuffer();
    gl.bindRenderbuffer(gl.RENDERBUFFER, cRB); gl.renderbufferStorageMultisample(gl.RENDERBUFFER, SAMPLES, HDR, w, h);
    gl.bindRenderbuffer(gl.RENDERBUFFER, dRB); gl.renderbufferStorageMultisample(gl.RENDERBUFFER, SAMPLES, gl.DEPTH_COMPONENT24, w, h);
    gl.bindFramebuffer(gl.FRAMEBUFFER, msFB); gl.framebufferRenderbuffer(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.RENDERBUFFER, cRB); gl.framebufferRenderbuffer(gl.FRAMEBUFFER, gl.DEPTH_ATTACHMENT, gl.RENDERBUFFER, dRB);
    const hw = Math.max(1, w >> 1), hh = Math.max(1, h >> 1);
    RT = { w, h, msFB, col: tex2(w, h), br: tex2(hw, hh), b1: [tex2(hw, hh), tex2(hw, hh)], b2: [tex2(hw >> 1, hh >> 1), tex2(hw >> 1, hh >> 1)], b3: [tex2(hw >> 2, hh >> 2), tex2(hw >> 2, hh >> 2)], ray: tex2(hw >> 1, hh >> 1) };
  }
  function quad(pr, target, setup) { gl.useProgram(pr.p); gl.bindFramebuffer(gl.FRAMEBUFFER, target ? target.fb : null); gl.viewport(0, 0, target ? target.w : canvas.width, target ? target.h : canvas.height); setup(pr.u); gl.bindVertexArray(vaoKosong); gl.drawArrays(gl.TRIANGLES, 0, 3); }
  function ikat(unit, t) { gl.activeTexture(gl.TEXTURE0 + unit); gl.bindTexture(gl.TEXTURE_2D, t); }

  // ---- draw a frame
  // S = { objek:[{mesh, mat, model}], cam:{pos,target,fov,up}, sun:{dir,col}, sky, ground, fog:{col,d}, pl:[{pos,col,r}], rim, post:{...}, sunTarget, sunSize }
  function gambar(S) {
    const W = canvas.width, H = canvas.height; siapRT(W, H);
    gl.enable(gl.DEPTH_TEST); gl.enable(gl.CULL_FACE);
    // shadow pass
    const sd = S.sun.dir, tc = S.sunTarget || [0, 1, 0], ext = S.sunSize || 6;
    const lv = M4.lookAt([tc[0] - sd[0] * 12, tc[1] - sd[1] * 12, tc[2] - sd[2] * 12], tc, Math.abs(sd[1]) > .95 ? [0, 0, 1] : [0, 1, 0]);
    const LVP = M4.mul(M4.ortho(-ext, ext, -ext, ext, .1, 30), lv);
    gl.bindFramebuffer(gl.FRAMEBUFFER, smFB); gl.viewport(0, 0, SM, SM); gl.clear(gl.DEPTH_BUFFER_BIT); gl.useProgram(PD.p); gl.uniformMatrix4fv(PD.u.uLVP, false, LVP);
    gl.enable(gl.POLYGON_OFFSET_FILL); gl.polygonOffset(1.5, 3); gl.disable(gl.CULL_FACE);
    for (const o of S.objek) { if (o.mat.bayangan === false || o.mat.alpha < 1 || o.mat.unlit) continue; gl.uniformMatrix4fv(PD.u.uModel, false, o.model); gl.bindVertexArray(o.mesh.vao); gl.drawElements(gl.TRIANGLES, o.mesh.n, o.mesh.type, 0); }
    gl.disable(gl.POLYGON_OFFSET_FILL); gl.enable(gl.CULL_FACE);
    // main pass
    gl.bindFramebuffer(gl.FRAMEBUFFER, RT.msFB); gl.viewport(0, 0, W, H);
    gl.clearColor(...S.fog.col, 1); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    const c = S.cam, VP = M4.mul(M4.persp(c.fov, W / H, .05, 60), M4.lookAt(c.pos, c.target, c.up || [0, 1, 0]));
    const u = P.u; gl.useProgram(P.p);
    gl.uniformMatrix4fv(u.uVP, false, VP); gl.uniformMatrix4fv(u.uLVP, false, LVP); gl.uniform3fv(u.uCam, c.pos);
    gl.uniform3fv(u.uSunDir, sd); gl.uniform3fv(u.uSunCol, S.sun.col); gl.uniform3fv(u.uSky, S.sky); gl.uniform3fv(u.uGround, S.ground);
    gl.uniform3fv(u.uFogCol, S.fog.col); gl.uniform1f(u.uFogD, S.fog.d); gl.uniform3fv(u.uRim, S.rim || [0, 0, 0]); gl.uniform1f(u.uT, S.t || 0);
    const pl = S.pl.slice(0, 4); gl.uniform1i(u.uNPL, pl.length);
    if (pl.length) { gl.uniform3fv(u.uPL, pl.flatMap(p => p.pos)); gl.uniform3fv(u.uPC, pl.flatMap(p => p.col)); gl.uniform1fv(u.uPR, pl.map(p => p.r)); }
    ikat(2, smTex); gl.uniform1i(u.uShadow, 2); gl.uniform1i(u.uTex, 0); gl.uniform1i(u.uTex2, 1);
    const gambarObj = o => { const m = o.mat;
      gl.uniformMatrix4fv(u.uModel, false, o.model); gl.uniformMatrix3fv(u.uNM, false, M4.normal3(o.model));
      gl.uniform3fv(u.uCol, m.col); gl.uniform3fv(u.uEmi, m.emi || [0, 0, 0]); gl.uniform1f(u.uRough, m.rough ?? .6); gl.uniform1f(u.uSpec, m.spec ?? .15);
      gl.uniform1f(u.uAlpha, m.alpha ?? 1); gl.uniform1f(u.uUnlit, m.unlit ? 1 : 0); gl.uniform1f(u.uRimK, m.rimK ?? .35); gl.uniform1f(u.uShadowK, m.terimaBayangan === false ? 0 : 1); gl.uniform1f(u.uWrap, m.wrap ?? .35);
      gl.uniform1f(u.uWave, m.wave || 0); ikat(0, m.tex || putih); ikat(1, m.tex2 || putih); gl.uniform1f(u.uTexK, m.tex ? 1 : 0); gl.uniform1f(u.uTex2Mix, m.tex2 ? (m.mix2 || 0) : 0);
      gl.uniform1f(u.uTexScale, m.skala ?? 1); gl.uniform2fv(u.uUVOff, m.uvOff || [0, 0]);
      if (m.duaSisi) gl.disable(gl.CULL_FACE); gl.bindVertexArray(o.mesh.vao); gl.drawElements(gl.TRIANGLES, o.mesh.n, o.mesh.type, 0); if (m.duaSisi) gl.enable(gl.CULL_FACE); };
    const opaque = S.objek.filter(o => !(o.mat.alpha < 1) && !o.mat.aditif), trans = S.objek.filter(o => o.mat.alpha < 1 || o.mat.aditif);
    for (const o of opaque) gambarObj(o);
    gl.enable(gl.BLEND); gl.depthMask(false);
    trans.sort((a, b) => (b.z || 0) - (a.z || 0));
    for (const o of trans) { gl.blendFunc(gl.SRC_ALPHA, o.mat.aditif ? gl.ONE : gl.ONE_MINUS_SRC_ALPHA); gambarObj(o); }
    gl.depthMask(true); gl.disable(gl.BLEND); gl.disable(gl.DEPTH_TEST);
    // resolve MSAA
    gl.bindFramebuffer(gl.READ_FRAMEBUFFER, RT.msFB); gl.bindFramebuffer(gl.DRAW_FRAMEBUFFER, RT.col.fb); gl.blitFramebuffer(0, 0, W, H, 0, 0, W, H, gl.COLOR_BUFFER_BIT, gl.NEAREST);
    // bloom
    const po = S.post;
    quad(PB, RT.br, u => { ikat(0, RT.col.t); gl.uniform1i(u.uT, 0); gl.uniform1f(u.uTh, po.th ?? 1.0); });
    const blur = (src, pair, rad) => { quad(PBL, pair[0], u => { ikat(0, src.t); gl.uniform1i(u.uT, 0); gl.uniform2f(u.uD, rad / pair[0].w, 0); }); quad(PBL, pair[1], u => { ikat(0, pair[0].t); gl.uniform1i(u.uT, 0); gl.uniform2f(u.uD, 0, rad / pair[1].h); }); return pair[1]; };
    const B1 = blur(RT.br, RT.b1, 1.2), B2 = blur(B1, RT.b2, 1.5), B3 = blur(B2, RT.b3, 2);
    // god rays
    const lp = S.rayPos ? M4.xf(VP, S.rayPos) : [0, 0, 0];
    quad(PR, RT.ray, u => { ikat(0, RT.br.t); gl.uniform1i(u.uT, 0); gl.uniform2f(u.uLP, lp[0] * .5 + .5, lp[1] * .5 + .5); gl.uniform1f(u.uK, po.rays || 0); });
    // composite
    quad(PC, null, u => { ikat(0, RT.col.t); ikat(1, B1.t); ikat(2, B2.t); ikat(3, B3.t); ikat(4, RT.ray.t);
      gl.uniform1i(u.uC, 0); gl.uniform1i(u.uB1, 1); gl.uniform1i(u.uB2, 2); gl.uniform1i(u.uB3, 3); gl.uniform1i(u.uR, 4);
      gl.uniform1f(u.uExp, po.exp ?? 1); gl.uniform1f(u.uBloom, po.bloom ?? .6); gl.uniform1f(u.uT, (S.t || 0) % 100); gl.uniform1f(u.uFade, po.fade ?? 1);
      gl.uniform1f(u.uVig, po.vig ?? 1.1); gl.uniform1f(u.uSat, po.sat ?? 1.05); gl.uniform3fv(u.uLift, po.lift || [0, 0, 0]); gl.uniform3fv(u.uGain, po.gain || [1, 1, 1]); });
    return VP;
  }
  return { gl, mesh, tekstur, gambar, HDR: F };
}

// =====================================================================
//  WORLD: procedural textures, the cozy room, the robot, the sprout
// =====================================================================
const hex = h => [parseInt(h.slice(1, 3), 16) / 255, parseInt(h.slice(3, 5), 16) / 255, parseInt(h.slice(5, 7), 16) / 255];
const mixV = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t);
function rngS(s) { return () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function kanvas(w, h, f) { const c = document.createElement('canvas'); c.width = w; c.height = h; f(c.getContext('2d'), w, h); return c; }

// ---------- procedural textures
function buatTekstur(R) {
  const T = {};
  T.lantai = R.tekstur(kanvas(512, 512, (x, w, h) => { const r = rngS(3), pw = 64;
    for (let i = 0; i < w / pw; i++) { const base = [150 + r() * 40, 96 + r() * 25, 58 + r() * 18]; x.fillStyle = `rgb(${base.map(Math.round)})`; x.fillRect(i * pw, 0, pw, h);
      for (let k = 0; k < 40; k++) { x.strokeStyle = `rgba(70,40,20,${.05 + r() * .12})`; x.lineWidth = 1 + r() * 2; x.beginPath(); const xx = i * pw + r() * pw; x.moveTo(xx, 0); for (let y = 0; y <= h; y += 16) x.lineTo(xx + Math.sin(y * .02 + k) * 3, y); x.stroke(); }
      const cut = r() * h; x.fillStyle = 'rgba(40,20,10,.55)'; x.fillRect(i * pw, cut, pw, 2); x.fillRect(i * pw, 0, 2, h); x.fillStyle = 'rgba(255,220,180,.08)'; x.fillRect(i * pw + 2, 0, 2, h); } }));
  T.dinding = R.tekstur(kanvas(256, 256, (x, w, h) => { x.fillStyle = '#e9dcc6'; x.fillRect(0, 0, w, h); const r = rngS(8);
    for (let i = 0; i < 900; i++) { x.fillStyle = `rgba(${r() < .5 ? '120,90,60' : '255,250,240'},${r() * .05})`; x.beginPath(); x.arc(r() * w, r() * h, 1 + r() * 6, 0, 7); x.fill(); } }));
  T.panel = R.tekstur(kanvas(256, 256, (x, w, h) => { x.fillStyle = '#8a5a36'; x.fillRect(0, 0, w, h); const r = rngS(5);
    for (let i = 0; i < 8; i++) { x.fillStyle = `rgba(${r() < .5 ? '60,30,15' : '190,130,80'},.18)`; x.fillRect(i * 32, 0, 32, h); x.fillStyle = 'rgba(40,20,10,.5)'; x.fillRect(i * 32, 0, 2, h); }
    for (let k = 0; k < 60; k++) { x.strokeStyle = `rgba(60,30,15,${r() * .15})`; x.beginPath(); const xx = r() * w; x.moveTo(xx, 0); x.bezierCurveTo(xx + 4, 80, xx - 4, 160, xx + 2, h); x.stroke(); } }));
  T.karpet = R.tekstur(kanvas(512, 512, (x, w, h) => { const cx = w / 2; const warna = ['#b8452e', '#e8b46a', '#f3e6cf', '#8a2f24', '#d9773f', '#f3e6cf', '#b8452e'];
    x.fillStyle = '#f3e6cf'; x.fillRect(0, 0, w, h); warna.forEach((c, i) => { x.fillStyle = c; x.beginPath(); x.arc(cx, cx, cx * (1 - i * .13), 0, 7); x.fill(); });
    x.strokeStyle = 'rgba(255,240,210,.6)'; x.lineWidth = 3; for (let k = 0; k < 24; k++) { const a = k / 24 * Math.PI * 2; x.beginPath(); x.moveTo(cx + Math.cos(a) * cx * .35, cx + Math.sin(a) * cx * .35); x.lineTo(cx + Math.cos(a) * cx * .6, cx + Math.sin(a) * cx * .6); x.stroke(); }
    const r = rngS(2); for (let i = 0; i < 4000; i++) { x.fillStyle = `rgba(${r() < .5 ? '0,0,0' : '255,255,255'},.05)`; x.fillRect(r() * w, r() * h, 2, 2); } }));
  const luar = hujan => kanvas(1024, 640, (x, w, h) => {
    const g = x.createLinearGradient(0, 0, 0, h); if (hujan) { g.addColorStop(0, '#5c6a80'); g.addColorStop(.55, '#8a95a4'); g.addColorStop(1, '#4a5560'); } else { g.addColorStop(0, '#6fa8e0'); g.addColorStop(.55, '#cfe4f2'); g.addColorStop(1, '#8fb87a'); }
    x.fillStyle = g; x.fillRect(0, 0, w, h); const r = rngS(11);
    if (!hujan) { for (let i = 0; i < 7; i++) { const cx = r() * w, cy = h * (.1 + r() * .25); for (let k = 0; k < 9; k++) { x.fillStyle = 'rgba(255,255,255,.85)'; x.beginPath(); x.arc(cx + (k - 4) * 22, cy + Math.sin(k) * 8, 26 + r() * 20, 0, 7); x.fill(); } }
      x.lineWidth = 14; ['#ff6b6b', '#ffb36b', '#ffe66b', '#8be06b', '#6bb8ff', '#9b7bff'].forEach((c, i) => { x.strokeStyle = c; x.globalAlpha = .28; x.beginPath(); x.arc(w * .75, h * .95, 420 - i * 14, Math.PI * 1.05, Math.PI * 1.55); x.stroke(); }); x.globalAlpha = 1; }
    for (let layer = 0; layer < 3; layer++) { const y0 = h * (.52 + layer * .1), col = hujan ? ['#6d7684', '#535c68', '#3b434c'][layer] : ['#7fa88a', '#5d8f5a', '#3f6e3c'][layer];
      x.fillStyle = col; for (let i = 0; i < 14; i++) { const cx = r() * w, rr = 40 + r() * 60 + layer * 20; x.beginPath(); x.arc(cx, y0, rr, 0, 7); x.fill(); } x.fillRect(0, y0, w, h); }
    for (let i = 0; i < 5; i++) { const bx = r() * w, bw = 90 + r() * 60, by = h * .66; x.fillStyle = hujan ? '#4a4e56' : '#e8dcc6'; x.fillRect(bx, by - 60, bw, 70); x.fillStyle = hujan ? '#383c44' : '#b8563e'; x.beginPath(); x.moveTo(bx - 12, by - 60); x.lineTo(bx + bw / 2, by - 105); x.lineTo(bx + bw + 12, by - 60); x.fill();
      x.fillStyle = hujan ? 'rgba(255,200,120,.9)' : 'rgba(70,90,110,.8)'; x.fillRect(bx + 18, by - 40, 18, 18); x.fillRect(bx + bw - 36, by - 40, 18, 18); }
    if (hujan) { x.fillStyle = 'rgba(160,170,185,.35)'; x.fillRect(0, 0, w, h); }
  });
  T.luarHujan = R.tekstur(luar(true), false); T.luarCerah = R.tekstur(luar(false), false);
  T.hujan = R.tekstur(kanvas(256, 512, (x, w, h) => { const r = rngS(4); x.clearRect(0, 0, w, h); x.strokeStyle = 'rgba(220,230,255,.55)';
    for (let i = 0; i < 140; i++) { const xx = r() * w, yy = r() * h, L = 18 + r() * 40; x.lineWidth = .8 + r() * 1.2; x.beginPath(); x.moveTo(xx, yy); x.lineTo(xx - 3, yy + L); x.stroke(); } }));
  T.tetes = R.tekstur(kanvas(512, 512, (x, w, h) => { const r = rngS(9); x.clearRect(0, 0, w, h);
    for (let i = 0; i < 160; i++) { const xx = r() * w, yy = r() * h, rr = 2 + r() * 7; const g = x.createRadialGradient(xx - rr * .3, yy - rr * .3, 0, xx, yy, rr); g.addColorStop(0, 'rgba(255,255,255,.95)'); g.addColorStop(.5, 'rgba(200,215,235,.35)'); g.addColorStop(1, 'rgba(120,140,170,.55)');
      x.fillStyle = g; x.beginPath(); x.ellipse(xx, yy, rr * .8, rr, 0, 0, 7); x.fill(); if (r() < .3) { x.strokeStyle = 'rgba(210,225,245,.35)'; x.lineWidth = rr * .5; x.beginPath(); x.moveTo(xx, yy - rr); x.lineTo(xx + (r() - .5) * 6, yy - rr - 20 - r() * 60); x.stroke(); } } }));
  T.mata = R.tekstur(kanvas(256, 256, (x, w, h) => { const c = w / 2; const g = x.createRadialGradient(c, c, 0, c, c, c); g.addColorStop(0, '#ffffff'); g.addColorStop(.18, '#dff8ff'); g.addColorStop(.42, '#5fd4ff'); g.addColorStop(.75, '#1a7fd0'); g.addColorStop(1, '#0a3a70');
    x.fillStyle = g; x.fillRect(0, 0, w, h); x.strokeStyle = 'rgba(255,255,255,.45)'; x.lineWidth = 3; for (const rr of [.55, .68, .82]) { x.beginPath(); x.arc(c, c, c * rr, 0, 7); x.stroke(); } }), false);
  T.blob = R.tekstur(kanvas(128, 128, (x, w, h) => { const g = x.createRadialGradient(64, 64, 0, 64, 64, 64); g.addColorStop(0, 'rgba(0,0,0,.6)'); g.addColorStop(.6, 'rgba(0,0,0,.25)'); g.addColorStop(1, 'rgba(0,0,0,0)'); x.fillStyle = g; x.fillRect(0, 0, w, h); }), false);
  T.debu = R.tekstur(kanvas(64, 64, (x, w, h) => { const g = x.createRadialGradient(32, 32, 0, 32, 32, 32); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(.4, 'rgba(255,255,255,.4)'); g.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = g; x.fillRect(0, 0, w, h); }), false);
  T.lukisan = [0, 1, 2].map(k => R.tekstur(kanvas(256, 320, (x, w, h) => { const r = rngS(20 + k), g = x.createLinearGradient(0, 0, 0, h);
    const pal = [['#f4c28a', '#e07a5a', '#5a7a9a'], ['#9fd0e8', '#f3e6cf', '#6a9a5a'], ['#f3d6a0', '#c86a4a', '#4a3a5a']][k]; g.addColorStop(0, pal[0]); g.addColorStop(1, pal[1]); x.fillStyle = g; x.fillRect(0, 0, w, h);
    x.fillStyle = pal[2]; x.beginPath(); x.moveTo(0, h); for (let i = 0; i <= 8; i++) x.lineTo(i * w / 8, h * (.6 + r() * .2)); x.lineTo(w, h); x.fill(); x.fillStyle = 'rgba(255,250,230,.9)'; x.beginPath(); x.arc(w * (.3 + r() * .4), h * .3, 22, 0, 7); x.fill(); }), false));
  T.buku = R.tekstur(kanvas(64, 256, (x, w, h) => { const r = rngS(31); let yy = 0; x.fillStyle = '#2a1d14'; x.fillRect(0, 0, w, h); while (yy < h) { const bh = 8 + r() * 12, tinggi = .7 + r() * .3; x.fillStyle = ['#8a3a30', '#3a5a7a', '#c9a36a', '#4a6a4a', '#6a4a7a', '#d8cbb0', '#2e4a5e'][Math.floor(r() * 7)]; x.fillRect(0, yy, w * tinggi, bh - 1); x.fillStyle = 'rgba(255,240,200,.35)'; x.fillRect(w * tinggi * .45, yy + 2, 3, bh - 5); yy += bh; } }));
  return T;
}

// ---------- scene graph
function buatDunia(R) {
  const T = buatTekstur(R), G = {};
  const m = g => R.mesh(g);
  G.kotak = m(GEO.roundBox(1, 1, 1, .02, 2)); G.kotakBulat = m(GEO.roundBox(1, 1, 1, .12, 8)); G.bola = m(GEO.sphere(.5, 10)); G.bidang = m(GEO.plane(1, 1));
  G.silinder = m(GEO.cyl(.5, 1, 28)); G.torus = m(GEO.torus(.5, .12, 48, 16)); G.daun = m(GEO.leaf(1, .42, .35, 14)); G.tirai = m(GEO.plane(1, 1, 10, 24));
  G.pot = m(GEO.lathe([[0, 0], [.33, 0], [.4, .05], [.46, .62], [.52, .66], [.53, .78], [.46, .8], [0, .8]], 32, false));
  G.tanah = m(GEO.cyl(.44, .04, 28));
  G.kap = m(GEO.lathe([[.08, .5], [.14, .45], [.35, .1], [.5, 0], [.48, -.02], [.33, .08], [.12, .43], [.06, .48]], 36, false));
  G.mug = m(GEO.lathe([[0, 0], [.38, 0], [.42, .05], [.42, 1], [.36, 1], [.36, .08], [0, .08]], 28, false));
  G.kepalaRobot = m(GEO.roundBox(1, 1, 1, .36, 10)); G.badanRobot = m(GEO.roundBox(1, 1, 1, .28, 9)); G.kapsul = m(GEO.roundBox(1, 1, 1, .5, 8));
  G.tutupMata = m(GEO.lathe([[0, 0], [.5, 0], [.5, .06], [.42, .08], [0, .1]], 36, false));

  const mat = (col, o = {}) => ({ col: typeof col === 'string' ? hex(col) : col, ...o });
  const MAT = {
    lantai: mat('#ffffff', { tex: T.lantai, skala: .9, rough: .45, spec: .25 }), dinding: mat('#ffffff', { tex: T.dinding, skala: .6, rough: .9, spec: .02 }),
    panel: mat('#ffffff', { tex: T.panel, skala: 1, rough: .5, spec: .12 }), kayu: mat('#8a5a36', { rough: .5, spec: .15 }), kayuGelap: mat('#5a3a24', { rough: .5, spec: .12 }), kayuMuda: mat('#b98a5a', { rough: .55, spec: .12 }),
    karpet: mat('#ffffff', { tex: T.karpet, rough: .95, spec: 0 }), kain: mat('#c9674a', { rough: .95, spec: .02, wave: .02, duaSisi: true }), kainKrem: mat('#efe2c8', { rough: .95, spec: .02 }),
    luar: mat('#ffffff', { tex: T.luarHujan, tex2: T.luarCerah, mix2: 0, unlit: true, bayangan: false }), hujan: mat('#ffffff', { tex: T.hujan, unlit: true, alpha: .7, bayangan: false }),
    kaca: mat('#cfe0f0', { tex: T.tetes, alpha: .35, unlit: false, spec: .8, rough: .05, rimK: .5, bayangan: false }),
    robotKrem: mat('#e3b56a', { rough: .35, spec: .45, rimK: .4 }), robotLogam: mat('#7c8790', { rough: .2, spec: 1.1, rimK: .5 }), robotOranye: mat('#e0763a', { rough: .4, spec: .5 }),
    robotGelap: mat('#2c2f36', { rough: .25, spec: .9 }), mata: mat('#ffffff', { tex: T.mata, unlit: true, bayangan: false }), antena: mat('#ff9a4a', { unlit: true }),
    pot: mat('#c8653e', { rough: .8, spec: .05 }), tanah: mat('#3a2618', { rough: 1, spec: 0 }), batang: mat('#5f8f3a', { rough: .6, spec: .1 }), daun: mat('#6aa84a', { rough: .5, spec: .25, duaSisi: true, wrap: .7 }),
    kelopak: mat('#ffd65a', { rough: .5, spec: .2, duaSisi: true, wrap: .8 }), putik: mat('#f08a3a', { rough: .6 }),
    lampu: mat('#fff2d0', { unlit: true, bayangan: false }), kap: mat('#e8b46a', { rough: .7, spec: .1, duaSisi: true, wrap: .8 }), tali: mat('#2a2420', { rough: .8 }),
    mug: mat('#f2eee6', { rough: .3, spec: .5 }), blob: mat('#000000', { tex: T.blob, alpha: 1, unlit: true, bayangan: false }), debu: mat('#fff0d0', { tex: T.debu, unlit: true, alpha: .9, aditif: true, bayangan: false }),
    buku: mat('#ffffff', { tex: T.buku, rough: .8, spec: .05 }), bingkai: mat('#3a2a1c', { rough: .5, spec: .2 }), tanamanBesar: mat('#3f7a3a', { rough: .6, spec: .2, duaSisi: true, wrap: .6 }), potBesar: mat('#d8cbb0', { rough: .6, spec: .2 }),
    lukisan: T.lukisan.map(t => mat('#ffffff', { tex: t, rough: .7, spec: .05 })),
  };
  MAT.blob.alpha = .99;

  // node helper
  const N = (mesh, mt, t = [0, 0, 0], s = [1, 1, 1], r = [0, 0, 0], parent = null) => ({ mesh, mat: mt, t, s, r, parent, vis: true });
  const statis = [];
  const S = (...a) => { const n = N(...a); statis.push(n); return n; };

  // ---- room (floor y=0, back wall z=-2.5, left wall x=-2.6, window centered x=.45)
  S(G.kotak, MAT.lantai, [0, -.05, -.2], [5.4, .1, 5]);
  const WX = .45, WW = 1.5, WY0 = .95, WY1 = 2.35, WZ = -2.5, TH = .16;
  S(G.kotak, MAT.dinding, [(-2.7 + WX - WW / 2) / 2, 1.5, WZ], [WX - WW / 2 + 2.7, 3, TH]);
  S(G.kotak, MAT.dinding, [(2.7 + WX + WW / 2) / 2, 1.5, WZ], [2.7 - WX - WW / 2, 3, TH]);
  S(G.kotak, MAT.dinding, [WX, WY0 / 2, WZ], [WW, WY0, TH]); S(G.kotak, MAT.dinding, [WX, (3 + WY1) / 2, WZ], [WW, 3 - WY1, TH]);
  S(G.kotak, MAT.dinding, [-2.6, 1.5, -.2], [TH, 3, 5]);
  S(G.kotak, MAT.dinding, [0, 3.02, -.2], [5.4, .08, 5]);
  S(G.kotak, MAT.panel, [-.05, .42, WZ + .09], [5.2, .84, .03]); S(G.kotak, MAT.kayuGelap, [-.05, .85, WZ + .1], [5.2, .05, .06]);
  S(G.kotak, MAT.panel, [-2.51, .42, -.2], [.03, .84, 5]); S(G.kotak, MAT.kayuGelap, [-2.5, .85, -.2], [.06, .05, 5]);
  S(G.kotak, MAT.kayuGelap, [-.05, .04, WZ + .1], [5.2, .08, .05]);
  // window frame, mullions, sill
  const fr = .07;
  S(G.kotak, MAT.kayu, [WX, WY0, WZ + .02], [WW + .12, fr, TH + .08]); S(G.kotak, MAT.kayu, [WX, WY1, WZ + .02], [WW + .12, fr, TH + .08]);
  S(G.kotak, MAT.kayu, [WX - WW / 2, (WY0 + WY1) / 2, WZ + .02], [fr, WY1 - WY0, TH + .08]); S(G.kotak, MAT.kayu, [WX + WW / 2, (WY0 + WY1) / 2, WZ + .02], [fr, WY1 - WY0, TH + .08]);
  S(G.kotak, MAT.kayu, [WX, (WY0 + WY1) / 2, WZ], [.045, WY1 - WY0, .06]); S(G.kotak, MAT.kayu, [WX, WY0 + (WY1 - WY0) * .62, WZ], [WW, .045, .06]);
  S(G.kotak, MAT.kayuMuda, [WX, WY0 - .02, WZ + .2], [WW + .3, .05, .36]);
  // outside world, rain and glass
  const luar = S(G.bidang, MAT.luar, [WX + .2, 1.7, -4.6], [5.2, 3.25, 1]);
  const hujanN = S(G.bidang, MAT.hujan, [WX, 1.65, -2.95], [2.4, 2.2, 1]);
  const kacaN = S(G.bidang, MAT.kaca, [WX, (WY0 + WY1) / 2, WZ + .01], [WW, WY1 - WY0, 1]);
  // curtains
  const tiraiL = S(G.tirai, MAT.kain, [WX - WW / 2 - .22, 1.6, WZ + .16], [.5, 1.9, 1]); const tiraiR = S(G.tirai, MAT.kain, [WX + WW / 2 + .22, 1.6, WZ + .16], [.5, 1.9, 1]);
  S(G.silinder, MAT.kayuGelap, [WX, 2.58, WZ + .16], [.025, 2.3, .025], [0, 0, Math.PI / 2]);
  // rug, pendant lamp, table + mug, shelf + books, frames, big plant, cushion
  S(G.silinder, MAT.karpet, [-.7, .005, -.9], [2.2, .01, 2.2]);
  S(G.silinder, MAT.tali, [-.55, 2.6, -.9], [.012, .8, .012]); S(G.kap, MAT.kap, [-.55, 1.98, -.9], [.55, .5, .55]); const bohlam = S(G.bola, MAT.lampu, [-.55, 2.08, -.9], [.09, .09, .09]);
  S(G.kotak, MAT.kayu, [-1.7, .42, -.4], [.7, .05, .5]); for (const [x, z] of [[-1.98, -.6], [-1.42, -.6], [-1.98, -.2], [-1.42, -.2]]) S(G.silinder, MAT.kayuGelap, [x, .2, z], [.04, .4, .04]);
  S(G.mug, MAT.mug, [-1.62, .445, -.35], [.09, .1, .09]); S(G.torus, MAT.mug, [-1.575, .5, -.35], [.05, .05, .05], [Math.PI / 2, 0, 0]);
  for (const y of [1.2, 1.62, 2.04]) { S(G.kotak, MAT.kayu, [-2.4, y, -1.2], [.28, .04, 1.1]); S(G.kotak, MAT.buku, [-2.42, y + .14, -1.2], [.2, .24, 1.0]); }
  S(G.kotak, MAT.bingkai, [-1.3, 1.75, WZ + .1], [.5, .62, .03]); S(G.kotak, MAT.lukisan[0], [-1.3, 1.75, WZ + .12], [.42, .54, .01]);
  S(G.kotak, MAT.bingkai, [-.6, 1.6, WZ + .1], [.34, .42, .03]); S(G.kotak, MAT.lukisan[1], [-.6, 1.6, WZ + .12], [.28, .36, .01]);
  S(G.kotak, MAT.bingkai, [1.85, 1.7, WZ + .1], [.4, .5, .03]); S(G.kotak, MAT.lukisan[2], [1.85, 1.7, WZ + .12], [.34, .44, .01]);
  S(G.pot, MAT.potBesar, [1.9, 0, -2.0], [.36, .5, .36]); for (let i = 0; i < 9; i++) { const a = i / 9 * Math.PI * 2; S(G.daun, MAT.tanamanBesar, [1.9, .38, -2.0], [.5, .8, .5], [-.55 - (i % 3) * .15, a, 0]); }
  S(G.kotakBulat, MAT.kainKrem, [-1.05, .08, .15], [.5, .15, .5]);
  // crate under the sprout (by the window)
  const PX = .55, PZ = -2.05;
  S(G.kotak, MAT.kayuMuda, [PX, .18, PZ], [.42, .36, .36]); for (const y of [.09, .27]) S(G.kotak, MAT.kayu, [PX, y, PZ + .185], [.43, .03, .01]);
  S(G.bidang, MAT.blob, [PX, .004, PZ], [.7, .6, 1], [-Math.PI / 2, 0, 0]);

  // ---- sprout
  const tanaman = { pot: N(G.pot, MAT.pot, [PX, .36, PZ], [.13, .15, .13]), tanah: N(G.tanah, MAT.tanah, [PX, .47, PZ], [.12, 1, .12]),
    batang: N(G.silinder, { ...MAT.batang }, [0, 0, 0], [.008, .22, .008]), daunL: N(G.daun, { ...MAT.daun }, [0, 0, 0], [.07, .09, .07]), daunR: N(G.daun, { ...MAT.daun }, [0, 0, 0], [.07, .09, .07]),
    kelopak: [0, 1, 2, 3, 4].map(() => N(G.bola, MAT.kelopak, [0, 0, 0], [.02, .006, .03])), putik: N(G.bola, MAT.putik, [0, 0, 0], [.014, .014, .014]) };

  // ---- robot (root at the feet)
  const rb = {};
  rb.root = N(null, null);
  rb.kakiL = N(G.silinder, MAT.robotGelap, [-.075, .06, 0], [.07, .08, .07], [0, 0, 0], rb.root); rb.kakiR = N(G.silinder, MAT.robotGelap, [.075, .06, 0], [.07, .08, .07], [0, 0, 0], rb.root);
  rb.tapakL = N(G.kotakBulat, MAT.robotOranye, [-.075, .024, .02], [.1, .048, .14], [0, 0, 0], rb.root); rb.tapakR = N(G.kotakBulat, MAT.robotOranye, [.075, .024, .02], [.1, .048, .14], [0, 0, 0], rb.root);
  rb.badan = N(G.badanRobot, MAT.robotKrem, [0, .22, 0], [.3, .26, .24], [0, 0, 0], rb.root);
  rb.panel = N(G.kotakBulat, MAT.robotOranye, [0, .21, .12], [.15, .09, .02], [0, 0, 0], rb.root); rb.tombol = N(G.silinder, MAT.robotGelap, [.035, .215, .13], [.022, .012, .022], [Math.PI / 2, 0, 0], rb.root);
  rb.leher = N(G.silinder, MAT.robotLogam, [0, .365, 0], [.05, .05, .05], [0, 0, 0], rb.root);
  rb.kepala = N(null, null, [0, .39, 0], [1, 1, 1], [0, 0, 0], rb.root);
  rb.helm = N(G.kepalaRobot, MAT.robotLogam, [0, .13, 0], [.36, .28, .3], [0, 0, 0], rb.kepala);
  rb.cincin = N(G.torus, MAT.robotGelap, [0, .12, .152], [.2, .2, .2], [Math.PI / 2, 0, 0], rb.kepala);
  rb.mataBelakang = N(G.silinder, MAT.robotGelap, [0, .12, .145], [.19, .02, .19], [Math.PI / 2, 0, 0], rb.kepala);
  rb.mata = N(G.silinder, { ...MAT.mata }, [0, .12, .158], [.16, .008, .16], [Math.PI / 2, 0, 0], rb.kepala);
  rb.kilap = N(G.bola, MAT.lampu, [-.03, .15, .166], [.022, .018, .006], [0, 0, 0], rb.kepala);
  rb.kupingL = N(G.silinder, MAT.robotOranye, [-.18, .12, 0], [.07, .04, .07], [0, 0, Math.PI / 2], rb.kepala); rb.kupingR = N(G.silinder, MAT.robotOranye, [.18, .12, 0], [.07, .04, .07], [0, 0, Math.PI / 2], rb.kepala);
  rb.antena = N(G.silinder, MAT.robotGelap, [.06, .31, 0], [.008, .1, .008], [0, 0, .15], rb.kepala); rb.bohlam = N(G.bola, { ...MAT.antena }, [.075, .365, 0], [.032, .032, .032], [0, 0, 0], rb.kepala);
  rb.bahuL = N(null, null, [-.17, .3, 0], [1, 1, 1], [0, 0, 0], rb.root); rb.bahuR = N(null, null, [.17, .3, 0], [1, 1, 1], [0, 0, 0], rb.root);
  rb.lenganL = N(G.kapsul, MAT.robotLogam, [0, -.07, 0], [.055, .16, .055], [0, 0, 0], rb.bahuL); rb.lenganR = N(G.kapsul, MAT.robotLogam, [0, -.07, 0], [.055, .16, .055], [0, 0, 0], rb.bahuR);
  rb.tanganL = N(G.bola, MAT.robotOranye, [0, -.16, 0], [.065, .065, .065], [0, 0, 0], rb.bahuL); rb.tanganR = N(G.bola, MAT.robotOranye, [0, -.16, 0], [.065, .065, .065], [0, 0, 0], rb.bahuR);
  rb.blob = N(G.bidang, MAT.blob, [0, .004, 0], [.45, .4, 1], [-Math.PI / 2, 0, 0]);
  const nodeRobot = Object.values(rb);

  // ---- little robin (root at its feet)
  const brd = { root: N(null, null) };
  const bulu = mat('#8a5a3a', { rough: .7, spec: .1 }), dada = mat('#e8864a', { rough: .7, spec: .1 }), paruh = mat('#f0c040', { rough: .5 }), hitam = mat('#101010', { unlit: true });
  brd.badan = N(G.bola, bulu, [0, .045, 0], [.07, .06, .095], [0, 0, 0], brd.root);
  brd.dada = N(G.bola, dada, [0, .04, .022], [.058, .05, .06], [0, 0, 0], brd.root);
  brd.ekor = N(G.bola, bulu, [0, .06, -.06], [.03, .008, .06], [-.4, 0, 0], brd.root);
  brd.kepala = N(null, null, [0, .085, .03], [1, 1, 1], [0, 0, 0], brd.root);
  brd.kepalaBola = N(G.bola, bulu, [0, 0, 0], [.048, .046, .05], [0, 0, 0], brd.kepala);
  brd.muka = N(G.bola, dada, [0, -.006, .012], [.036, .03, .036], [0, 0, 0], brd.kepala);
  brd.paruh = N(G.bola, paruh, [0, -.002, .034], [.009, .008, .022], [0, 0, 0], brd.kepala);
  brd.mataL = N(G.bola, hitam, [-.017, .008, .018], [.008, .008, .008], [0, 0, 0], brd.kepala); brd.mataR = N(G.bola, hitam, [.017, .008, .018], [.008, .008, .008], [0, 0, 0], brd.kepala);
  brd.sayapL = N(null, null, [-.03, .055, 0], [1, 1, 1], [0, 0, 0], brd.root); brd.sayapR = N(null, null, [.03, .055, 0], [1, 1, 1], [0, 0, 0], brd.root);
  brd.sayapLb = N(G.bola, bulu, [-.035, 0, -.01], [.07, .012, .075], [0, 0, 0], brd.sayapL); brd.sayapRb = N(G.bola, bulu, [.035, 0, -.01], [.07, .012, .075], [0, 0, 0], brd.sayapR);
  brd.kakiL = N(G.silinder, paruh, [-.012, .01, .005], [.006, .025, .006], [0, 0, 0], brd.root); brd.kakiR = N(G.silinder, paruh, [.012, .01, .005], [.006, .025, .006], [0, 0, 0], brd.root);
  const nodeBurung = Object.values(brd);

  // dust motes
  const r = rngS(77);
  const DEBU = Array.from({ length: 60 }, () => ({ n: N(G.bidang, MAT.debu, [0, 0, 0], [.012, .012, 1]), x: WX - .8 + r() * 1.6, y: .1 + r() * 2.0, z: -2.3 + r() * 1.8, f: r() * 9, s: .5 + r() }));

  return { G, MAT, T, statis, tanaman, rb, nodeRobot, burung: brd, nodeBurung, DEBU, luar, hujanN, kacaN, tiraiL, tiraiR, bohlam, WX, WY0, WY1, WZ, PX, PZ };
}

// world matrices
function kumpulkan(nodes, out) {
  const cache = new Map();
  const dunia = n => { if (cache.has(n)) return cache.get(n); const l = M4.trs(n.t, n.r, n.s); const w = n.parent ? M4.mul(dunia(n.parent), l) : l; cache.set(n, w); return w; };
  for (const n of nodes) { if (!n.mesh || !n.vis) continue; const w = dunia(n); out.push({ mesh: n.mesh, mat: n.mat, model: w, z: n.z }); }
  return cache;
}

// =====================================================================
//  STORY: shots, animation, lighting, sound
// =====================================================================
const DUR = 50;
const BURUNG_DARAT = [.69, .36, -1.99];
const klem = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const eio = t => { t = klem(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const halus = t => { t = klem(t); return t * t * (3 - 2 * t); };
const u = (t, a, b) => klem((t - a) / (b - a));
const lerpV = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t);
const nz = (x, s) => Math.sin(x * 1.3 + s) * .5 + Math.sin(x * 2.9 + s * 1.7) * .3 + Math.sin(x * 6.1 + s * 2.3) * .2;

const TITIK_A = [-1.0, 0, -1.2], TITIK_B = [.08, 0, -1.9], YAW_A = .6;
// robot position / yaw / walk phase over time
function posRobot(t, D) {
  const jalan = u(t, 12.2, 17.2), e = halus(jalan);
  const pos = lerpV(TITIK_A, TITIK_B, e);
  const dx = TITIK_B[0] - TITIK_A[0], dz = TITIK_B[2] - TITIK_A[2], yawJalan = Math.atan2(dx, dz);
  const yawTanaman = Math.atan2(D.PX - TITIK_B[0], D.PZ - TITIK_B[2]), yawJendela = Math.atan2(D.WX - TITIK_B[0] - .1, D.WZ - TITIK_B[2]), yawBurung = Math.atan2(BURUNG_DARAT[0] - TITIK_B[0], BURUNG_DARAT[2] - TITIK_B[2]) - .25;
  let yaw = YAW_A;
  if (t > 11.6) yaw = lerp(YAW_A, yawJalan, eio(u(t, 11.6, 12.6)));
  if (t > 16.6) yaw = lerp(yawJalan, yawTanaman, eio(u(t, 16.6, 17.8)));
  if (t > 33.2) yaw = lerp(yawTanaman, yawBurung, eio(u(t, 33.2, 34.0)));
  if (t > 41.5) yaw = lerp(yawBurung, yawJendela, eio(u(t, 41.5, 43)));
  const langkah = jalan > 0 && jalan < 1 ? (t - 12.2) * 9.5 : 0;
  return { pos, yaw, langkah, berjalan: jalan > 0 && jalan < 1 };
}

function animasiRobot(t, D) {
  const rb = D.rb, P = posRobot(t, D);
  const hop = Math.max(0, Math.sin(u(t, 30.2, 30.75) * Math.PI)) * .09 + Math.max(0, Math.sin(u(t, 30.8, 31.35) * Math.PI)) * .07;
  const bob = P.berjalan ? Math.abs(Math.sin(P.langkah)) * .018 : Math.sin(t * 2.1) * .004;
  rb.root.t = [P.pos[0], P.pos[1] + bob + hop, P.pos[2]]; rb.root.r = [0, P.yaw, P.berjalan ? Math.sin(P.langkah) * .07 : 0];
  // legs + feet
  const lift = s => P.berjalan ? Math.max(0, Math.sin(P.langkah + (s > 0 ? Math.PI : 0))) * .035 : 0;
  const maju = s => P.berjalan ? Math.cos(P.langkah + (s > 0 ? Math.PI : 0)) * .03 : 0;
  rb.kakiL.t = [-.075, .06 + lift(-1), maju(-1)]; rb.kakiR.t = [.075, .06 + lift(1), maju(1)];
  rb.tapakL.t = [-.075, .024 + lift(-1), .02 + maju(-1)]; rb.tapakR.t = [.075, .024 + lift(1), .02 + maju(1)];
  // powered down: slumped; wakes up at 9
  const bangun = eio(u(t, 9.0, 10.2)), lesu = 1 - bangun;
  const lihatJendela = eio(u(t, 10.4, 11.3)) * (1 - eio(u(t, 11.6, 12.4)));
  const penasaran = eio(u(t, 18.4, 19.4)) * (1 - eio(u(t, 22.6, 23.4)));
  const condong = eio(u(t, 20.2, 21.2)) * (1 - eio(u(t, 23.8, 24.8)));
  const senang = eio(u(t, 29.6, 30.2)) * (1 - eio(u(t, 31.6, 32.4)));
  const akhir = eio(u(t, 41.8, 43)), kaget = eio(u(t, 33.3, 33.8)) * (1 - eio(u(t, 35, 36))), lambai = eio(u(t, 34.4, 34.9)) * (1 - eio(u(t, 37.2, 37.8)));
  rb.kepala.r = [lesu * .42 + condong * .22 - senang * .15 - akhir * .12 - kaget * .18 + Math.sin(t * 1.3) * .015, lihatJendela * -.7 + akhir * -.25, penasaran * .28 * Math.sin(t * .9 + .5) + penasaran * .15 + akhir * .12 + kaget * .3 + lambai * .12 * Math.sin(t * 2)];
  rb.badan.r = [lesu * .12 + condong * .1, 0, 0]; rb.panel.r = rb.badan.r; rb.tombol.r = [Math.PI / 2 + lesu * .12, 0, 0];
  // arms: hang / swing when walking / reach / cheer
  const ayun = P.berjalan ? Math.sin(P.langkah) * .45 : Math.sin(t * 1.7) * .03;
  const raih = eio(u(t, 20.6, 21.6)) * (1 - eio(u(t, 23.6, 24.6)));
  rb.bahuL.r = [ayun - senang * 2.6, 0, -.12 - lesu * .05 + senang * .3]; rb.bahuR.r = [-ayun - raih * 1.25 - senang * 2.6 - lambai * 2.7 + raih * Math.sin(t * 3) * .05, raih * -.25, .12 + lesu * .05 - senang * .3 + lambai * (.2 + Math.sin(t * 10) * .45)];
  // eye
  let nyala = t < 8.2 ? 0 : t < 8.9 ? (Math.sin(t * 60) > 0 ? .9 : .15) * u(t, 8.2, 8.9) + u(t, 8.2, 8.9) * .3 : 1;
  nyala *= 1 + .5 * eio(u(t, 20.2, 21)) * (1 - eio(u(t, 24, 25))) + .3 * senang + .35 * lambai;
  const kd = (t + .7) % 3.4, kedip = t > 9 && kd < .16 ? Math.abs(kd - .08) / .08 : 1;
  rb.mata.s = [.16, .008, .16 * Math.max(.08, kedip)]; rb.mata.mat.emi = [nyala * .25, nyala * .6, nyala * .95]; rb.mata.mat.col = mixV([.08, .09, .1], [1, 1, 1], klem(nyala));
  rb.kilap.vis = nyala > .2 || true;
  const ant = t > 8.5 ? .6 + .4 * Math.sin(t * 3) + (senang + lambai) * 1.5 * (.6 + .4 * Math.sin(t * 12)) : .05; rb.bohlam.mat.emi = [ant * 1.6, ant * .7, ant * .2]; rb.bohlam.mat.col = [1, .6, .3];
  rb.blob.t = [P.pos[0], .004, P.pos[2]]; rb.blob.s = [.45 - hop, .4 - hop, 1];
  return { nyala, P };
}

function animasiTanaman(t, D) {
  const tn = D.tanaman, w = 1 - .45 * eio(u(t, 21, 23.6)) - .55 * eio(u(t, 25.8, 29)), b = eio(u(t, 28.2, 30.6));
  const base = [D.PX, .49, D.PZ], L = .15 + (1 - w) * .05, lean = w * .95 + Math.sin(t * .8) * .02;
  tn.batang.t = [base[0] - Math.sin(lean) * L / 2, base[1] + Math.cos(lean) * L / 2, base[2]]; tn.batang.r = [0, 0, lean]; tn.batang.s = [.009, L, .009];
  const top = [base[0] - Math.sin(lean) * L, base[1] + Math.cos(lean) * L, base[2]];
  const hijau = mixV([.4, .66, .28], [.55, .5, .25], w), th = lerp(.85, 2.25, w);
  tn.batang.mat.col = mixV([.37, .56, .23], [.5, .45, .25], w);
  tn.daunL.t = [top[0], top[1] - .01, top[2]]; tn.daunL.r = [.15, 0, lean + th]; tn.daunL.mat.col = hijau;
  tn.daunR.t = [top[0], top[1] - .01, top[2]]; tn.daunR.r = [.15, 0, lean - th + (w > .5 ? .5 : 0)]; tn.daunR.mat.col = hijau;
  const sz = lerp(.05, .085, 1 - w); tn.daunL.s = [sz * .8, sz, sz]; tn.daunR.s = [sz * .8, sz, sz];
  tn.kelopak.forEach((k, i) => { const a = i / 5 * Math.PI * 2 + t * .1; k.vis = b > .01; k.t = [top[0] + Math.cos(a) * .018 * b, top[1] + .012, top[2] + Math.sin(a) * .018 * b]; k.r = [0, -a, .25]; k.s = [.022 * b, .006 * b, .012 * b]; });
  tn.putik.vis = b > .01; tn.putik.t = [top[0], top[1] + .016, top[2]]; tn.putik.s = [.012 * b, .01 * b, .012 * b];
  return { w, b, top };
}

// ---------- cameras
function kamera(t, D, P, potret) {
  const rp = P.pos, kepala = [rp[0], .5, rp[2]];
  let c;
  if (t < 7) { const k = eio(t / 7); c = { pos: lerpV([1.75, 1.3, 1.45], [1.3, 1.05, .85], k), target: [-.4, .55, -1.45], fov: 48 }; }
  else if (t < 12) { const f = [Math.sin(YAW_A), 0, Math.cos(YAW_A)], k = eio((t - 7) / 5), d = lerp(1.05, .86, k);
    c = { pos: [TITIK_A[0] + f[0] * d + .1, lerp(.5, .54, k), TITIK_A[2] + f[2] * d - .04], target: [TITIK_A[0], lerp(.4, .5, u(t, 8.8, 10.2)), TITIK_A[2]], fov: 34 }; }
  else if (t < 18) { const w = eio(u(t, 12.2, 17.2)); c = { pos: [rp[0] + lerp(1.1, .95, w), lerp(.55, .62, w), rp[2] + lerp(-.22, .45, w)], target: [rp[0] + lerp(.08, .2, w), .3, rp[2] - .08], fov: 40 }; }
  else if (t < 25) { const k = eio((t - 18) / 7);
    c = { pos: [lerp(1.15, 1.02, k), lerp(.64, .6, k), lerp(-1.62, -1.72, k)], target: [.3, .5, -1.95], fov: 38 }; }
  else if (t < 32) { const k = eio((t - 25) / 7); c = { pos: [lerp(-.5, -.42, k), lerp(.4, .44, k), lerp(-.62, -.78, k)], target: [.4, lerp(.75, .88, k), -2.3], fov: 46 }; }
  else if (t < 40) { const k = eio((t - 32) / 8); c = { pos: [lerp(1.28, 1.12, k), lerp(.7, .64, k), lerp(-1.3, -1.42, k)], target: [.4, .5, -1.98], fov: 40 }; }
  else { const k = eio((t - 40) / 7); c = { pos: lerpV([1.05, .72, -.75], [1.95, 1.45, 1.1], k), target: [.35, lerp(.55, .75, k), -1.95], fov: 42 }; }
  // handheld drift
  c.pos = [c.pos[0] + nz(t * .4, 1) * .008, c.pos[1] + nz(t * .35, 2) * .006, c.pos[2] + nz(t * .3, 3) * .008];
  let fov = c.fov * Math.PI / 180;
  if (potret) { fov = 2 * Math.atan(Math.tan(fov / 2) * 1.75); const d = lerpV(c.pos, c.target, 0); c.pos = lerpV(c.target, d, 1.08); }
  c.fov = fov; return c;
}

// ---------- lighting per moment
function cahayaDunia(t, D, R) {
  const hujan = 1 - eio(u(t, 25.4, 27.6)), cerah = 1 - hujan;
  return {
    hujan, cerah,
    sun: { dir: (() => { const v = [-.3, -.78, 1]; const l = Math.hypot(...v); return v.map(x => x / l); })(), col: mixV([.12, .15, .22], [2.5, 2.0, 1.45], cerah) },
    sky: mixV([.30, .34, .44], [.52, .48, .44], cerah), ground: mixV([.16, .14, .14], [.34, .26, .19], cerah),
    fog: { col: mixV([.14, .15, .2], [.42, .36, .3], cerah), d: .02 },
    rim: mixV([.3, .45, .7], [1, .8, .55], cerah),
    lampu: mixV([1.7, 1.08, .55], [.55, .38, .22], cerah),
    post: { exp: lerp(1.0, .95, cerah), bloom: lerp(.75, .65, cerah), th: lerp(.85, 1.05, cerah), rays: cerah * .95, sat: lerp(1.0, 1.1, cerah), vig: 1.15,
      lift: mixV([.015, .025, .055], [.03, .02, .0], cerah), gain: mixV([.98, 1.0, 1.06], [1.06, 1.0, .92], cerah) },
  };
}

// ---------- sound
let A = null, master = null, gema = null, bising = null, amb = {};
function siapAudio() {
  if (A) { A.resume(); return; }
  try {
    A = new (window.AudioContext || window.webkitAudioContext)();
    const k = A.createDynamicsCompressor(); k.threshold.value = -16; k.connect(A.destination);
    master = A.createGain(); master.gain.value = .9; master.connect(k);
    const n = A.sampleRate * 3.5, ir = A.createBuffer(2, n, A.sampleRate); for (let c = 0; c < 2; c++) { const d = ir.getChannelData(c); for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / n, 2.4); }
    gema = A.createConvolver(); gema.buffer = ir; const gg = A.createGain(); gg.gain.value = .5; gema.connect(gg); gg.connect(master);
    bising = A.createBuffer(1, A.sampleRate * 3, A.sampleRate); const d = bising.getChannelData(0); let l = 0; for (let i = 0; i < d.length; i++) { const w = Math.random() * 2 - 1; l = (l + .02 * w) / 1.02; d[i] = w * .5 + l * 3; }
    const loop = (tipe, f, q) => { const s = A.createBufferSource(); s.buffer = bising; s.loop = true; const fl = A.createBiquadFilter(); fl.type = tipe; fl.frequency.value = f; fl.Q.value = q; const g = A.createGain(); g.gain.value = 0; s.connect(fl); fl.connect(g); g.connect(master); s.start(); return g; };
    amb.hujan = loop('highpass', 1400, .4); amb.gemuruh = loop('lowpass', 380, .5); amb.tetes = loop('bandpass', 3200, 3);
  } catch (_) { A = null; }
}
const hz = m => 440 * Math.pow(2, (m - 69) / 12);
function kirim(node, pan = 0, rev = .4) { let n = node; if (A.createStereoPanner) { const p = A.createStereoPanner(); p.pan.value = pan; node.connect(p); n = p; } n.connect(master); const s = A.createGain(); s.gain.value = rev; n.connect(s); s.connect(gema); }
function piano(m, t, v, d = 3.5) { const f0 = hz(m), lp = A.createBiquadFilter(), g = A.createGain(); lp.type = 'lowpass'; lp.frequency.setValueAtTime(1500 + v * 12000, t); lp.frequency.exponentialRampToValueAtTime(420, t + d);
  for (const [k, ty, a] of [[1, 'triangle', 1], [2, 'sine', .38], [3, 'sine', .12]]) { const o = A.createOscillator(), gg = A.createGain(); o.type = ty; o.frequency.value = f0 * k; o.detune.value = (Math.random() - .5) * 6; gg.gain.value = a; o.connect(gg); gg.connect(lp); o.start(t); o.stop(t + d + .1); }
  g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(v, t + .006); g.gain.exponentialRampToValueAtTime(v * .4, t + .35); g.gain.exponentialRampToValueAtTime(.0001, t + d); lp.connect(g); kirim(g, klem((m - 64) / 30, -.5, .5), .5); }
function pad(ms, t, d, v) { for (const m of ms) for (const dt of [-6, 6]) { const o = A.createOscillator(), f = A.createBiquadFilter(), g = A.createGain(); o.type = 'sawtooth'; o.frequency.value = hz(m); o.detune.value = dt; f.type = 'lowpass'; f.frequency.setValueAtTime(500, t); f.frequency.linearRampToValueAtTime(1300, t + d * .5);
  g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(v, t + Math.min(1.5, d * .4)); g.gain.linearRampToValueAtTime(0, t + d + .5); o.connect(f); f.connect(g); kirim(g, dt > 0 ? .3 : -.3, .6); o.start(t); o.stop(t + d + .6); } }
function bip(f0, f1, t, d, v, tipe = 'sine') { const o = A.createOscillator(), g = A.createGain(); o.type = tipe; o.frequency.setValueAtTime(f0, t); o.frequency.exponentialRampToValueAtTime(f1, t + d); g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(v, t + .01); g.gain.exponentialRampToValueAtTime(.0001, t + d); o.connect(g); kirim(g, .15, .35); o.start(t); o.stop(t + d + .05); }
function desing(t, d, v, f0 = 300, f1 = 900) { const s = A.createBufferSource(); s.buffer = bising; const f = A.createBiquadFilter(), g = A.createGain(); f.type = 'bandpass'; f.Q.value = 6; f.frequency.setValueAtTime(f0, t); f.frequency.linearRampToValueAtTime(f1, t + d); g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(v, t + .05); g.gain.linearRampToValueAtTime(0, t + d); s.connect(f); f.connect(g); kirim(g, 0, .2); s.start(t, Math.random()); s.stop(t + d + .05); }
function lonceng(m, t, v) { const o = A.createOscillator(), o2 = A.createOscillator(), g = A.createGain(), g2 = A.createGain(); o.type = o2.type = 'sine'; o.frequency.value = hz(m); o2.frequency.value = hz(m) * 2.76; g2.gain.value = .25; g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(v, t + .004); g.gain.exponentialRampToValueAtTime(.0001, t + 2.4); o.connect(g); o2.connect(g2); g2.connect(g); kirim(g, .3, .8); o.start(t); o2.start(t); o.stop(t + 2.5); o2.stop(t + 2.5); }
function klik(t, v) { const s = A.createBufferSource(); s.buffer = bising; const f = A.createBiquadFilter(), g = A.createGain(); f.type = 'bandpass'; f.frequency.value = 1800; f.Q.value = 2; g.gain.setValueAtTime(v, t); g.gain.exponentialRampToValueAtTime(.0001, t + .05); s.connect(f); f.connect(g); kirim(g, 0, .15); s.start(t, Math.random()); s.stop(t + .06); }

const BPM = 76, E8 = 60 / BPM / 2;
const AKOR_HUJAN = [[41, [57, 60, 64]], [40, [55, 59, 62]], [38, [57, 60, 65]], [36, [55, 59, 64]]];
const AKOR_CERAH = [[41, [57, 60, 64, 69]], [43, [59, 62, 67]], [40, [59, 64, 67]], [45, [60, 64, 69]], [38, [60, 65, 69]], [43, [59, 62, 65]], [36, [60, 64, 67, 72]], [36, [60, 64, 67, 71]]];
const MELODI = { 2: [[0, 76, 3], [4, 74, 2], [6, 72, 2]], 3: [[0, 71, 4], [4, 72, 4]], 4: [[0, 69, 3], [3, 72, 1], [4, 74, 4]], 5: [[0, 76, 2], [2, 79, 2], [4, 76, 4]], 6: [[0, 74, 4], [4, 72, 2], [6, 71, 2]], 7: [[0, 72, 8]],
  8: [[0, 81, 2], [2, 79, 2], [4, 76, 4]], 9: [[0, 79, 3], [3, 81, 1], [4, 83, 4]], 10: [[0, 84, 2], [2, 83, 2], [4, 79, 4]], 11: [[0, 81, 3], [3, 79, 1], [4, 76, 4]], 12: [[0, 79, 2], [2, 81, 2], [4, 84, 4]], 13: [[0, 83, 3], [3, 81, 1], [4, 79, 4]], 14: [[0, 76, 4], [4, 79, 4]] };
let jadwal = -1;
function langkahMusik(i, at) {
  const bar = Math.floor(i / 8), pos = i % 8;
  if (bar >= 15) { if (bar === 15 && pos === 0) { [36, 48, 55, 60, 64, 67, 71, 74].forEach((m, k) => piano(m, at + k * .07, .09, 6)); pad([60, 64, 67, 71], at, 4, .01); lonceng(88, at + .9, .03); } return; }
  const cerah = bar >= 8, [ba, ak] = cerah ? AKOR_CERAH[(bar - 8) % 8] : AKOR_HUJAN[bar % 4];
  if (pos === 0) { piano(ba, at, .13, 5); if (bar >= 2) piano(ba + 12, at + .01, .06, 4); if (cerah) pad(ak, at, E8 * 8, .007); }
  if (bar >= 1 && pos % 2 === 1 || (cerah && pos % 2 === 0 && pos)) piano(ak[(pos >> 1) % ak.length] + (pos > 4 ? 12 : 0), at, cerah ? .055 : .045, 3);
  const mel = MELODI[bar]; if (mel) for (const [p, m, l] of mel) if (p === pos) piano(m, at, cerah ? .1 : .08, l * E8 + 1.6);
}
function musik(T, main) {
  if (!A || !main) return;
  if (jadwal < T - .1 || jadwal > T + 1) jadwal = Math.ceil(T / E8 - 1e-6) * E8;
  while (jadwal < T + .25) { const tb = jadwal, at = A.currentTime + Math.max(0, tb - T) + .03; if (tb < DUR - .3) langkahMusik(Math.round(tb / E8), at); jadwal += E8; }
}
function ambiens(T, main) {
  if (!A) return; const now = A.currentTime, hujan = 1 - eio(u(T, 25.2, 27.8)), m = main ? 1 : 0;
  amb.hujan.gain.setTargetAtTime(.16 * hujan * m, now, .3); amb.gemuruh.gain.setTargetAtTime(.09 * hujan * m, now, .3); amb.tetes.gain.setTargetAtTime(.02 * hujan * m, now, .3);
}
const ACARA = [
  [8.2, t => { desing(t, .9, .05, 200, 1400); bip(400, 1200, t + .5, .25, .05); bip(900, 1500, t + .78, .12, .045); }],
  [10.7, t => { bip(1400, 1100, t, .09, .05); bip(1400, 1700, t + .14, .11, .05); }],
  ...Array.from({ length: 10 }, (_, k) => [12.3 + k * .33 + .16, t => { klik(t, .05); if (k % 3 === 0) desing(t, .18, .015, 500, 700); }]),
  [20.6, t => { desing(t, .6, .03, 300, 800); }], [21.8, t => { bip(900, 1300, t, .2, .04); }], [23.2, t => lonceng(84, t, .025)],
  [28.4, t => { [88, 91, 95, 100].forEach((m, k) => lonceng(m, t + k * .12, .02)); }],
  [29.5, t => { bip(2800, 3900, t, .08, .02); bip(3000, 4200, t + .12, .08, .02); }],
  [32.5, t => { for (let k = 0; k < 9; k++) desing(t + k * .1, .08, .012, 900, 1400); }],
  [33.7, t => { bip(3200, 4400, t, .07, .03); bip(3500, 4800, t + .11, .07, .03); bip(3000, 4200, t + .22, .09, .03); }],
  [34.5, t => { bip(900, 1400, t, .12, .045); bip(1300, 1800, t + .16, .14, .045); }],
  [35.2, t => { bip(3400, 4600, t, .06, .03); bip(3600, 5000, t + .09, .06, .03); }], [37.3, t => { bip(3100, 4300, t, .07, .03); bip(2900, 4100, t + .1, .07, .03); bip(3300, 4700, t + .2, .08, .03); }],
  [41.0, t => { [84, 88, 91].forEach((m, k) => lonceng(m, t + k * .15, .02)); }],
  [30.2, t => { bip(300, 700, t, .22, .06, 'triangle'); bip(1200, 1800, t + .05, .1, .04); }], [30.8, t => { bip(320, 760, t, .22, .06, 'triangle'); bip(1500, 2100, t + .05, .1, .04); }],
];

// ---------- the little bird that drops by
function animasiBurung(t, D) {
  const b = D.burung, dari = [1.55, 1.75, -1.05];
  const f = u(t, 32.4, 33.65), terbang = t < 33.65;
  b.root.vis = t > 32.3;
  let p;
  if (terbang) { const e = halus(f); p = [lerp(dari[0], BURUNG_DARAT[0], e), lerp(dari[1], BURUNG_DARAT[1], e) + Math.sin(e * Math.PI) * .18, lerp(dari[2], BURUNG_DARAT[2], e)]; }
  else { const hop = Math.max(0, Math.sin(u(t, 35.1, 35.45) * Math.PI)) * .035 + Math.max(0, Math.sin(u(t, 37.2, 37.55) * Math.PI)) * .03; p = [BURUNG_DARAT[0] + u(t, 37.2, 37.55) * .02, BURUNG_DARAT[1] + hop, BURUNG_DARAT[2]]; }
  const yaw = terbang ? Math.atan2(BURUNG_DARAT[0] - dari[0], BURUNG_DARAT[2] - dari[2]) : lerp(-1.3, -1.75, u(t, 33.6, 34.2));
  b.root.t = p; b.root.r = [terbang ? .25 : 0, yaw, 0];
  const kepak = terbang || (t > 35.05 && t < 35.5) || (t > 37.15 && t < 37.6) ? Math.sin(t * 38) : 0, lipat = terbang ? 0 : 1;
  b.sayapL.r = [0, 0, lerp(.9 + kepak * .9, .15, lipat * (kepak ? .4 : 1))]; b.sayapR.r = [0, 0, -lerp(.9 + kepak * .9, .15, lipat * (kepak ? .4 : 1))];
  b.kepala.r = [Math.sin(t * 3.1) * .12 * (1 - lipat * 0) + (t > 34 && t < 36.8 ? -.25 : 0), t > 33.9 ? Math.sin(t * 1.7) * .5 : 0, Math.sin(t * 2.3) * .25];
}

const SUB = [
  [0.8, 3.6, 'Some days, the quiet gets loud.'],
  [3.9, 6.8, 'Like the whole world forgot you’re even here.'],
  [8.3, 11.6, 'But even the smallest light can still turn on.'],
  [12.6, 15.2, 'You don’t need to have it all figured out.'],
  [15.4, 17.8, 'Just take one small step.'],
  [18.6, 21.6, 'Find something to care for. Even something tiny.'],
  [22.0, 24.8, 'Taking care of something is how we heal, too.'],
  [25.8, 28.6, 'Rain doesn’t last forever.'],
  [29.0, 31.8, 'And neither does feeling alone.'],
  [33.4, 36.4, 'Sometimes, the right ones find their way to you.'],
  [36.8, 39.7, 'You were never as alone as you felt.'],
  [41.0, 44.9, 'So keep your little light on.'],
];

const cv = document.getElementById('gl'), tk = document.getElementById('teks'), X = tk.getContext('2d');
let R = null, D = null;
try { R = buatRenderer(cv); if (R) D = buatDunia(R); } catch (e) { console.error(e); R = null; }
if (!R) { document.getElementById('galat').hidden = false; document.getElementById('mulai').hidden = true; }
let FORMAT = '916', T = 0, main = false, tSebelum = 0, lalu = performance.now();
function ukur() { const r = cv.getBoundingClientRect(), dpr = Math.min(devicePixelRatio || 1, 1.5); cv.width = Math.max(2, Math.round(r.width * dpr)); cv.height = Math.max(2, Math.round(r.height * dpr)); tk.width = cv.width; tk.height = cv.height; }
new ResizeObserver(ukur).observe(cv);

function render() {
  const potret = FORMAT === '916', L = cahayaDunia(T, D, R), ar = animasiRobot(T, D), tn = animasiTanaman(T, D), cam = kamera(T, D, ar.P, potret); animasiBurung(T, D);
  const M = D.MAT;
  M.luar.mix2 = L.cerah; M.luar.col = mixV([.95, .95, 1], [1.75, 1.6, 1.4], L.cerah); M.hujan.alpha = .7 * L.hujan; M.hujan.uvOff = [0, T * 2.2]; M.kaca.alpha = .12 + .25 * L.hujan; M.kaca.uvOff = [0, -T * .004];
  D.hujanN.vis = L.hujan > .01; D.bohlam.mat.emi = L.lampu.map(v => v * 1.6);
  // dust motes in the sunbeam
  const debu = [];
  for (const d of D.DEBU) { d.n.t = [d.x + Math.sin(T * .3 + d.f) * .06, d.y + Math.sin(T * .21 + d.f * 2) * .05, d.z + Math.cos(T * .25 + d.f) * .06]; d.n.s = [.012 * d.s, .012 * d.s, 1];
    const dx = cam.pos[0] - d.n.t[0], dz = cam.pos[2] - d.n.t[2]; d.n.r = [0, Math.atan2(dx, dz), 0]; d.n.mat = { ...D.MAT.debu, alpha: .8 * L.cerah * (.5 + .5 * Math.sin(T * 1.3 + d.f)) }; if (L.cerah > .05) debu.push(d.n); }
  const obj = []; kumpulkan([...D.statis, ...D.nodeRobot, ...(D.burung.root.vis ? D.nodeBurung : []), D.tanaman.pot, D.tanaman.tanah, D.tanaman.batang, D.tanaman.daunL, D.tanaman.daunR, ...D.tanaman.kelopak, D.tanaman.putik, ...debu], obj);
  for (const o of obj) if (o.mat.alpha < 1 || o.mat.aditif) { const p = [o.model[12], o.model[13], o.model[14]]; o.z = Math.hypot(p[0] - cam.pos[0], p[1] - cam.pos[1], p[2] - cam.pos[2]); }
  // point lights: lamp, the robot's eye, antenna
  const kp = D.rb, head = M4.trs(kp.root.t, kp.root.r, [1, 1, 1]), eyeW = M4.xf(M4.mul(head, M4.trs(kp.kepala.t, kp.kepala.r, [1, 1, 1])), [0, .12, .3]);
  const pl = [{ pos: [-.55, 1.95, -.9], col: L.lampu, r: 4.8 }, { pos: eyeW, col: [.35 * ar.nyala, .85 * ar.nyala, 1.5 * ar.nyala], r: 1.1 }];
  const fade = Math.min(u(T, 0, 1), 1 - u(T, 45.6, 46.6) * .88, 1 - u(T, DUR - .5, DUR));
  R.gambar({ objek: obj, cam, sun: L.sun, sunTarget: [.2, .8, -1.4], sunSize: 3.6, sky: L.sky, ground: L.ground, fog: L.fog, pl, rim: L.rim, t: T,
    rayPos: [D.WX, 1.7, -3.3], post: { ...L.post, fade } });
  // title
  X.setTransform(1, 0, 0, 1, 0, 0); X.clearRect(0, 0, tk.width, tk.height);
  // subtitles
  { const s = tk.width / (potret ? 720 : 1280); for (const [a0, b0, teks] of SUB) { const al = Math.min(u(T, a0, a0 + .45), 1 - u(T, b0 - .45, b0)); if (al <= 0) continue;
    X.save(); X.globalAlpha = al; X.textAlign = 'center'; X.textBaseline = 'middle'; X.font = `500 ${Math.round((potret ? 27 : 26) * s)}px system-ui, -apple-system, "Segoe UI", sans-serif`;
    let maks = (potret ? 620 : 1000) * s; const tot = X.measureText(teks + ' ').width; if (tot > maks) maks = tot / Math.ceil(tot / maks) * 1.12; const kata = teks.split(' '), baris = [[]]; let w = 0; for (const k of kata) { const lw = X.measureText(k + ' ').width; if (w + lw > maks && baris[baris.length - 1].length) { baris.push([]); w = 0; } baris[baris.length - 1].push(k); w += lw; }
    const y0 = tk.height * (potret ? .8 : .86), lh = (potret ? 38 : 34) * s;
    baris.forEach((b, i) => { const tx = b.join(' '), yy = y0 + (i - (baris.length - 1) / 2) * lh; X.shadowColor = 'rgba(0,0,0,.85)'; X.shadowBlur = 10 * s; X.lineJoin = 'round'; X.lineWidth = 4 * s; X.strokeStyle = 'rgba(0,0,0,.45)'; X.strokeText(tx, tk.width / 2, yy); X.fillStyle = '#fff4dc'; X.fillText(tx, tk.width / 2, yy); });
    X.restore(); } }
  const a = u(T, 46.4, 47.4) * (1 - u(T, DUR - .5, DUR)); if (a > 0) { const s = tk.width / (potret ? 720 : 1280); X.save(); X.globalAlpha = a; X.textAlign = 'center'; X.textBaseline = 'middle';
    X.fillStyle = '#f7efe2'; X.font = `600 ${Math.round((potret ? 64 : 72) * s)}px system-ui, sans-serif`; X.shadowColor = 'rgba(127,212,255,.6)'; X.shadowBlur = 24 * s; X.fillText('Little Light', tk.width / 2, tk.height * .46);
    X.shadowBlur = 0; X.globalAlpha = a * u(T, 47.2, 48); X.fillStyle = 'rgba(247,239,226,.8)'; X.font = `500 ${Math.round(20 * s)}px system-ui, sans-serif`; X.fillText('a tiny robot, a tiny sprout, a little light', tk.width / 2, tk.height * .46 + 62 * s); X.restore(); }
}
const bMain = document.getElementById('bMain'), mulaiEl = document.getElementById('mulai'), isi = document.getElementById('isi'), waktuEl = document.getElementById('waktu'), bar = document.getElementById('bar');
function setMain(v) { main = v; bMain.textContent = v ? '❚❚' : '▶'; bMain.setAttribute('aria-label', v ? 'Pause' : 'Play'); if (A) v ? A.resume() : A.suspend(); }
function putar(dariAwal) { if (!R) return; siapAudio(); mulaiEl.hidden = true; if (dariAwal || T >= DUR - .01) { T = 0; tSebelum = 0; } setMain(true); }
function bingkai(t0) {
  const dt = Math.min((t0 - lalu) / 1000, .05); lalu = t0;
  if (main) { T += dt; if (T >= DUR) { T = DUR; setMain(false); } if (A) for (const [w, f] of ACARA) if (tSebelum < w && w <= T) f(A.currentTime + .02); musik(T, main); }
  ambiens(T, main); tSebelum = T;
  if (R) render();
  isi.style.width = (T / DUR * 100) + '%'; waktuEl.textContent = `${T.toFixed(1)} / ${DUR.toFixed(1)}`;
  requestAnimationFrame(bingkai);
}
document.getElementById('bMulai').onclick = () => putar(true);
bMain.onclick = () => main ? setMain(false) : putar(false);
document.getElementById('bUlang').onclick = () => putar(true);
bar.onclick = e => { const r = bar.getBoundingClientRect(); T = klem((e.clientX - r.left) / r.width) * DUR; tSebelum = T; if (!main) putar(false); };
bar.onkeydown = e => { if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { T = klem(T + (e.key === 'ArrowRight' ? 3 : -3), 0, DUR); tSebelum = T; } };
addEventListener('keydown', e => { if (e.key === ' ' && e.target.tagName !== 'BUTTON') { e.preventDefault(); main ? setMain(false) : putar(false); } });
function gantiFormat(f) { FORMAT = f; document.body.classList.toggle('v916', f === '916'); document.querySelectorAll('[data-format]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.format === f))); ukur(); }
document.querySelectorAll('[data-format]').forEach(b => b.onclick = () => gantiFormat(b.dataset.format));
gantiFormat(KONFIG_AWAL.format);
window.__video = { lompat: t => { T = t; tSebelum = t; }, format: gantiFormat, render: () => R && render() };
requestAnimationFrame(bingkai);
})();
</script>
</body></html>
'''

html = HTML_ANIMATION.replace("const KONFIG_AWAL = { format: '916' };", f"const KONFIG_AWAL = {{ format: '{FORMAT}' }};")
components.html(html, height=1060 if FORMAT == "916" else 760, scrolling=False)
st.caption("Press ▶ Play with sound on, then screen-record for TikTok / YouTube. Needs a browser with WebGL2 (any recent Chrome, Edge, Firefox or Safari).")
