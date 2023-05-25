'''Caissa_BC_Player.py
An agent that might someday play Baroque Chess.

'''

from BC_state_etc import *
import Caissa_BC_Player_Move_Generator as MG
import Caissa_BC_Player_Zobrist as ZB
from time import time

IMITATOR_CAPTURES_IMPLEMENTED = True

USE_ALPHA_BETA = True
USE_BASIC_EVAL = False
USE_ZOBRIST = False
# USE_IMITATOR = False

# of the form {znum: (state, ply_used, val)}
zb_table = {}
# of the form {znum: {possible moves, as returned by MG.findMoves}}
zb_moves = {}
# has to exist for parameterized, easier to update than check a flag each time
tracking_dict = {}
start_time = 0
tlimit = 1000

def parameterized_minimax(currentState, alphaBeta=False, ply=3,\
    useBasicStaticEval=True, useZobristHashing=False):
    '''Implement this testing function for your agent's basic
    capabilities here.'''

    # Want to return a dict with
    # 'CURRENT_STATE_VAL': The value determined for the current state.
    # 'N_STATES_EXPANDED': The number of states expanded as part of your minimax search.
    # 'N_STATIC_EVALS': The number of static evals performed as part of your minimax search
    # 'N_CUTOFFS': The number of cutoffs that occurred during the minimax search (0 if alpha-beta was not enabled)

    tracking_dict['CURRENT_STATE_VAL'] = 0
    tracking_dict['N_STATES_EXPANDED'] = 0
    tracking_dict['N_STATIC_EVALS'] = 0
    tracking_dict['N_CUTOFFS'] = 0

    global USE_ALPHA_BETA, USE_BASIC_EVAL, USE_ZOBRIST
    USE_ALPHA_BETA = alphaBeta
    USE_BASIC_EVAL = useBasicStaticEval
    USE_ZOBRIST = useZobristHashing

    znum = 0
    if USE_ZOBRIST:
        znum = ZB.zhash(currentState.board) 

    move, tracking_dict['CURRENT_STATE_VAL'] = minimax_search(currentState, ply, znum, -100000, 100000, "BAD")
    # print(move)
    return tracking_dict

def makeMove(currentState, currentRemark, timelimit=10):
    global tlimit
    global start_time
    start_time = time()
    tlimit = timelimit
    # Compute the new state for a move.
    # You should implement an anytime algorithm based on IDDFS.

    # From the spec,
    # It should return a list of the form [[move, newState], newRemark]

    # Copies the current state and gets the znum for hash chaining
    newState = BC_state(currentState.board, currentState.whose_move)
    if USE_ZOBRIST: znum = ZB.zhash(newState.board) 
    else: znum = 0
    
    # Evaluates moves, using AB pruning minimax search, increasing ply until we hit 
    # the timelimit with the best move in a local iterative deepening dfs
    ply = 1
    move = None
    while time() - start_time < (tlimit - .3):
        temp_move, val = minimax_search(currentState, ply, znum, -100000, 100000, move)
        if temp_move is not None:
            move = temp_move
        # print(ply, move)
        ply += 1

    # If we have no move when the clock strikes, pick one at random
    if move is None:
        move = MG.get_random_move(newState)
            
    # Construct a representation of the move that goes from the
    # currentState to the newState.
    applyMove(newState, znum, move)

    # Make up a new remark. Remarks are ignored, otherwise I would make a table
    #  for them based on how much of a lead we have
    newRemark = "Prepare to be smote!"

    return [[move, newState], newRemark]


