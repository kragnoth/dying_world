"""Tiny orthographic software renderer for Minecraft-style models (OBJ + block cuboids), real textures, nearest sampling."""
import math
import numpy as np
from PIL import Image


def load_tex(path):
    im = Image.open(path).convert('RGBA')
    return np.asarray(im).astype(np.float32) / 255.0


class Scene:
    def __init__(self):
        self.tris = []          # (P[3x3], UV[3x2], tex, tint)

    def add_tri(self, p, uv, tex, shade=None):
        self.tris.append((np.asarray(p, np.float64), np.asarray(uv, np.float64), tex, shade))

    def add_quad(self, p, uv, tex, shade=None):
        self.add_tri([p[0], p[1], p[2]], [uv[0], uv[1], uv[2]], tex, shade)
        self.add_tri([p[0], p[2], p[3]], [uv[0], uv[2], uv[3]], tex, shade)

    def add_obj(self, path, texmap, xform, flip_v=True):
        vs, vts, mat = [], [], None
        for line in open(path):
            t = line.split()
            if not t:
                continue
            if t[0] == 'v':
                vs.append(xform(np.array(list(map(float, t[1:4])))))
            elif t[0] == 'vt':
                u, v = map(float, t[1:3])
                vts.append((u, 1 - v if flip_v else v))
            elif t[0] == 'usemtl':
                mat = t[1]
            elif t[0] == 'f':
                idx = [x.split('/') for x in t[1:]]
                pts = [vs[int(a[0]) - 1] for a in idx]
                uvs = [vts[int(a[1]) - 1] for a in idx]
                for k in range(1, len(pts) - 1):
                    self.add_tri([pts[0], pts[k], pts[k + 1]], [uvs[0], uvs[k], uvs[k + 1]], texmap[mat])

    def add_box(self, lo, hi, faces, tex, xform, texsize=16):
        """Minecraft block element: lo/hi in pixels (0..16 = one block). faces: name -> (u0,v0,u1,v1) in pixels."""
        x0, y0, z0 = lo; x1, y1, z1 = hi
        corners = {
            'north': [(x1, y1, z0), (x0, y1, z0), (x0, y0, z0), (x1, y0, z0)],
            'south': [(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)],
            'west': [(x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x0, y0, z0)],
            'east': [(x1, y1, z1), (x1, y1, z0), (x1, y0, z0), (x1, y0, z1)],
            'up': [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
            'down': [(x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)],
        }
        tw = tex.shape[1]; th = tex.shape[0]
        for name, (u0, v0, u1, v1) in faces.items():
            p = [xform(np.array(c, float) / 16) for c in corners[name]]
            uv = [(u0 / tw, v0 / th), (u1 / tw, v0 / th), (u1 / tw, v1 / th), (u0 / tw, v1 / th)]
            self.add_quad(p, uv, tex)

    def render(self, W, H, cam, scale, offset, light=(-0.45, 0.8, 0.4), ss=2):
        """cam: 3x3 rotation world->view (x right, y up, z toward viewer). Ortho: screen = (x*scale+ox, -y*scale+oy)."""
        Ws, Hs = W * ss, H * ss
        color = np.zeros((Hs, Ws, 4), np.float32)
        zbuf = np.full((Hs, Ws), -1e9)
        L = np.array(light) / np.linalg.norm(light)
        for P, UV, tex, shade in self.tris:
            V = P @ cam.T
            n = np.cross(V[1] - V[0], V[2] - V[0])
            nl = np.linalg.norm(n)
            if nl < 1e-12:
                continue
            n /= nl
            wn = np.cross(P[1] - P[0], P[2] - P[0]); wn /= np.linalg.norm(wn)
            if n[2] < 0:
                wn = -wn                                        # double-sided: shade the side we see
            if shade is None:
                # Minecraft-like: up 1.0, sides 0.8/0.6, down 0.5, plus a soft directional term
                b = 0.62 + 0.30 * wn[1] + 0.12 * abs(wn[2]) + 0.10 * max(0.0, float(np.dot(wn, L)))
                b = max(0.45, min(1.05, b))
            else:
                b = shade
            sx = V[:, 0] * scale * ss + offset[0] * ss
            sy = -V[:, 1] * scale * ss + offset[1] * ss
            xmin, xmax = int(max(0, math.floor(sx.min()))), int(min(Ws - 1, math.ceil(sx.max())))
            ymin, ymax = int(max(0, math.floor(sy.min()))), int(min(Hs - 1, math.ceil(sy.max())))
            if xmin > xmax or ymin > ymax:
                continue
            xs, ys = np.meshgrid(np.arange(xmin, xmax + 1) + 0.5, np.arange(ymin, ymax + 1) + 0.5)
            d = (sy[1] - sy[2]) * (sx[0] - sx[2]) + (sx[2] - sx[1]) * (sy[0] - sy[2])
            if abs(d) < 1e-9:
                continue
            w0 = ((sy[1] - sy[2]) * (xs - sx[2]) + (sx[2] - sx[1]) * (ys - sy[2])) / d
            w1 = ((sy[2] - sy[0]) * (xs - sx[2]) + (sx[0] - sx[2]) * (ys - sy[2])) / d
            w2 = 1 - w0 - w1
            inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not inside.any():
                continue
            z = w0 * V[0, 2] + w1 * V[1, 2] + w2 * V[2, 2]
            u = w0 * UV[0, 0] + w1 * UV[1, 0] + w2 * UV[2, 0]
            v = w0 * UV[0, 1] + w1 * UV[1, 1] + w2 * UV[2, 1]
            th, tw = tex.shape[:2]
            tx = np.clip((u * tw).astype(int), 0, tw - 1)
            ty = np.clip((v * th).astype(int), 0, th - 1)
            texel = tex[ty, tx]
            sub = zbuf[ymin:ymax + 1, xmin:xmax + 1]
            m = inside & (z > sub) & (texel[..., 3] > 0.5)
            if not m.any():
                continue
            sub[m] = z[m]
            c = color[ymin:ymax + 1, xmin:xmax + 1]
            rgb = texel[..., :3] * b
            c[m, :3] = rgb[m]
            c[m, 3] = 1.0
        img = Image.fromarray((np.clip(color, 0, 1) * 255).astype(np.uint8), 'RGBA')
        return img.resize((W, H), Image.BOX) if ss > 1 else img


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
