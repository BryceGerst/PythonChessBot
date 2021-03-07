
from Game import Game

moves = ['e2e4', 'd7d5', 'e4d5', 'd8d5', 'c2c4', 'd5c4', 'g1f3', 'c4c1', 'd1c1', 'g8f6', 'f3d4', 'f6e4', 'd4e6', 'c8e6','c1c3','e4c3','b2c3','b8c6','a2a4','c6e5','f2f4','e5c4','d2d4','e8c8','f1c4','d8d4','c3d4','e6d7','b1c3','c8d8','e1c1','d7g4','c3b5','g4d1','b5a7','b7b5','a7b5','c7c5','b5c3','c5d4','c3e2']

g = Game()

for move in moves:
    if not g.do_str_move(move):
        print('failed move ' + str(move))


def give_game():
    return g
