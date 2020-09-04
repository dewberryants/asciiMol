import numpy as np


class Renderer:
    def __init__(self, height, width, config):
        self.height = height
        self.width = width
        self.colors = config.colors
        self.pos, self.sym = np.array(config.coordinates), config.symbols
        self.content = [[" ,0"] * self.width for n in range(self.height - 1)]
        self.zbuffer = [[10000.0] * self.width for n in range(self.height - 1)]
        self.ztoggle = True
        self.zoom = 1.0
        self.rot = np.identity(3)
        self.rotcounter = [0, 0, 0]
        self.draw_scene()

    def draw_scene(self):
        mx, my = round(self.width / 2), round(self.height / 2)
        rot = np.matmul(self.pos, self.rot)
        self.clear()
        for n, atm in enumerate(self.sym):
            x, y, z = rot[n]
            xp, yp = round(float(x) * self.zoom + mx), round(float(y) * self.zoom + my)
            if 1 < xp < self.width - 2 and 1 < yp < self.height - 2 and float(z) < self.zbuffer[yp][xp]:
                self.zbuffer[yp][xp] = float(z)
                self.content[yp][xp] = atm[0].upper() + "," + self.colors[atm[0]]
        return True

    def rotate(self, direction):
        if direction == 1:
            self.rot = np.matmul(self.rot, [[1.0, 0.0, 0.0], [0.0, 0.9962, -0.0872], [0.0, 0.0872, 0.9962]])
            if self.rotcounter[0] + 5 > 360:
                self.rotcounter[0] = 0
            self.rotcounter[0] += 5
        elif direction == -1:
            self.rot = np.matmul(self.rot, [[1.0, 0.0, 0.0], [0.0, 0.9962, 0.0872], [0.0, -0.0872, 0.9962]])
            if self.rotcounter[0] - 5 < 0:
                self.rotcounter[0] = 360
            self.rotcounter[0] -= 5
        elif direction == 2 and self.ztoggle:
            self.rot = np.matmul(self.rot, [[0.9962, -0.0872, 0.0], [0.0872, 0.9962, 0.0], [0.0, 0.0, 1.0]])
            if self.rotcounter[2] + 5 > 360:
                self.rotcounter[2] = 0
            else:
                self.rotcounter[2] += 5
        elif direction == -2 and self.ztoggle:
            self.rot = np.matmul(self.rot, [[0.9962, 0.0872, 0.0], [-0.0872, 0.9962, 0.0], [0.0, 0.0, 1.0]])
            if self.rotcounter[2] - 5 < 0:
                self.rotcounter[2] = 360
            else:
                self.rotcounter[2] -= 5
        elif direction == 2:
            self.rot = np.matmul(self.rot, [[0.9962, 0.0, 0.0872], [0.0, 1.0, 0.0], [-0.0872, 0.0, 0.9962]])
            if self.rotcounter[1] + 5 > 360:
                self.rotcounter[1] = 0
            else:
                self.rotcounter[1] += 5
        elif direction == -2:
            self.rot = np.matmul(self.rot, [[0.9962, 0.0, -0.0872], [0.0, 1.0, 0.0], [0.0872, 0.0, 0.9962]])
            if self.rotcounter[1] - 5 < 0:
                self.rotcounter[1] = 360
            else:
                self.rotcounter[1] -= 5

    def reset_view(self):
        self.zoom = 1.0
        self.rotcounter = [0, 0, 0]
        self.rot = np.identity(3)

    def resize(self, height, width):
        self.height = height
        self.width = width
        self.content = [[" ,0"] * self.width for n in range(self.height - 1)]
        self.zbuffer = [[10000.0] * self.width for n in range(self.height - 1)]

    def clear(self):
        for i in range(self.height - 1):
            for j in range(self.width):
                self.zbuffer[i][j] = 10000.0
        for i in range(self.height - 1):
            for j in range(self.width):
                if i == 0 and j == 0:
                    self.content[i][j] = "┌,0"
                elif (i == 0 or i == self.height - 2) and 0 < j < self.width - 1:
                    self.content[i][j] = "─,0"
                elif i == 0 and j == self.width - 1:
                    self.content[i][j] = "┐,0"
                elif i < self.height - 2 and (j == 0 or j == self.width - 1):
                    self.content[i][j] = "│,0"
                elif i == self.height - 2 and j == 0:
                    self.content[i][j] = "└,0"
                elif i == self.height - 2 and j == self.width - 1:
                    self.content[i][j] = "┘,0"
                else:
                    self.content[i][j] = " ,0"
