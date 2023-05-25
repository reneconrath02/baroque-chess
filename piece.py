import os

class Piece:

    def __init__(self, name, color, value, texture=None, texture_rect=None):
        self.name = name
        self.color = color
        value_add = 1 if color == 'white' else 0
        self.value = value + value_add
        self.moves = []
        self.moved = False
        self.texture = texture
        self.set_texture()
        self.texture_rect = texture_rect

    def set_texture(self, size=80):
        self.texture = os.path.join(
            f'assets/images/imgs-{size}px/{self.color}_{self.name}.png')

    def add_move(self, move):
        self.moves.append(move)

    def clear_moves(self):
        self.moves = []

class Pincer(Piece):

    def __init__(self, color):
        super().__init__('pincer', color, 2)

class Leaper(Piece):

    def __init__(self, color):
        super().__init__('leaper', color, 6)

class Imitator(Piece):

    def __init__(self, color):
        super().__init__('imitator', color, 8)

class Freezer(Piece):

    def __init__(self, color):
        super().__init__('freezer', color, 14)

class Coordinator(Piece):

    def __init__(self, color):
        super().__init__('coordinator', color, 4)

class Withdrawer(Piece):

    def __init__(self, color):
        super().__init__('withdrawer', color, 10)

class King(Piece):

    def __init__(self, color):
        super().__init__('king', color, 12)