# performs a minimax search, starting at the current state and going ply
# levels deep (with 0 returning a static eval of the state).
# 
# Return: move, value
#  - move is a tuple of coordinate tuples, in the form ((h1,w1), (h2,w2))
#  - value is the found value of the given state
# 
# Pays attention to AB iff USE_ALPHA_BETA, and uses ZB hashing iff USE_ZOBRIST
# AB cutoffs occur when an opponent wouldn't let us access the current state,
#  based on alpha and beta (as they have a better play), and returns None, None
def minimax_search(state, ply, znum, alpha, beta, order=None):
    if ply == 0:
        tracking_dict['N_STATIC_EVALS'] += 1
        return None, staticEval(state)
    
    # White is 1 and maximizing, so initial value will be -100,000. Black is min and 0, so 100,000.
    value = -200000 * (state.whose_move - .5)

    # get possible moves, either from the zb moves table or generate them if in an unseen state
    # we use state as opposed on just the hash + player move due to collision reasons
    if USE_ZOBRIST and zb_moves.get(znum, None) is not None and zb_moves[znum][0] == state:
        tracking_dict['N_ZOBRIST_LOOKUPS'] += 1
        possible_moves = zb_moves[znum][1]
    else: 
        possible_moves = MG.findMoves(state, IMITATOR_CAPTURES_IMPLEMENTED)
        zb_moves[znum] = (state, possible_moves)
    
    if order == "BAD":
        # dicts have a preservation of order property, so we can reorder our moves into a new one
        a1_h8 = {}
        starts = sorted(possible_moves, key=lambda coord: (coord[1], -coord[0]))
        for start in starts:
            ends = sorted(possible_moves[start], key=lambda coord: (coord[1], -coord[0]))
            a1_h8[start] = ends
        possible_moves = a1_h8
    # best move from the previous iteration at the start to establish good alpha beta values
    elif order is not None:
        ends = possible_moves[order[0]]
        ends.remove(order[1])
        temp = list()
        temp.append(order[1])
        ends = temp + ends
        del possible_moves[order[0]]
        hold = {order[0]: ends}
        for start_coord, possible_move_list in possible_moves.items():
            hold[start_coord] = possible_move_list
        zb_moves[znum] = (state.whose_move, hold)
        possible_moves = hold
        # our order move won't be helpful to lower states, but we need to propagate bad order
        order = None

    # keep our znum so we can find our successor's
    our_znum = znum
    best_move = None
    # the starting coordinate of each piece we control, and the list of places we could move it
    for start_coord, possible_move_list in possible_moves.items():
        for piece_move in possible_move_list:
            if time() - start_time > (tlimit - .3):
                tracking_dict['N_TIMEOUT'] += 1
                return best_move, value
            new_state = BC_state(state.board, state.whose_move)
            # apply move modifies our new state to be our successor
            znum = applyMove(new_state, our_znum, (start_coord, piece_move))
            
            # znum is None in the special case where we take the king, making this the best move
            if znum is None:
                return (start_coord, piece_move), -200000 * (.5 - state.whose_move)
            # minimax of the successor to determine how valuable that board is to us
            #  we ignore the move it wants to make, we don't care because we're not there.
            if USE_ZOBRIST and zb_table.get(znum, None) != None and zb_table[znum][0] == (ply-1):
                tracking_dict['N_ZOBRIST_LOOKUPS'] += 1
                successor_value = zb_table[znum][1]
            else:
                tracking_dict['N_STATES_EXPANDED'] += 1
                _, successor_value = minimax_search(new_state, ply-1, znum, alpha, beta, order)
                zb_table[znum] = (ply-1, successor_value)

            # Successor value is none when it triggers an alpha beta cutoff.
            #  We can ignore this successor, it's bad for us.
            if successor_value is None:
                continue

            # if we're the maximizing player and this is the best board we've seen, keep the value
            if state.whose_move == WHITE and value < successor_value:
                value = successor_value
                best_move = (start_coord, piece_move)
            # if the value is better than the best move we're currently guaranteed, set alpha
            if state.whose_move == WHITE and alpha < value:
                alpha = value
            # same, but for the minimizing player
            if state.whose_move == BLACK and successor_value < value:
                value = successor_value
                best_move = (start_coord, piece_move)
            if state.whose_move == BLACK and value < beta:
                beta = value
            
            # If we have beta <= alpha, we know that we'll never reach this state because our opponent
            #  wouldn't bring us into this state, as we can make a move that is bad for them. We can return
            if USE_ALPHA_BETA and beta <= alpha:
                tracking_dict['N_CUTOFFS'] += 1
                return None, None

    return best_move, value


