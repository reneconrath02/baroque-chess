import pygame

from const import *
from board import Board
from dragger import Dragger
from config import Config


class Game:

    def __init__(self):
        self.next_player = 'white'
        self.hovered_sqr = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()

    # blit methods
    def show_bg(self, surface):
        theme = self.config.theme
        
        for row in range(ROWS):
            for col in range(COLS):
                # color
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark
                # rect
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

                # row coordinates
                if col == 0:
                    # color
                    color = theme.bg.dark if row % 2 == 0 else theme.bg.light
                    # label
                    lbl = self.config.font.render(str(row), 1, color)
                    lbl_pos = (5, 5 + row * SQSIZE)
                    # blit
                    surface.blit(lbl, lbl_pos)

                # col coordinates
                if row == 7:
                    # color
                    color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                    # label
                    lbl = self.config.font.render(str(col), 1, color)
                    lbl_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
                    # blit
                    surface.blit(lbl, lbl_pos)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                # if there is a piece there, we want to show it
                if self.board.state.board[row][col] != 0:

                    piece = self.board.piece_table[row][col]
                    # we want the object, hence made a piece table
                    # all pieces except dragger piece
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    # When we click a piece, we want to highlight the moves that piece can make
    def show_moves(self, surface):
        theme = self.config.theme

        if self.dragger.dragging:
            piece = self.dragger.piece

            # loop all valid moves
            for move in piece.moves:
                # color
                color = theme.moves.light if (move[0] + move[1]) % 2 == 0 else theme.moves.dark
                # rect
                # note the ordering (L)
                rect = (move[1] * SQSIZE, move[0] * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface):
        theme = self.config.theme

        if self.board.last_move:
            # form of ((6, 0), (4, 0))
            move = self.board.last_move

            # note the worser ordering
            color = theme.trace.light if (move[0][1] + move[0][0]) % 2 == 0 else theme.trace.dark
            rect = (move[0][1] * SQSIZE, move[0][0] * SQSIZE, SQSIZE, SQSIZE)
            pygame.draw.rect(surface, color, rect)

            color = theme.trace.light if (move[1][0] + move[1][1]) % 2 == 0 else theme.trace.dark
            rect = (move[1][1] * SQSIZE, move[1][0] * SQSIZE, SQSIZE, SQSIZE)
            pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_sqr:
            # color
            color = (180, 180, 180)
            # rect
            # ordering is just this way, ye? Ye
            rect = (self.hovered_sqr[1] * SQSIZE, self.hovered_sqr[0] * SQSIZE, SQSIZE, SQSIZE)
            # blit
            pygame.draw.rect(surface, color, rect, width=3)

    # other methods
    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def set_hover(self, row, col):
        self.hovered_sqr = (row, col)

    def play_sound(self):
        self.config.move_sound.play()

    def reset(self):
        self.__init__()