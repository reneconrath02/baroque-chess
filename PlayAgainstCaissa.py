import pygame
import sys

from const import *
from game import Game
from BC_state_etc import *
from chat import Chat
import Caissa_BC_Player_Transparant as Caissa
from winTester import winTester

CAISSA_TIME_LIMIT = 3
class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Chess')
        self.game = Game()
        # If we don't do this, we crash because we initialize tracking dict there
        self.chat = Chat()
        Caissa.prepare("Human player")
        self.game_state = "start_menu"
        self.player_color = "white"

    def mainloop(self):

        while True:
            if self.game_state == "start_menu":
                self.draw_start_menu()
            else:
                self.play_game()
    def play_game(self):
        # show methods
        self.game.show_bg(self.screen)
        self.game.show_last_move(self.screen)
        self.game.show_moves(self.screen)
        self.game.show_pieces(self.screen)
        self.game.show_hover(self.screen)
        self.chat.show_message(self.screen)

        possible_win = winTester(self.game.board.state)
        if possible_win != "No win":
            end_game(self.screen, possible_win)

        if (self.player_color == "white" and self.game.board.state.whose_move == WHITE) or \
                (self.player_color == "black" and self.game.board.state.whose_move == BLACK):
            self.run_player_side()
        else:
            pygame.display.update()
            caissa_move = Caissa.makeMove(self.game.board.state, "hi", self.screen, CAISSA_TIME_LIMIT)
            # form of ((6, 0), (2, 0))
            move = caissa_move[0][0]
            piece = self.game.board.piece_table[move[0][0]][move[0][1]]

            # the following method is what is changing the board state
            self.game.board.move(piece, move)

            # After the move is made, we look at the current board evaluation, and generate a comment
            polarity = [1, -1]
            eval = Caissa.staticEval(self.game.board.state) * polarity[self.game.board.state.whose_move]
            self.chat.new_message(eval)

            # play sound
            self.game.play_sound()
            # show the move
            self.game.show_bg(self.screen)
            self.game.show_last_move(self.screen)
            self.game.show_pieces(self.screen)
            # next turn
            self.game.next_turn()

        pygame.display.update()

    def run_player_side(self):
        # This constantly checks for the player input (event)
        # If the player gives certain input, like mouse down, mouse release,
        # the game reacts accordingly
        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger

        if dragger.dragging:
            dragger.update_blit(screen)

        for event in pygame.event.get():

            # click
            if event.type == pygame.MOUSEBUTTONDOWN:
                dragger.update_mouse(event.pos)

                clicked_row = dragger.mouseY // SQSIZE
                clicked_col = dragger.mouseX // SQSIZE

                # if clicked square has a piece, we want to find its moves
                if board.state.board[clicked_row][clicked_col] != 0:
                    piece = board.piece_table[clicked_row][clicked_col]
                    # we first check to see if we are the active player
                    if piece.color == game.next_player:
                        board.calc_moves(piece, clicked_row, clicked_col)
                        dragger.save_initial(event.pos)
                        dragger.drag_piece(piece)

                        # show methods
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)

            # mouse motion
            elif event.type == pygame.MOUSEMOTION:
                motion_row = event.pos[1] // SQSIZE
                motion_col = event.pos[0] // SQSIZE

                if motion_col < 8:
                    # if our mouse is hovering inside the board, highlight the square
                    game.set_hover(motion_row, motion_col)

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        # show methods
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        game.show_hover(screen)
                        dragger.update_blit(screen)

            # click release
            elif event.type == pygame.MOUSEBUTTONUP:

                if dragger.dragging:
                    dragger.update_mouse(event.pos)

                    released_row = dragger.mouseY // SQSIZE
                    released_col = dragger.mouseX // SQSIZE

                    # create possible move
                    initial = (dragger.initial_row, dragger.initial_col)
                    final = (released_row, released_col)

                    move = (initial, final)
                    if board.valid_move(dragger.piece, move):
                        # if the move is valid, we run
                        # the following method to change the board state
                        board.move(dragger.piece, move)

                        # sound
                        game.play_sound()
                        # show methods
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_pieces(screen)

                        # next turn
                        game.next_turn()

                dragger.undrag_piece()

            # quit application
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def draw_start_menu(self):
        color_white = (255,255,255)
        # light shade of the button
        color_light = (170,170,170)
        # dark shade of the button
        color_dark = (100,100,100)
        smallfont = pygame.font.SysFont('Corbel',35)
        text_play_as_white = smallfont.render('I want to play as white!', True, color_white)
        text_play_as_black = smallfont.render('I want to play as black!', True, color_white)
        white_button_top = HEIGHT / 2
        black_button_top = HEIGHT / 2 + 80
        button_left = WIDTH / 6
        button_height = 40
        button_width = 325

        # Background is purple
        self.screen.fill((60, 25, 60))
        mouse = pygame.mouse.get_pos()

        for ev in pygame.event.get():

            if ev.type == pygame.QUIT:
                pygame.quit()

            # checks if a mouse is clicked
            if ev.type == pygame.MOUSEBUTTONDOWN:

                # if the mouse is clicked on the
                # button, the game will start
                if button_left <= mouse[0] <= button_left+button_width and \
                        white_button_top <= mouse[1] <= white_button_top+button_height:
                    self.game_state = "game"
                if button_left <= mouse[0] <= button_left+button_width and \
                        black_button_top <= mouse[1] <= black_button_top+button_height:
                    self.player_color = "black"
                    self.game_state = "game"

        if button_left <= mouse[0] <= button_left+button_width and \
                white_button_top <= mouse[1] <= white_button_top+button_height:
            pygame.draw.rect(self.screen,color_light,[button_left,white_button_top,button_width,button_height])
        else:
            pygame.draw.rect(self.screen,color_dark,[button_left,white_button_top,button_width,button_height])

        if button_left <= mouse[0] <= button_left+button_width and \
                black_button_top <= mouse[1] <= black_button_top+button_height:
            pygame.draw.rect(self.screen,color_light,[button_left,black_button_top,button_width,button_height])
        else:
            pygame.draw.rect(self.screen,color_dark,[button_left,black_button_top,button_width,button_height])

        # superimposing the text onto our button
        self.screen.blit(text_play_as_white , (button_left,white_button_top))
        self.screen.blit(text_play_as_black , (button_left,black_button_top))

        # updates the frames of the game
        pygame.display.update()

def end_game(screen, possible_win):
    font = pygame.font.SysFont('monospace', 90, bold=True)
    blue = (52, 140, 235)
    text = font.render(possible_win, True, blue)
    text = pygame.transform.rotate(text, 45)
    textRect = text.get_rect()
    screen.blit(text, textRect)
    pygame.display.update()

    # Once the game ends, you can only exit
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


main = Main()
main.mainloop()