# Moves the piece from the first position in move to the second, capturing
# pieces as appropriate. Note that only the moving piece has capture priority
# as per the validation tool--moving between two pincers, for example, is
# legal and doesn't remove the moving piece. Assumes the move is legal, but
# checks that it's made by the active player and that it's not overwriting
# a piece illegally
# 
# Swaps the active player
# modifies state, so copy should be made before applying a move
# returns znum, or None if a king is captured by this move
def applyMove(state, znum, move):
    piece = state.board[move[0][0]][move[0][1]]
    assert(piece != 0 and piece%2 == state.whose_move)
    turn = state.whose_move
    state.whose_move = 1 - state.whose_move
    if state.board[move[1][0]][move[1][1]] != 0:
        # Zobrist for King captures (and by imitator)
        # King can capture occupied space, imitator can capture kings by moving into their space
        assert(piece == BLACK_KING+turn or (IMITATOR_CAPTURES_IMPLEMENTED and 
                    piece == BLACK_IMITATOR+turn and state.board[move[1][0]][move[1][1]] == WHITE_KING-turn))
        if USE_ZOBRIST: znum = ZB.zcapture(state.board, znum, (move[1][0], move[1][1]))
        if state.board[move[1][0]][move[1][1]] == WHITE_KING-turn:
            state.board[move[0][0]][move[0][1]] = 0
            state.board[move[1][0]][move[1][1]] = piece
            return None
    if USE_ZOBRIST: znum = ZB.zmove(state.board, znum, move)
    state.board[move[0][0]][move[0][1]] = 0
    state.board[move[1][0]][move[1][1]] = piece

    # turn is the active player, so BLACK_piece + turn yields that piece
    #  for the active player
    if piece == (BLACK_PINCER+turn):
        ordinals = [(1,0), (0, 1), (-1, 0), (0,-1)]
        for dir in ordinals:
            new_h, new_w = move[1][0], move[1][1]
            new_h += 2*dir[0]
            new_w += 2*dir[1]
            # if a sandwich of our pincer, an enemy piece, a friendly piece
            #  was completed on board
            # make sure not to count empty squares
            if 0 <= new_h and new_h < 8 and 0 <= new_w and new_w < 8\
                and state.board[new_h][new_w] != 0 and state.board[new_h-dir[0]][new_w-dir[1]] != 0 \
                and state.board[new_h][new_w] % 2 == turn and state.board[new_h-dir[0]][new_w-dir[1]] % 2 == (1-turn):
                # Zobrist
                if USE_ZOBRIST: znum = ZB.zcapture(state.board, znum, (new_h-dir[0], new_w-dir[1]))
                state.board[new_h-dir[0]][new_w-dir[1]] = 0
                if state.board[new_h-dir[0]][new_w-dir[1]] == WHITE_KING-turn:
                    return None
    elif piece == (BLACK_COORDINATOR+turn):
        # King's coords
        r, c = 0, 0
        for i in range(8):
            for j in range(8):
                # King is guaranteed to exist if game is going
                if state.board[i][j] == (BLACK_KING+turn):
                    r = i
                    c = j
        # Coord's coords
        i, j = move[1][0], move[1][1]
        # If King and Coord share an axis, they can't capture
        if i == r or j == c:
            return znum
        # otherwise, if there's an enemy piece on sX or sY, capture
        if state.board[i][c] % 2 == (1-turn):
            # Zobrist
            if USE_ZOBRIST: znum = ZB.zcapture(state.board, znum, (i, c))
            state.board[i][c] = 0
            if state.board[i][c] == WHITE_KING-turn:
                return None
        if state.board[r][j] % 2 == (1-turn):
            # Zobrist
            if USE_ZOBRIST: znum = ZB.zcapture(state.board, znum, (r, j))
            state.board[r][j] = 0
            if state.board[r][j] == WHITE_KING-turn:
                return None
    elif piece == (BLACK_LEAPER+turn):
        # determine the direction of movement, normalize so we can check the space before we land
        dirh, dirw = move[1][0] - move[0][0], move[1][1] - move[0][1]
        if dirh != 0: dirh //= abs(dirh)
        if dirw != 0: dirw //= abs(dirw)

        # go one space back, if it's an enemy, capture. Always on board because we passed it
        if state.board[move[1][0] - dirh][move[1][1] - dirw] % 2 == (1-turn):
            # Zobrist
            if USE_ZOBRIST: znum = ZB.zcapture(state.board, znum, (move[1][0] - dirh, move[1][1] - dirw))
            state.board[move[1][0] - dirh][move[1][1] - dirw] = 0
            if state.board[move[1][0] - dirh][move[1][1] - dirw] == WHITE_KING-turn:
                return None
    elif IMITATOR_CAPTURES_IMPLEMENTED and piece == (BLACK_IMITATOR+turn):
        znum = imitator_capture(state, znum, move)
    elif piece == (BLACK_WITHDRAWER+turn):
        # determine the direction of movement, normalize so we can check the space before we move
        dirh, dirw = move[1][0] - move[0][0], move[1][1] - move[0][1]
        if dirh != 0: dirh //= abs(dirh)
        if dirw != 0: dirw //= abs(dirw)

        cap_h = move[0][0] - dirh
        cap_w = move[0][1] - dirw

        # one space back from where we started, if it's an enemy, capture.
        if 0 <= cap_h and cap_h < 8 and 0 <= cap_w and cap_w < 8\
            and state.board[cap_h][cap_w] % 2 == (1-turn):
            # Zobrist
            if USE_ZOBRIST: znum = ZB.zcapture(state.board, znum, (cap_h, cap_w))
            state.board[cap_h][cap_w] = 0
            if state.board[cap_h][cap_w] == WHITE_KING-turn:
                return None
        # Freezer doesn't capture, King is handled earlier
    return znum


