import pygame
import sys

from const import *
from game import Game
from winTester import winTester

class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
        pygame.display.set_caption('Chess')
        self.game = Game()
        self.game_state = "start_menu"
        self.player_color = "white"

    def mainloop(self):

        while True:
            self.play_game()
    def play_game(self):
        # show methods
        self.game.show_bg(self.screen)
        self.game.show_last_move(self.screen)
        self.game.show_moves(self.screen)
        self.game.show_pieces(self.screen)
        self.game.show_hover(self.screen)

        possible_win = winTester(self.game.board.state)
        if possible_win != "No win":
            self.end_game(self.screen, possible_win)

        if self.game.dragger.dragging:
            self.game.dragger.update_blit(self.screen)

        for event in pygame.event.get():

            # click
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.game.dragger.update_mouse(event.pos)

                clicked_row = self.game.dragger.mouseY // SQSIZE
                clicked_col = self.game.dragger.mouseX // SQSIZE

                # if clicked square has a piece, we want to find its moves
                if self.game.board.state.board[clicked_row][clicked_col] != 0:
                    piece = self.game.board.piece_table[clicked_row][clicked_col]
                    # valid piece (color) ?
                    if piece.color == self.game.next_player:
                        self.game.board.calc_moves(piece, clicked_row, clicked_col)
                        self.game.dragger.save_initial(event.pos)
                        self.game.dragger.drag_piece(piece)
                        # show methods
                        self.game.show_bg(self.screen)
                        self.game.show_last_move(self.screen)
                        self.game.show_moves(self.screen)
                        self.game.show_pieces(self.screen)

            # mouse motion
            elif event.type == pygame.MOUSEMOTION:
                motion_row = event.pos[1] // SQSIZE
                motion_col = event.pos[0] // SQSIZE

                if motion_col < 8:
                    self.game.set_hover(motion_row, motion_col)

                    if self.game.dragger.dragging:
                        self.game.dragger.update_mouse(event.pos)
                        # show methods
                        self.game.show_bg(self.screen)
                        self.game.show_last_move(self.screen)
                        self.game.show_moves(self.screen)
                        self.game.show_pieces(self.screen)
                        self.game.show_hover(self.screen)
                        self.game.dragger.update_blit(self.screen)

            # click release
            elif event.type == pygame.MOUSEBUTTONUP:

                if self.game.dragger.dragging:
                    self.game.dragger.update_mouse(event.pos)

                    released_row = self.game.dragger.mouseY // SQSIZE
                    released_col = self.game.dragger.mouseX // SQSIZE

                    # create possible move
                    initial = (self.game.dragger.initial_row, self.game.dragger.initial_col)
                    final = (released_row, released_col)

                    move = (initial, final)
                    if self.game.board.valid_move(self.game.dragger.piece, move):
                        # This is changing the states, it's the make move
                        self.game.board.move(self.game.dragger.piece, move)

                        # sounds
                        self.game.play_sound()
                        # show methods
                        self.game.show_bg(self.screen)
                        self.game.show_last_move(self.screen)
                        self.game.show_pieces(self.screen)

                        # next turn
                        self.game.next_turn()

                self.game.dragger.undrag_piece()

            # quit application
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()

    def end_game(self, screen, possible_win):
        font = pygame.font.SysFont('monospace', 90, bold=True)
        blue = (52, 140, 235)
        text = font.render(possible_win, True, blue)
        text = pygame.transform.rotate(text, 45)
        textRect = text.get_rect()
        screen.blit(text, textRect)
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()


main = Main()
main.mainloop()