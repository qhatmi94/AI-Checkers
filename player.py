'''
player.py

A player for a checkers game. Uses a precomputed table of values assigned to
specific board states to determine the best move.
'''

from q_learning import *
from state import *
from random import randint


def move(maximize, state, Q_VALUES):
    """Make a move from the q learning values."""
    successors = state.generate_successors()
    best_value = float('-inf') if maximize else float('inf')
    best_move = None
    for (new_state, move_info) in successors:
        hash = new_state.generate_hash()
        try:
            q_value, _ = Q_VALUES[hash]
            if maximize:
                if q_value > best_value:
                    best_value = q_value
                    best_move = (new_state, move_info)
            else:
                if q_value < best_value:
                    best_value = q_value
                    best_move = (new_state, move_info)
        except KeyError:
            pass

    if best_move is None:
        move = successors[randint(0, len(successors) - 1)]
        return move, Q_VALUES.get(move[0].generate_hash()) or 0
    return best_move, best_value
