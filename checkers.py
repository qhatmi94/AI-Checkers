'''
checkers.py

A manager for a checkers game.
'''

from copy import copy
from time import *
from tkinter import *

import player as player1
import player as player2

from display import *
from q_learning import *
from state import *

player1_turn = True

learning_games = 1000

# tkinter settings
ENABLE_GUI = True
window_size = 500
pieces = []
sleep_time = .1

# default q learning settings
DEFAULT_SETTINGS = {
    'Q_GAMES': 10,
    'LEARNING_RATE': .8,
    'DISCOUNT': .5,
    'EXPLORE_PROB': .4
}
PLAYER_1_SETTINGS = copy(DEFAULT_SETTINGS)
PLAYER_2_SETTINGS = copy(DEFAULT_SETTINGS)

# size of the game board
BOARD_SIZE = 8


class Game():
    """Creates an instance of a checkers game."""
    def __init__(self):
        self.state = State(board_size=BOARD_SIZE)
        self.start_time = perf_counter()

    # run the game 
    def play_game(self, Q_VALUES_1, Q_VALUES_2):
        tk = Tk()
        canvas = Canvas(tk, width=window_size + 200, height=window_size)
        canvas.grid(row=0, column=0)

        player1_turn = True
        q_val = 0

        exists_winner = True

        def update():
            display(canvas, self.state, q_val)
            tk.update()
            sleep(sleep_time)

        print("---\nGame Start")

        while not self.state.is_game_over():
            previous_state = self.state
            if player1_turn:
                (self.state, self.move_info), q_val = player1.move(
                    True, self.state, Q_VALUES_1)
                player1_turn = False
            else:
                (self.state, self.move_info), q_val = player2.move(
                    False, self.state, Q_VALUES_2)
                player1_turn = True
            if ENABLE_GUI:
                update()
            if (perf_counter() - self.start_time) > (sleep_time * 160):
                exists_winner = False
                break
        display(canvas, self.state, q_val)
        winner = "no winner"
        if exists_winner:
            winner = self.state.get_winner()
        canvas.create_text(window_size + 100, 20,
                           text="Winner: " + winner)
        print("Winner: " + winner)


def main():
    """Runs the program."""
    options = Tk()
    options.update_idletasks()
    Q_VALUES_1 = {}
    Q_VALUES_2 = {}

    def update_settings():
        """Changes the settings for the game."""
        nonlocal Q_VALUES_1
        nonlocal Q_VALUES_2
        global BOARD_SIZE
        BOARD_SIZE = int(b_size.get())
        PLAYER_1_SETTINGS = {
            'Q_GAMES': int(q_games_1.get()),
            'LEARNING_RATE': float(lr_1.get()),
            'DISCOUNT': .5,
            'EXPLORE_PROB': float(ep_1.get())
        }
        PLAYER_2_SETTINGS = {
            'Q_GAMES': int(q_games_2.get()),
            'LEARNING_RATE': float(lr_2.get()),
            'DISCOUNT': .5,
            'EXPLORE_PROB': float(ep_2.get())
        }
        Q_VALUES_1 = q_learning(PLAYER_1_SETTINGS, initial_state=State(board_size=BOARD_SIZE))
        Q_VALUES_2 = q_learning(PLAYER_2_SETTINGS, initial_state=State(board_size=BOARD_SIZE))

    def play():
        """Plays one game between the two players."""
        game = Game()
        game.play_game(Q_VALUES_1, Q_VALUES_2)

    # set up config gui
    Label(options, text='Black Q Games:').grid(row=0, column=0)
    q_games_1 = Entry(options)
    q_games_1.config(width=3)
    q_games_1.insert(0, PLAYER_1_SETTINGS['Q_GAMES'])
    q_games_1.grid(row=0, column=1)
    Label(options, text='Red Q Games').grid(row=0, column=2)
    q_games_2 = Entry(options)
    q_games_2.insert(0, PLAYER_2_SETTINGS['Q_GAMES'])
    q_games_2.config(width=3)
    q_games_2.grid(row=0, column=3)

    Label(options, text='Black Learning Rate:').grid(row=1, column=0)
    lr_1 = Scale(options, from_=0, to=1, resolution=.1)
    lr_1.config(orient=HORIZONTAL)
    lr_1.grid(row=1, column=1)
    lr_1.set(PLAYER_1_SETTINGS['LEARNING_RATE'])
    Label(options, text='Red Learning Rate:').grid(row=1, column=2)
    lr_2 = Scale(options, from_=0, to=1, resolution=.1)
    lr_2.config(orient=HORIZONTAL)
    lr_2.grid(row=1, column=3)
    lr_2.set(PLAYER_2_SETTINGS['LEARNING_RATE'])

    Label(options, text='Black Explore Prob:').grid(row=2, column=0)
    ep_1 = Scale(options, from_=0, to=1, resolution=.1)
    ep_1.config(orient=HORIZONTAL)
    ep_1.grid(row=2, column=1)
    ep_1.set(PLAYER_1_SETTINGS['EXPLORE_PROB'])
    Label(options, text='Red Explore Prob:').grid(row=2, column=2)
    ep_2 = Scale(options, from_=0, to=1, resolution=.1)
    ep_2.config(orient=HORIZONTAL)
    ep_2.grid(row=2, column=3)
    ep_2.set(PLAYER_2_SETTINGS['EXPLORE_PROB'])

    Label(options, text='Board Size:').grid(row=3, column=0)
    b_size = Entry(options)
    b_size.config(width=3)
    b_size.insert(0, BOARD_SIZE)
    b_size.grid(row=3, column=1)

    q_learn = Button(options, text="Q Learn", command=update_settings)
    q_learn.grid(row=4, column=0)
    play_game = Button(options, text="Play Game", command=play)
    play_game.grid(row=4, column=1)
    update_settings()
    options.mainloop()
    

main()
