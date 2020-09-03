class Renderer:
    def __init__(self, height, width, config):
        self.height = height
        self.width = width
        self.pos, self.sym = config.coordinates, config.symbols
        self.content = [[" "] * self.width for n in range(self.height - 1)]
        self.zbuffer = [[10000.0] * self.width for n in range(self.height - 1)]
        self.zoom = 1.0
        self.draw_scene()

    def draw_scene(self):
        mx, my = round(self.width / 2), round(self.height / 2)
        self.clear()
        for n, atm in enumerate(self.sym):
            x, y, z = self.pos[n]
            xp, yp = round(x * self.zoom + mx), round(y * self.zoom + my)
            if 0 < xp < self.width - 1 and 0 < yp < self.height - 1 and z < self.zbuffer[yp][xp]:
                self.zbuffer[yp][xp] = z
                self.content[yp][xp] = atm[0]
        return True

    def clear(self):
        for i in range(self.height - 1):
            for j in range(self.width):
                self.zbuffer[i][j] = 10000.0
        for i in range(self.height - 1):
            for j in range(self.width):
                if i == 0 and j == 0:
                    self.content[i][j] = "┌"
                elif (i == 0 or i == self.height - 2) and 0 < j < self.width - 1:
                    self.content[i][j] = "─"
                elif i == 0 and j == self.width - 1:
                    self.content[i][j] = "┐"
                elif i < self.height - 2 and (j == 0 or j == self.width - 1):
                    self.content[i][j] = "│"
                elif i == self.height - 2 and j == 0:
                    self.content[i][j] = "└"
                elif i == self.height - 2 and j == self.width - 1:
                    self.content[i][j] = "┘"
                else:
                    self.content[i][j] = " "
