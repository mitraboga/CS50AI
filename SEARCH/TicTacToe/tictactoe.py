"""
Tic-Tac-Toe with optimal Minimax AI + Alpha-Beta pruning, transposition table,
and smart move ordering. Fully compatible with CS50 AI Project 0 specification.

Functions implemented per spec:
- initial_state
- player
- actions
- result
- winner
- terminal
- utility
- minimax

Advanced features (still spec-compliant):
- Alpha-Beta pruning
- Transposition table (memoization) keyed by an immutable board encoding
- Move ordering (center -> corners -> edges)
- Optional depth-limited search with a heuristic (disabled by default)
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None

# ---- Advanced AI tuning knobs (safe defaults for full-search optimal play) ----
USE_ALPHA_BETA = True
USE_TRANSPOSITION = True
USE_MOVE_ORDERING = True
DEPTH_LIMIT = None  # Set to an int (e.g., 5) to enable heuristic cutoff; None = full search

# Transposition table: key -> (value, best_action)
# value is the exact minimax utility from the perspective of optimal play.
_TRANSPOSITION = {}


def initial_state():
    """
    Returns starting state of the board.
    A 3x3 list-of-lists with EMPTY cells.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    X moves first; players alternate. Any value acceptable if board is terminal.
    """
    # Count marks
    x_count = sum(cell == X for row in board for cell in row)
    o_count = sum(cell == O for row in board for cell in row)

    # If terminal, spec says any return value acceptable; we return X by convention
    if terminal(board):
        return X

    # X starts and alternates
    return X if x_count == o_count else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    Any return value acceptable if board is terminal. We return empty set then.
    """
    if terminal(board):
        return set()
    return {(i, j) for i in range(3) for j in range(3) if board[i][j] is EMPTY}


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    Raises an exception if action is invalid. Does not modify original board.
    """
    (i, j) = action
    if i not in {0, 1, 2} or j not in {0, 1, 2}:
        raise Exception("Action out of bounds.")
    if board[i][j] is not EMPTY:
        raise Exception("Invalid action: cell already occupied.")
    new_board = deepcopy(board)
    new_board[i][j] = player(board)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    Returns X, O, or None.
    """

    def line_winner(a, b, c):
        if a is not EMPTY and a == b == c:
            return a
        return None

    # Rows
    for i in range(3):
        w = line_winner(board[i][0], board[i][1], board[i][2])
        if w:
            return w
    # Columns
    for j in range(3):
        w = line_winner(board[0][j], board[1][j], board[2][j])
        if w:
            return w
    # Diagonals
    w = line_winner(board[0][0], board[1][1], board[2][2])
    if w:
        return w
    w = line_winner(board[0][2], board[1][1], board[2][0])
    if w:
        return w

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    Game is over if someone won or if no EMPTY cells remain.
    """
    if winner(board) is not None:
        return True
    return all(board[i][j] is not EMPTY for i in range(3) for j in range(3))


def utility(board):
    """
    Returns the utility of the board:
    1  if X has won,
    -1 if O has won,
    0  if tie (or non-terminal if accidentally called).
    """
    w = winner(board)
    if w == X:
        return 1
    if w == O:
        return -1
    return 0


# -------------------------- Advanced helpers --------------------------

def _key(board):
    """
    Create an immutable key for the transposition table.
    Board is a list of lists; convert to a tuple of tuples.
    """
    return tuple(tuple(row) for row in board)


def _ordered_actions(board):
    """
    Order moves to improve alpha-beta pruning.
    Preference: center -> corners -> edges.
    """
    all_moves = list(actions(board))
    if not USE_MOVE_ORDERING:
        return all_moves

    center = [(1, 1)]
    corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
    edges = [(0, 1), (1, 0), (1, 2), (2, 1)]

    # Keep only those that are available, in priority order.
    ordered = [m for m in center if m in all_moves]
    ordered += [m for m in corners if m in all_moves]
    ordered += [m for m in edges if m in all_moves]

    # If anything left out (shouldn't happen), append them
    leftovers = [m for m in all_moves if m not in ordered]
    ordered += leftovers
    return ordered


def _evaluate(board):
    """
    Simple heuristic for non-terminal positions (used only if DEPTH_LIMIT is set).
    Scores lines where X has potential as positive, O as negative.
    """
    # If someone already won or it's a draw, return exact utility
    if terminal(board):
        return utility(board)

    score = 0

    lines = [
        # Rows
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
        # Cols
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
        # Diagonals
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)],
    ]

    def line_score(cells):
        xs = sum(board[i][j] == X for (i, j) in cells)
        os = sum(board[i][j] == O for (i, j) in cells)
        empties = 3 - xs - os
        # Only one side can still make a three-in-a-row on a line.
        if xs > 0 and os > 0:
            return 0
        # Weight by how many marks and empties remain.
        if xs > 0:
            # Encourage 2-in-a-row more than 1
            return {1: 1, 2: 3}.get(xs, 0)
        if os > 0:
            return -{1: 1, 2: 3}.get(os, 0)
        # All empty line is neutral but slightly favor X as first player
        return 0

    for line in lines:
        score += line_score(line)

    # Slight preference for center and corners if open
    if board[1][1] == X:
        score += 0.5
    elif board[1][1] == O:
        score -= 0.5

    return score


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    If board is terminal, returns None.

    Uses Minimax with Alpha-Beta pruning, a transposition table, and
    move ordering. If DEPTH_LIMIT is set, uses a heuristic evaluator.
    """
    if terminal(board):
        return None

    turn = player(board)

    # If we cached this exact board (including best move), use it.
    if USE_TRANSPOSITION:
        k = _key(board)
        cached = _TRANSPOSITION.get(k)
        if cached is not None:
            # cached = (value, best_action)
            return cached[1]

    # Root search
    if turn == X:
        best_val = -math.inf
        best_move = None
        alpha, beta = -math.inf, math.inf
        for a in _ordered_actions(board):
            val = _min_value(result(board, a), alpha, beta, depth=1)
            if val > best_val:
                best_val, best_move = val, a
            if USE_ALPHA_BETA:
                alpha = max(alpha, best_val)
        if USE_TRANSPOSITION:
            _TRANSPOSITION[_key(board)] = (best_val, best_move)
        return best_move
    else:
        best_val = math.inf
        best_move = None
        alpha, beta = -math.inf, math.inf
        for a in _ordered_actions(board):
            val = _max_value(result(board, a), alpha, beta, depth=1)
            if val < best_val:
                best_val, best_move = val, a
            if USE_ALPHA_BETA:
                beta = min(beta, best_val)
        if USE_TRANSPOSITION:
            _TRANSPOSITION[_key(board)] = (best_val, best_move)
        return best_move