# checks if an imitator's move hit any captures. Reuses most logic
#  from apply move, replacing enemy checks with checks for the capture style piece
def imitator_capture(state, znum, move):
    # King is handled before this is called, freezers don't capture and are checked on move generation
    # we inverted the turn in apply_move, so we need to have turn be before that inversion
    turn = 1 - state.whose_move
    # determine the direction of movement, normalize so we can check the space before we land and start
    dirh, dirw = move[1][0] - move[0][0], move[1][1] - move[0][1]
    if dirh != 0: dirh //= abs(dirh)
    if dirw != 0: dirw //= abs(dirw)

    # if we moved horizontally, check if we pinced any pincers
    if abs(dirh) != abs(dirw):
        ordinals = [(1,0), (0, 1), (-1, 0), (0,-1)]
        for dir in ordinals:
            new_h, new_w = move[1][0], move[1][1]
            new_h += 2*dir[0]
            new_w += 2*dir[1]
            # if a sandwich of our imitator, an enemy pincer, a friendly piece
            #  was completed on board, capture it
            # make sure not to count empty squares
            if 0 <= new_h and new_h < 8 and 0 <= new_w and new_w < 8\
                and state.board[new_h][new_w] != 0 and state.board[new_h-dir[0]][new_w-dir[1]] != 0 \
                and state.board[new_h][new_w] % 2 == turn and state.board[new_h-dir[0]][new_w-dir[1]] == (WHITE_PINCER-turn):
                # Zobrist
                if USE_ZOBRIST: znum = ZB.zcapture(state.board, znum, (new_h-dir[0], new_w-dir[1]))
                state.board[new_h-dir[0]][new_w-dir[1]] = 0
    
    # Coordinator captures
    # King's coords
    r, c = 0, 0
    for i in range(8):
        for j in range(8):
            # King is guaranteed to exist if game is going
            if state.board[i][j] == (BLACK_KING+turn):
                r = i
                c = j
    # Imitator's coords
    i, j = move[1][0], move[1][1]
    # If King and Coord share an axis, they can't capture
    if i == r or j == c:
        # do nothing, just don't check coordinator captures
        znum = znum
    # otherwise, if there's an enemy Coordinator on sX or sY, capture
    elif state.board[i][c] == (WHITE_COORDINATOR-turn):
        # Zobrist
        if USE_ZOBRIST: znum = ZB.zcapture(state.board, znum, (i, c))
        state.board[i][c] = 0
    elif state.board[r][j] == (WHITE_COORDINATOR-turn):
        # Zobrist
        if USE_ZOBRIST: znum = ZB.zcapture(state.board, znum, (r, j))
        state.board[r][j] = 0
    
    cap_h = move[0][0] - dirh
    cap_w = move[0][1] - dirw

    # one space back from where we started, if it's an enemy withdrawer, capture.
    if 0 <= cap_h and cap_h < 8 and 0 <= cap_w and cap_w < 8\
        and state.board[cap_h][cap_w] == (WHITE_WITHDRAWER-turn):
        # Zobrist
        if USE_ZOBRIST: znum = ZB.zcapture(state.board, znum, (cap_h, cap_w))
        state.board[cap_h][cap_w] = 0
    # go one space back from end, if it's an enemy leaper, capture. Always on board because we passed it
    if state.board[move[1][0] - dirh][move[1][1] - dirw] == (WHITE_LEAPER-turn):
        # Zobrist
        if USE_ZOBRIST: znum = ZB.zcapture(state.board, znum, (move[1][0] - dirh, move[1][1] - dirw))
        state.board[move[1][0] - dirh][move[1][1] - dirw] = 0
    return znum


