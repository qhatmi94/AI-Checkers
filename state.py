'''
state.py

A state class for a checkers game.
'''

from collections import namedtuple
from enum import IntEnum
from random import randint

Location = namedtuple('Location', ['x', 'y'])


class Piece(IntEnum):
    """Represents a checkers piece."""
    EMPTY = 0
    BLACK_PAWN = 1
    BLACK_KING = 3
    RED_PAWN = 2
    RED_KING = 4

    def __repr__(self):
        if self == self.EMPTY:
            return '_'
        if self == self.BLACK_PAWN:
            return 'b'
        if self == self.BLACK_KING:
            return 'B'
        if self == self.RED_PAWN:
            return 'r'
        if self == self.RED_KING:
            return 'R'

    def player(self):
        if self == self.EMPTY:
            return None
        return Player(self % 2 + 1)

    def is_king(self):
        return self == self.RED_KING or self == self.BLACK_KING


class Player(IntEnum):
    """Designates the color of the player."""
    BLACK = 2
    RED = 1


def _create_initial_board(size):
    """Generates the starting position of the game."""
    b = [[Piece.EMPTY for _ in range(size)] for _ in range(size)]
    for x in range(size):
        for y in range(size):
            if y < size / 2 - 1:
                if x % 2 != y % 2:
                    b[y][x] = Piece.BLACK_PAWN
            if y >= size / 2 + 1:
                if x % 2 != y % 2:
                    b[y][x] = Piece.RED_PAWN
    return b

#INITIAL_BOARD = _create_initial_board()
'''b = [[Piece.EMPTY for _ in range(8)] for _ in range(8)]
b[1][6] = Piece.BLACK_PAWN
b[2][7] = Piece.RED_PAWN
b[6][7] = Piece.BLACK_PAWN
INITIAL_BOARD = b
'''

class State:
    """The state space for the game."""
    def __init__(self, board=None, whose_move=Player.BLACK, board_size=8):
        self.board = [r[:] for r in board] if board is not None else _create_initial_board(board_size)
        self.board_size = board_size
        self.whose_move = whose_move

    def __repr__(self):
        res = '_________________________________\n'
        for y in range(self.board_size):
            res += '| '
            for x in range(self.board_size):
                piece = self.board[y][x]
                res += repr(piece) + ' | '
            res += '\n_________________________________\n'
        return res

    def get_piece(self, x, y):
        """Returns the piece at the given coordintes on the board."""
        return self.board[y][x]

    def is_game_over(self):
        """Returns true if one player has run out of pieces."""
        n_reds = 0
        n_blacks = 0
        board = self.board
        for y in range(self.board_size):
            for x in range(self.board_size):
                piece = board[y][x]
                if piece.player() == Player.BLACK:
                    n_blacks += 1
                elif piece.player() == Player.RED:
                    n_reds += 1
        if n_reds == 0:
            # print("Black wins.")
            return Player.BLACK
        if n_blacks == 0:
            # print("Red wins.")
            return Player.RED

        if len(self.generate_successors()) == 0:
            return Player(self.whose_move % 2 + 1)
        return 0

    def generate_successors(self, help=False):
        """Returns all possible successor states to the passed state."""
        board = self.board
        whose_move = self.whose_move
        successors = []
        has_kills = False
        for y in range(self.board_size):
            for x in range(self.board_size):
                piece = board[y][x]
                if piece.player() == whose_move:
                    moves = self.generate_moves(
                        Location(x, y), needs_kill=has_kills)
                    if not has_kills:
                        for s, m in moves:
                            if len(m.kills) > 0:
                                has_kills = True
                                break
                    successors += moves
        if has_kills:
            new_moves = []
            for (s, m) in successors:
                if len(m.kills) > 0:
                    new_moves.append((s, m))
            return new_moves
        return successors

    def move(self, move_info):
        """Moves one piece."""
        loc = move_info.steps[0]
        new_loc = move_info.steps[-1]
        state = State(board=self.board, whose_move=Player(
            self.whose_move % 2 + 1), board_size=self.board_size)
        state.board[new_loc.y][new_loc.x] = state.board[loc.y][loc.x]
        state.board[loc.y][loc.x] = Piece.EMPTY
        piece = state.board[new_loc.y][new_loc.x]
        if not piece.is_king():
            if new_loc.y == self.board_size - 1 or new_loc.y == 0:
                state.board[new_loc.y][new_loc.x] = Piece(piece + 2)

        for (x, y) in move_info.kills:
            state.board[y][x] = Piece.EMPTY
        return state
    # generate moves for specific location and piece, recrusive for kills
    def generate_moves(self, loc, needs_kill=False, current_move_info=None):
        """Returns all possible moves from the current state."""
        board = self.board
        whose_move = self.whose_move
        piece = board[loc.y][loc.x]
        player = piece.player()
        moves = []

        def gen_diagonals(loc):
            d = []
            if player == Player.BLACK or piece.is_king():
                d += [
                    Location(loc.x + 1, loc.y + 1),
                    Location(loc.x - 1, loc.y + 1)
                ]
            if player == Player.RED or piece.is_king():
                d += [
                    Location(loc.x + 1, loc.y - 1),
                    Location(loc.x - 1, loc.y - 1)
                ]
            return d

        def check_bounds(loc):
            x, y = loc
            if x < 0 or x > self.board_size - 1:
                return False
            if y < 0 or y > self.board_size - 1:
                return False
            return True

        for x, y in gen_diagonals(loc):
            if check_bounds((x, y)):
                opp = board[y][x].player()
            else:
                continue
            if opp != whose_move:
                if opp is None:
                    if not needs_kill:
                        move_info = MoveInfo([loc, Location(x, y)], [])
                        new_state = self.move(move_info)
                        moves.append((new_state, move_info))
                else:
                    xx = x + (x - loc.x)
                    yy = y + (y - loc.y)
                    if check_bounds((xx, yy)):
                        p = board[yy][xx]
                        if p == Piece.EMPTY:
                            move_info = current_move_info or MoveInfo([loc], [])
                            move_info.kills.append(Location(x, y))
                            move_info.steps.append(Location(xx, yy))
                            s = self.move(
                                MoveInfo([loc, Location(xx, yy)], [Location(x, y)]))

                            s.whose_move = whose_move
                            s.generate_moves(
                                Location(xx, yy), True, move_info)

                            if current_move_info is None:
                                new_state = self.move(move_info)
                                moves.append((new_state, move_info))
                            else:
                                # break after first successive jump is found,
                                # can only go one way
                                break
                    else:
                        continue
        return moves


    def generate_hash(self):
        """Generates a zobrist hash string of the state."""
        hash = 0
        board = self.board
        whose_move = self.whose_move
        flattened = [str(int(board[y][x])) for y in range(self.board_size)
                     for x in range(self.board_size)] + [str(int(whose_move))]
        return ''.join(flattened)


    def get_winner(self):
        """Returns the winner."""
        winner = self.is_game_over()
        if winner == Player.BLACK:
            return "Black"
        else:
            return "Red"


class MoveInfo:
    """info representing a move."""
    def __init__(self, steps=[], kills=[]):
        self.steps = steps
        self.kills = kills

    def __repr__(self):
        return 'steps: %r\nkills: %r' % (self.steps, self.kills)
