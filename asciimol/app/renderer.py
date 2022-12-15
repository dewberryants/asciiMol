import numpy as np


class Renderer:
    def __init__(self, height, width, config):
        self.height = height
        self.width = width
        self.content = dict()
        self.m = None
        self.f = 1.0
        self.resize(height, width)

        self.config = config
        self.btoggle = len(self.config.bonds) > 0
        self.pos = np.array(self.config.coordinates)

        self.ztoggle = False
        self.zoom = 1.0
        self.rot = np.identity(3)
        self.rotcounter = [0, 0, 0]
        self.reset_view()
        self.buffer_scene()

        self.auto_rotate_flags = np.array([False, False, False])

    def buffer_scene(self):
        """
        A super simple rasterizer. For now, just draw single character atom symbols at their rounded x and y
        positions.

        :return: True if nothing bad happened.
        """
        mx, my = self.m
        rot = np.matmul(self.pos, self.rot)
        self.clear()
        # Draw bonds
        for bond in self.config.bonds:
            i, j = bond
            # if bond is (i, j) with i == j, just draw the label (no bonds)
            if i == j:
                x, y, z = rot[i]
                xp, yp = round(float(x) * self.f * self.zoom + mx), round(float(y) * self.zoom + my)
                zbuf = self.content[yp, xp][2] if (yp, xp) in self.content else float("inf")
                if 1 < xp < self.width - 2 and 1 < yp < self.height - 3 and float(z) < zbuf:
                    self.content[yp, xp] = (self.config.symbols[0].upper(), self.config.colors[i], float(z))
            # else draw the bond with the labels at the end points
            else:
                # Draw the two labels at the end points
                xa, ya, za = rot[i]
                xa = float(xa) * self.f * self.zoom + mx
                ya = float(ya) * self.zoom + my
                xb, yb, zb = rot[j]
                xb = float(xb) * self.f * self.zoom + mx
                yb = float(yb) * self.zoom + my
                xap, yap = round(xa), round(ya)
                xbp, ybp = round(xb), round(yb)
                zbuf = self.content[yap, xap][2] if (yap, xap) in self.content else float("inf")
                if 1 < xap < self.width - 2 and 1 < yap < self.height - 3 and float(za) < zbuf:
                    self.content[yap, xap] = (self.config.symbols[i].upper(), self.config.colors[i], float(za))
                zbuf = self.content[ybp, xbp][2] if (ybp, xbp) in self.content else float("inf")
                if 1 < xbp < self.width - 2 and 1 < ybp < self.height - 3 and float(zb) < zbuf:
                    self.content[ybp, xbp] = (self.config.symbols[j].upper(), self.config.colors[j], float(zb))
                if not self.btoggle:
                    continue
                # Then start at xap+1 and go to xbp-1, drawing line segments
                sy = -1 if ya > yb else 1
                sx = -1 if xa > xb else 1
                sz = -1 if za > zb else 1
                dx = float((xb - xa) / (yb - ya)) if abs(yb - ya) > 0 else 0
                dy = float((yb - ya) / (xb - xa)) if abs(xb - xa) > 0 else 0
                dz = float((zb - za) / (xb - xa)) if abs(xb - xa) > 0 else 0
                if abs(dy) <= 1:
                    for k in range(1, abs(xap - xbp)):
                        xk = xap + sx * k
                        yk = round(float(ya) + sx * k * dy)
                        zk = round((float(za) + sz * k * dz))
                        zbuf = self.content[yk, xk][2] if (yk, xk) in self.content else float("inf")
                        if 1 < xk < self.width - 2 and 1 < yk < self.height - 3 and float(zk) < zbuf:
                            col = self.config.colors[i] if k < abs(xap - xbp) / 2 else self.config.colors[j]
                            self.content[yk, xk] = ("·", col, float(zk))
                else:
                    for k in range(1, abs(yap - ybp)):
                        xk = round((float(xa) + sy * k * dx))
                        yk = yap + sy * k
                        zk = round((float(za) + sz * k * dz))
                        zbuf = self.content[yk, xk][2] if (yk, xk) in self.content else float("inf")
                        if 1 < xk < self.width - 2 and 1 < yk < self.height - 3 and float(zk) < zbuf:
                            col = self.config.colors[i] if k < abs(yap - ybp) / 2 else self.config.colors[j]
                            self.content[yk, xk] = ("·", col, float(zk))
        return True

    def toggle_auto_rotate(self, x=False, y=False, z=False):
        self.auto_rotate_flags[[x, y, z]] = not all(self.auto_rotate_flags[[x, y, z]])

    def get_auto_rotate(self):
        return any(self.auto_rotate_flags)

    def auto_rotate(self):
        if self.auto_rotate_flags[0]:
            self.rotate(x=0.32)
        if self.auto_rotate_flags[1]:
            self.rotate(y=0.32)
        if self.auto_rotate_flags[2]:
            self.rotate(z=0.32)

    def rotate(self, x=0.0, y=0.0, z=0.0):
        """
        Set an internal rotation matrix that is applied to the coordinates before every render.
        """
        if abs(x) > 0:
            increment = np.pi / 36 * x
            sine = np.sin(increment)
            cosine = np.cos(increment)
            self.rot = np.matmul(self.rot, [[1.0, 0.0, 0.0], [0.0, cosine, -sine], [0.0, sine, cosine]])
            if self.rotcounter[0] + 5 * x > 360:
                self.rotcounter[0] -= 360
            elif self.rotcounter[0] + 5 * x < 0:
                self.rotcounter[0] += 360
            self.rotcounter[0] += 5 * x
        if abs(y) > 0:
            increment = np.pi / 36 * y
            sine = np.sin(increment)
            cosine = np.cos(increment)
            self.rot = np.matmul(self.rot, [[cosine, 0.0, sine], [0.0, 1.0, 0.0], [-sine, 0.0, cosine]])
            if self.rotcounter[1] + 5 * y > 360:
                self.rotcounter[1] -= 360
            elif self.rotcounter[1] + 5 * y < 0:
                self.rotcounter[1] += 360
            self.rotcounter[1] += 5 * y
        if abs(z) > 0:
            increment = np.pi / 36 * z
            sine = np.sin(increment)
            cosine = np.cos(increment)
            self.rot = np.matmul(self.rot, [[cosine, -sine, 0.0], [sine, cosine, 0.0], [0.0, 0.0, 1.0]])
            if self.rotcounter[2] + 5 * z > 360:
                self.rotcounter[2] -= 360
            elif self.rotcounter[2] + 5 * z < 0:
                self.rotcounter[2] += 360
            self.rotcounter[2] += 5 * z
        return abs(x) > 0 or abs(y) > 0 or abs(z) > 0

    def navigate(self, dx=0, dy=0):
        """
        Navigate the view so that the new mid point sits at (x + dx, y + dy).
        """
        x, y = self.m
        self.m = (x + dx, y + dy)
        return True

    def modify_zoom(self, factor):
        if self.zoom + factor > 0.2:
            self.zoom += factor
            return True
        return False

    def reset_view(self):
        """
        Reset the view to the starting values.
        """
        self.rotcounter = [0, 0, 0]
        self.rot = np.identity(3)
        self.m = round((self.width - 2) / 2), round((self.height - 2) / 2)
        self.pos = np.array(self.config.coordinates)
        self.center()
        dx = np.max(self.pos[:, 0]) - np.min(self.pos[:, 0])
        dy = np.max(self.pos[:, 1]) - np.min(self.pos[:, 1])
        fx = 0.9 * self.m[0] / (2.25 * dx)
        fy = 0.9 * self.m[1] / dy
        self.zoom = fx if fx > fy else fy
        return True

    def resize(self, height, width):
        """
        Resize the screen. Known issue: crashes if the resize is faster than the framerate.
        """
        self.height = height
        self.width = width
        self.m = round((self.width - 2) / 2), round((self.height - 2) / 2)
        # Since terminal characters are higher than wide, I correct for this by multiplying the x by f
        # so that it appears wider. 2.25 is what looks good on my terminals, but might be
        # nice to have a general way of determining the optimal value
        self.f = 2.25

    def clear(self):
        """
        Clear the canvas and redraw the border.
        """
        self.content = dict()
        for i in range(self.height - 2):
            for j in range(self.width):
                if i == 0 and j == 0:
                    self.content[i, j] = ("┌", 0, -1)
                elif (i == 0 or i == self.height - 3) and 0 < j < self.width - 1:
                    self.content[i, j] = ("─", 0, -1)
                elif i == 0 and j == self.width - 1:
                    self.content[i, j] = ("┐", 0, -1)
                elif i < self.height - 3 and (j == 0 or j == self.width - 1):
                    self.content[i, j] = ("│", 0, -1)
                elif i == self.height - 3 and j == 0:
                    self.content[i, j] = ("└", 0, -1)
                elif i == self.height - 3 and j == self.width - 1:
                    self.content[i, j] = ("┘", 0, -1)

    def center(self):
        """
        Move the internal coordinate matrix to the center of coordinates
        """
        center = 1.0 / self.pos.shape[0] * np.sum(self.pos, axis=0)
        self.pos -= center
        return True

    def prinicple_axes(self):
        """
        Transform to principle axes of rotation
        """
        self.center()
        x, y, z = np.transpose(self.pos)
        xx = np.sum(y * y + z * z)
        yy = np.sum(x * x + z * z)
        zz = np.sum(x * x + y * y)
        xy = -np.sum(x * y)
        yz = -np.sum(y * z)
        xz = -np.sum(x * z)
        i = np.array([[xx, xy, xz], [xy, yy, yz], [xz, yz, zz]])
        w, t = np.linalg.eig(i)
        # Einstein Summation: for the 3x3 matrix t, multiply row j with each of the k rows in pos and sum
        # this is essentially just a basis transformation to the principle axes coordinate system.
        self.pos = np.einsum('ij,kj->ki', np.linalg.inv(t), self.pos)
        return True
