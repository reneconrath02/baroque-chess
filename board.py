from const import *
from piece import *
import Caissa_BC_Player_Move_Generator as MG
import Caissa_BC_Player as Caissa
from BC_state_etc import *
from sound import Sound
import copy
import os

class Board:

    def __init__(self):
        self.state = BC_state(INITIAL, WHITE)
        self.piece_table = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self.last_move = None
        self._create()
        self.init_add_pieces('white')
        self.init_add_pieces('black')

    def move(self, piece, move):
        Caissa.applyMove(self.state, 0, move)

        self.piece_table[move[0][0]][move[0][1]] = None
        self.piece_table[move[1][0]][move[1][1]] = piece

        # move
        piece.moved = True

        # clear valid moves
        piece.clear_moves()

        # set last move
        self.last_move = move

    def valid_move(self, piece, move):
        end_move = move[1]
        return end_move in piece.moves

    def calc_moves(self, piece, row, col):
        '''
            Calculate all the possible (valid) moves of a specific piece on a specific position
        '''
        piece.clear_moves()
        all_moves = MG.findMoves(self.state)
        if all_moves.get((row, col)) is not None:
            for move in all_moves.get((row, col)):
                piece.add_move(move)
        # for move in all_moves[(row, col)]:
        #     piece.add_move(move)

    def _create(self):
        self.state = BC_state(INITIAL, WHITE)

    def init_add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)

        # put pincers on the board
        for col in range(COLS):
            self.piece_table[row_pawn][col] = Pincer(color)

        # leaper
        self.piece_table[row_other][1] = Leaper(color)
        self.piece_table[row_other][6] = Leaper(color)

        # imitator
        self.piece_table[row_other][2] = Imitator(color)
        self.piece_table[row_other][5] = Imitator(color)

        # coordinator/freezer
        self.piece_table[7][0] = Freezer('white')
        self.piece_table[7][7] = Coordinator('white')

        self.piece_table[0][7] = Freezer('black')
        self.piece_table[0][0] = Coordinator('black')

        # withdrawer
        self.piece_table[row_other][3] = Withdrawer(color)

        # king
        self.piece_table[row_other][4] = King(color)