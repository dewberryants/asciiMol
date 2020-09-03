class Renderer:
    def __init__(self, height, width, config):
        self.height = height
        self.width = width
        self.content = self._init_content()

    def _init_content(self):
        content = [[" "] * self.width for n in range(self.height - 1)]
        for i in range(self.height - 1):
            for j in range(self.width):
                if i == 0 and j == 0:
                    content[i][j] = "┌"
                elif (i == 0 or i == self.height - 2) and 0 < j < self.width - 1:
                    content[i][j] = "─"
                elif i == 0 and j == self.width - 1:
                    content[i][j] = "┐"
                elif i < self.height - 2 and (j == 0 or j == self.width - 1):
                    content[i][j] = "│"
                elif i == self.height - 2 and j == 0:
                    content[i][j] = "└"
                elif i == self.height - 2 and j == self.width - 1:
                    content[i][j] = "┘"
        return content
