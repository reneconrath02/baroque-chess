from BC_state_etc import *
from random import randint

S = 64
P = 14

zobristnum = [[0]*P for i in range(S)]

# initializes zobrist numbers
def zb_init():
    for i in range(S):
        for j in range(P):
            zobristnum[i][j] = randint(0, 4294967296)

# calculates the zobrist number of a board
def zhash(board):
    val = 0
    for i in range(S):
        piece = board[i//8][i%8]
        if piece != 0:
            znum = zobristnum[i][piece-2]
            val ^= znum
    return val

# modifies the zobrist number to move the piece on the first coord
#  to the second coordinate. Assumes the second coord is empty
def zmove(board, znum, move):
    piece = board[move[0][0]][move[0][1]] - 2
    znum ^= zobristnum[move[0][0]*8 + move[0][1]][piece]
    znum ^= zobristnum[move[1][0]*8 + move[1][1]][piece]
    return znum

# modifies the zobrist number to remove the piece on the given tile
def zcapture(board, znum, coord):
    piece = board[coord[0]][coord[1]] - 2
    znum ^= zobristnum[coord[0]*8 + coord[1]][piece]
    return znum

if __name__ == "__main__":
    zb_init()
    print(zobristnum)
    init_state = BC_state(INITIAL, WHITE)
    print(zhash(init_state.board))
