# Making the move generator, because we apparently have to do that

from BC_state_etc import *
from Caissa_BC_Player_Zobrist import *

USE_IMITATOR = True

# returns a dictionary of form {(coord of piece): [(pos. end coord), (pos. end coord)], etc}
# with each piece of the active player.
# suicide moves, defined as moves by an immobile piece (thus killing it) are not allowed.
def findMoves(state, im_allowed=True):
    global USE_IMITATOR
    USE_IMITATOR = im_allowed
    piece_coords = []
    # gets the coordinates of all pieces of the active player
    for i in range(8):
        for j in range(8):
            if state.board[i][j] != 0 and state.board[i][j] % 2 == state.whose_move:
                piece_coords.append((i,j))
    # checks immoblization of a piece--if it's immoble, no legal moves
    to_remove = []
    for piece in piece_coords:
        if check_immoble(state, piece[0], piece[1]):
            to_remove.append(piece)
    for piece in to_remove:
        piece_coords.remove(piece)
    
    moves = {}
    # generates the possible moves for each of our pieces
    for piece in piece_coords:
        piece_style = state.board[piece[0]][piece[1]]
        if piece_style == BLACK_KING or piece_style == WHITE_KING:
            moves[piece] = generate_king_move(state, piece_style, piece[0], piece[1])
            continue
        moves[piece] = generate_standard_move(state, piece_style, piece[0], piece[1])
        if USE_IMITATOR and piece_style == BLACK_IMITATOR+state.whose_move:
            moves[piece] = generate_imitator_king_move(state, piece_style, piece[0], piece[1]) + moves[piece]
      
    return moves


## takes a non-king piece and it's starting position in the current
# state, and returns all the moves it could make in a list, terminating 
# at a piece or at the edge of the board (except leapers, who
# terminate one square after an opposing piece if the tile is not
# occupied)
def generate_standard_move(state, piece, pos_h, pos_w):
    global USE_IMITATOR
    assert(piece == state.board[pos_h][pos_w])
    assert(piece % 2 == state.whose_move)

    valid_moves = []
    ordinals = [(1,0), (1, 1), (0, 1), (-1, 1),
      (-1, 0), (-1, -1), (0,-1), (1, -1)]
    if piece == BLACK_PINCER or piece == WHITE_PINCER:
       ordinals = [(1,0), (0, 1), (-1, 0), (0,-1)]
    
    for dir in ordinals:
        new_h, new_w = pos_h, pos_w
        new_h += dir[0]
        new_w += dir[1]
        while 0 <= new_h and new_h < 8 and 0 <= new_w and new_w < 8\
                and state.board[new_h][new_w] == 0:
            valid_moves.append((new_h, new_w))
            new_h += dir[0]
            new_w += dir[1]
        
        # if we're on board (stopped because we were blocked) check if we're allowed to hop that piece
        #  allowed if we're a leaper blocked by an enemy, *or* we're an imitator blocked by a leaper
        if 0 <= new_h and new_h < 8 and 0 <= new_w and new_w < 8 and\
                (((piece == BLACK_LEAPER and state.board[new_h][new_w] % 2 == WHITE)
                    or (piece == WHITE_LEAPER and state.board[new_h][new_w] % 2 == BLACK))
                or (USE_IMITATOR and 
                 ((piece == BLACK_IMITATOR and state.board[new_h][new_w] == WHITE_LEAPER)
                or (piece == WHITE_IMITATOR and state.board[new_h][new_w] == BLACK_LEAPER)))):
            new_h += dir[0]
            new_w += dir[1]
            if 0 <= new_h and new_h < 8 and 0 <= new_w and new_w < 8 and state.board[new_h][new_w] == 0:
                valid_moves.append((new_h, new_w))
    return valid_moves


def generate_king_move(state, piece, pos_h, pos_w):
    assert(piece == state.board[pos_h][pos_w])
    assert(piece % 2 == state.whose_move)

    valid_moves = []
    ordinals = [(1,0), (1, 1), (0, 1), (-1, 1),
      (-1, 0), (-1, -1), (0,-1), (1, -1)]
    
    for dir in ordinals:
        new_h, new_w = pos_h, pos_w
        new_h += dir[0]
        new_w += dir[1]
        if 0 <= new_h and new_h < 8 and 0 <= new_w and new_w < 8\
            and (state.board[new_h][new_w] % 2 == 1-state.whose_move or
                 state.board[new_h][new_w] == 0):
            valid_moves.append((new_h, new_w))
    return valid_moves

# Imitator can enter the king's square iff it is one away
def generate_imitator_king_move(state, piece, pos_h, pos_w):
    assert(piece == state.board[pos_h][pos_w])
    assert(piece % 2 == state.whose_move)

    valid_moves = []
    ordinals = [(1,0), (1, 1), (0, 1), (-1, 1),
      (-1, 0), (-1, -1), (0,-1), (1, -1)]
    
    for dir in ordinals:
        new_h, new_w = pos_h, pos_w
        new_h += dir[0]
        new_w += dir[1]
        if 0 <= new_h and new_h < 8 and 0 <= new_w and new_w < 8\
            and state.board[new_h][new_w] == WHITE_KING-state.whose_move:
          valid_moves.append((new_h, new_w))
    return valid_moves
           

def check_immoble(state, pos_h, pos_w, turn=-1, chain=True):
  global USE_IMITATOR
  ordinals = [(1,0), (1, 1), (0, 1), (-1, 1),
    (-1, 0), (-1, -1), (0,-1), (1, -1)]
  if turn == -1:
      turn = state.whose_move
  freeze = [BLACK_FREEZER, WHITE_FREEZER]
  imitator = [BLACK_IMITATOR, WHITE_IMITATOR]
  for dir in ordinals:
    new_h, new_w = pos_h, pos_w
    new_h += dir[0]
    new_w += dir[1]
    if 0 <= new_h and new_h < 8 and 0 <= new_w and new_w < 8\
         and (state.board[new_h][new_w] == freeze[1-turn] or
        # imitator chained--if enemy imitator is present, call check_immoble on *it* to det if it's copying a freezer
         (USE_IMITATOR and chain and state.board[new_h][new_w] == imitator[1-turn]
           and check_immoble(state, new_h, new_w, 1-turn, False))):
       return True
  return False

def get_random_move(state):
    possible_moves = findMoves(state)
    start_coords = list(possible_moves.keys())
    move = None
    while move is None:
        piece = start_coords[randint(0, len(start_coords)-1)]
        possible = possible_moves[piece]
        if len(possible) == 0:
            continue
        end = possible[randint(0, len(possible)-1)]
        move = (piece, end)
    return move