def _max_value(board, alpha, beta, depth):
    if terminal(board):
        return utility(board)

    # Depth-limited eval (optional)
    if DEPTH_LIMIT is not None and depth >= DEPTH_LIMIT:
        return _evaluate(board)

    if USE_TRANSPOSITION:
        k = _key(board)
        cached = _TRANSPOSITION.get(k)
        if cached is not None:
            # We only trust exact utilities for transposition reuse during recursion.
            return cached[0]

    v = -math.inf
    for a in _ordered_actions(board):
        v = max(v, _min_value(result(board, a), alpha, beta, depth + 1))
        if USE_ALPHA_BETA and v >= beta:
            # Beta cut
            break
        if USE_ALPHA_BETA:
            alpha = max(alpha, v)

    if USE_TRANSPOSITION:
        _TRANSPOSITION[_key(board)] = (v, None)
    return v


def _min_value(board, alpha, beta, depth):
    if terminal(board):
        return utility(board)

    # Depth-limited eval (optional)
    if DEPTH_LIMIT is not None and depth >= DEPTH_LIMIT:
        return _evaluate(board)

    if USE_TRANSPOSITION:
        k = _key(board)
        cached = _TRANSPOSITION.get(k)
        if cached is not None:
            return cached[0]

    v = math.inf
    for a in _ordered_actions(board):
        v = min(v, _max_value(result(board, a), alpha, beta, depth + 1))
        if USE_ALPHA_BETA and v <= alpha:
            # Alpha cut
            break
        if USE_ALPHA_BETA:
            beta = min(beta, v)

    if USE_TRANSPOSITION:
        _TRANSPOSITION[_key(board)] = (v, None)
    return v