def nickname():
    return "Caissa"

def introduce():
    return '''I'm Caissa, and I'll soon be the god of chess! I've been 
    training under Brice (bricecm) and Rene (renec3)'''

def prepare(player2Nickname):
    ''' Here the game master will give your agent the nickname of
    the opponent agent, in case your agent can use it in some of
    the dialog responses.  Other than that, this function can be
    used for initializing data structures, if needed.'''
    global USE_ALPHA_BETA, USE_ZOBRIST, USE_BASIC_EVAL, IMITATOR_CAPTURES_IMPLEMENTED, tracking_dict
    USE_ALPHA_BETA = True
    USE_ZOBRIST = True
    USE_BASIC_EVAL = False
    IMITATOR_CAPTURES_IMPLEMENTED = True

    ZB.zb_init()
    
    tracking_dict['CURRENT_STATE_VAL'] = 0
    tracking_dict['N_STATES_EXPANDED'] = 0
    tracking_dict['N_STATIC_EVALS'] = 0
    tracking_dict['N_CUTOFFS'] = 0

    tracking_dict['N_ZOBRIST_LOOKUPS'] = 0
    tracking_dict['N_TIMEOUT'] = 0
    pass


def basicStaticEval(state):
    '''Use the simple method for state evaluation described in the spec.
    This is typically used in parameterized_minimax calls to verify
    that minimax and alpha-beta pruning work correctly.'''
    eval = 0
    for i in range(8):
        for j in range(8):
            if state.board[i][j] == 0:
                continue
            elif state.board[i][j] == WHITE_KING:
                eval += 100
            elif state.board[i][j] == BLACK_KING:
                eval -= 100
            elif state.board[i][j] == WHITE_PINCER:
                eval += 1
            elif state.board[i][j] == BLACK_PINCER:
                eval -= 1
            elif state.board[i][j] % 2 == WHITE:
                eval += 2
            elif state.board[i][j] % 2 == BLACK:
                eval -= 2
    return eval


def staticEval(state):
    '''Compute a more thorough static evaluation of the given state.
    This is intended for normal competitive play.  How you design this
    function could have a significant impact on your player's ability
    to win games.'''
    if USE_BASIC_EVAL:
        return basicStaticEval(state)
    # {'p':2, 'P':3, 'c':4, 'C':5, 'l':6, 'L':7, 'i':8, 'I':9,
    #     'w':10, 'W':11, 'k':12, 'K':13, 'f':14, 'F':15, '-':0}
    #
    # values: pincers worth 1, coords and withdrawers worth 3, leapers worth 4
    #   imitators worth 5, and king worth game. Freezers are worth 2 by themselves
    #   and take half value of each piece they're freezing, except kings (still worth 10)
    values = [0, 0, -2, 2, -7, 7, -8, 8, -10, 10, -6, 6, -300, 300, -3, 3]
    if IMITATOR_CAPTURES_IMPLEMENTED == False:
        values = [0, 0, -2, 2, -7, 7, -8, 8, -1, 1, -6, 6, -300, 300, -3, 3]
    polarity = [-1, 1]
    eval = 0

    white_piece_moves, black_piece_moves = static_eval_2(state)
    # (3, 4): (1, 4), (2, 4)
    white_mobility_bonus = 0
    for piece in white_piece_moves.keys():
        moves = white_piece_moves[piece]
        white_mobility_bonus += len(moves)

    black_mobility_bonus = 0
    for piece in black_piece_moves.keys():
        moves = black_piece_moves[piece]
        black_mobility_bonus += len(moves)

    eval += .1*white_mobility_bonus
    eval -= .1*black_mobility_bonus

    for i in range(8):
        for j in range(8):

            eval += values[state.board[i][j]]
            if state.board[i][j] == BLACK_FREEZER:
                ordinals = [(1,0), (1, 1), (0, 1), (-1, 1),
                    (-1, 0), (-1, -1), (0,-1), (1, -1)]
                for dir in ordinals:
                    new_h, new_w = i, j
                    new_h += dir[0]
                    new_w += dir[1]
                    if 0 <= new_h and new_h < 8 and 0 <= new_w and new_w < 8\
                            and state.board[new_h][new_w] % 2 == WHITE:
                        if state.board[new_h][new_w] == WHITE_KING:
                            eval -= 10
                            continue
                        eval -= values[state.board[new_h][new_w]]/2
            elif state.board[i][j] == WHITE_FREEZER:
                ordinals = [(1,0), (1, 1), (0, 1), (-1, 1),
                    (-1, 0), (-1, -1), (0,-1), (1, -1)]
                for dir in ordinals:
                    new_h, new_w = i, j
                    new_h += dir[0]
                    new_w += dir[1]
                    if 0 <= new_h and new_h < 8 and 0 <= new_w and new_w < 8\
                            and state.board[new_h][new_w] != 0 and state.board[new_h][new_w] % 2 == BLACK:
                        if state.board[new_h][new_w] == BLACK_KING:
                            eval += 10
                            continue
                        eval -= values[state.board[new_h][new_w]]/2
    return eval


