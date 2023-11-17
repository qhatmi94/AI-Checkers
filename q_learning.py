'''
q_learning.py

A q_learning function for a checkers game.
'''

import pickle
from io import FileIO
from os.path import isfile, dirname
from os import makedirs
from random import randint, uniform

from state import Player, State

Q_VALUES = {}


def save_q(Q, file_location):
    """Saves the current q learning values to the specified location."""
    try:
        makedirs(dirname(file_location))
    except OSError as exc:
        pass
    file = FileIO(file_location, 'w')
    pickle.dump(Q, file)
    file.close()


def load_q(file_location):
    """Loads the q learning values from the specified file."""
    file = FileIO(file_location, 'r')
    Q = pickle.load(file)
    file.close()
    return Q


def q_learning(settings, initial_state=State()):
    """Run q learning on the specified state."""
    # variable settings
    LEARNING_RATE = settings['LEARNING_RATE']
    EXPLORE_PROB = settings['EXPLORE_PROB']
    DISCOUNT = settings['DISCOUNT']
    Q_GAMES = settings['Q_GAMES']

    # check if q-values are cached
    cache_path = 'cache/%.1f-%.1f-%.1f-%d-%d.save' % (
        LEARNING_RATE, EXPLORE_PROB, DISCOUNT, Q_GAMES, initial_state.board_size)
    if isfile(cache_path):
        return load_q(cache_path)
    Q = {}
    Q[initial_state.generate_hash()] = (0, 1)
    n_games = 0
    state = initial_state
    while n_games < Q_GAMES:
        # Choose least seen state if explore, choose best q-value otherwise
        if uniform(0.0, 1.0) < EXPLORE_PROB:
            (new_state, move_info), q_value = _explore_action(Q, state)
        else:
            (new_state, move_info), q_value = _best_action(Q, state)
        reward = _reward(new_state, move_info)

        game_over = new_state.is_game_over()
        hash = state.generate_hash()
        q, n = Q[hash]
        if game_over == 0:
            state = new_state
            _, q_prime = _best_action(Q, new_state)
            Q[hash] = (q + LEARNING_RATE *
                       ((reward + DISCOUNT * q_prime) - q_value), n + 1)
        else:
            # check if game is over start a new one
            state = initial_state
            Q[hash] = (q + LEARNING_RATE * (reward - q_value), n + 1)
            n_games += 1

    save_q(Q, cache_path)
    return Q


def _explore_action(Q, state):
    """Explores going from the passed state."""
    # explore, use the least seen state
    explore_actions = []
    min_visited = float('inf')
    for (new_state, move_info) in state.generate_successors():
        hash = new_state.generate_hash()
        try:
            _, n = Q[hash]
        except KeyError:
            n = 1
            Q[hash] = (uniform(-.1, .1), 1)
        if n < min_visited:
            explore_actions = [(new_state, move_info)]
            min_visited = n
        elif n == min_visited:
            explore_actions.append((new_state, move_info))
    if len(explore_actions) == 1:
        return explore_actions[0], Q[explore_actions[0][0].generate_hash()][0]
    s, move_info = explore_actions[randint(0, len(explore_actions) - 1)]
    return (s, move_info), Q[s.generate_hash()][0]


def _best_action(Q, state):
    """Follows the best known course of action from the passed state."""
    successors = state.generate_successors()
    player = state.whose_move
    best_q_value = float('inf') if player == player.BLACK else float('-inf')
    best_actions = []
    for (new_state, move_info) in successors:
        hash = new_state.generate_hash()
        try:
            q_value, _ = Q[hash]
        except KeyError:
            q_value = uniform(-0.1, .1)
            Q[hash] = (q_value, 1)

        if player == player.BLACK:
            if q_value < best_q_value:
                best_q_value = q_value
                best_actions = [(new_state, move_info)]
            elif q_value == best_q_value:
                best_actions.append((new_state, move_info))
        else:
            if q_value > best_q_value:
                best_q_value = q_value
                best_actions = [(new_state, move_info)]
            elif q_value == best_q_value:
                best_actions.append((new_state, move_info))
    if len(best_actions) == 1:
        return best_actions[0], best_q_value
    try:
        return best_actions[randint(0, len(best_actions) - 1)], best_q_value
    except ValueError as e:
        print(state)
        raise(e)


def _reward(state, move_info):
    """Returns a reward afer moving to a state."""
    # reward caclulated by kills and game over, and if kinged
    game_over = state.is_game_over()
    if game_over == Player.RED:
        return 100
    if game_over == Player.BLACK:
        return -100
    reward = len(move_info.kills)

    board = state.board
    player = state.whose_move
    kings = 0
    for y in range(state.board_size):
        for x in range(state.board_size):
            piece = board[y][x]
            if piece.player() == player and piece.is_king():
                kings += 1

    reward += kings

    if state.whose_move == Player.RED:
        return reward
    else:
        return -reward
