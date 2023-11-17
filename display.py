'''
display.py

A graphical display for a checkers game using tkinter.
Little pieces are pawns, big pieces are kings.
'''

from tkinter import *
from state import *

window_size = 500

pieces = []


def draw_board(canvas, board_size):
    """Draws the checkerboard."""
    cell_width = window_size / board_size
    cell_height = window_size / board_size
    for col in range(board_size):
        for row in range(board_size):
            if (row + col) % 2 == 0:
                canvas.create_rectangle(col * cell_width, row * cell_height,
                                        (col + 1) * cell_width, (row + 1) *
                                        cell_height, fill='gray')


def erase_pieces(canvas, pieces):
    """Deletes all game pieces from the game gui."""
    for piece in pieces:
        canvas.delete(piece)
        pieces.remove(piece)


def draw_pieces(canvas, board, pieces):
    """Draws all pieces on the gui from a provided board."""
    board_size = board.board_size
    king_size = 0.1 * window_size / board_size
    pawn_size = 0.25 * window_size / board_size

    for x in range(board_size):
        for y in range(board_size):
            start_x = (x) * window_size / board_size
            start_y = ((y) * window_size / board_size)
            end_x = start_x + window_size / board_size
            end_y = start_y + window_size / board_size

            a = None
            if board.get_piece(x, y) == Piece.RED_KING:
                a = canvas.create_oval(start_x + king_size, start_y + king_size,
                                       end_x - king_size, end_y - king_size,
                                       fill='red')
            elif board.get_piece(x, y) == Piece.RED_PAWN:
                a = canvas.create_oval(start_x + pawn_size, start_y + pawn_size,
                                       end_x - pawn_size, end_y - pawn_size,
                                       fill='red')
            elif board.get_piece(x, y) == Piece.BLACK_KING:
                a = canvas.create_oval(start_x + king_size, start_y + king_size,
                                       end_x - king_size, end_y - king_size,
                                       fill='black')
            elif board.get_piece(x, y) == Piece.BLACK_PAWN:
                a = canvas.create_oval(start_x + pawn_size, start_y + pawn_size,
                                       end_x - pawn_size, end_y - pawn_size,
                                       fill='black')
            pieces.append(a)


def display(canvas, board, q_val):
    """Displays the entire state of a game."""
    canvas.delete('all')
    draw_board(canvas, board.board_size)
    erase_pieces(canvas, pieces)
    draw_pieces(canvas, board, pieces)
    canvas.create_text(window_size + 100, 50,
                       text="Q Value of current board: " + str(q_val))