def static_eval_2(state):
    if state.whose_move == WHITE:
        white_piece_moves = MG.findMoves(state, IMITATOR_CAPTURES_IMPLEMENTED)
        state.whose_move = 1 - state.whose_move
        black_piece_moves = MG.findMoves(state, IMITATOR_CAPTURES_IMPLEMENTED)
        state.whose_move = 1 - state.whose_move
    else:
        black_piece_moves = MG.findMoves(state, IMITATOR_CAPTURES_IMPLEMENTED)
        state.whose_move = 1 - state.whose_move
        white_piece_moves = MG.findMoves(state, IMITATOR_CAPTURES_IMPLEMENTED)
        state.whose_move = 1 - state.whose_move
    return white_piece_moves, black_piece_moves


def enable_imitator_captures(status = False):
    global IMITATOR_CAPTURES_IMPLEMENTED
    IMITATOR_CAPTURES_IMPLEMENTED = status
    return

if __name__ == "__main__":
    prepare("Nick")
    # init_state = BC_state(INITIAL, WHITE)
    # print(staticEval(init_state))

#     b_state = parse('''
# - P - p - - - -
# - I - - p - k p
# - - p - - - - -
# - p - - - - - -
# w - - - - - P p
# - - - - - - - -
# P - - K - l - -
# - - - W - - - -
# ''')
#
#
#     bcc = BC_state(b_state, WHITE)
#     # bcc.whose_move = BLACK
#     print(bcc)
#     print("eval is " + str(staticEval(bcc)))
#     dict1 = MG.findMoves(bcc)
#     for k in dict1.keys():
#         print("key: " + str(k) + " val: " + str(dict1[k]))
#
#     m = makeMove(bcc, "hi", 3)
#     print("move is")
#     print(m)

    b_state = parse('''
- - - - - - - -
- - - - - - - -
- - - - - - - -
- - - - - - - -
- - - - - - - -
- - - - - - - -
P P P P P P P P
F L I W K I L C
''')


    bcc = BC_state(b_state, WHITE)
    # print(MG.findMoves(bcc, True))
    # print(bcc)
    print(staticEval(bcc))

    # a_state = BC_state(a_state, WHITE)
    # print(staticEval(a_state))
    # print("state before")
    # print(a_state)
    # applyMove(a_state, 0, ((7,5), (7,7)))
    # print("state after")
    # print(a_state)
    #
    # makeMove(a_state, "", 10)
    # print("state after after")
    # print(a_state)
    # print(parameterized_minimax(a_state, ply=1, useBasicStaticEval=False)['CURRENT_STATE_VAL'])
    # print(parameterized_minimax(a_state, ply=2, useBasicStaticEval=False)['CURRENT_STATE_VAL'])
    # print(parameterized_minimax(a_state, ply=3, useBasicStaticEval=False)['CURRENT_STATE_VAL'])
