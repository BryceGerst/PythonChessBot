import numpy as np
from math import sqrt

class MCTS:
    # We have Q[s][a], which returns the expected reward for making a move whose string representation
    # is a from the game board whose hash value is s.
    # We have N[s][a], which returns the number of times that we have explored making a move whose string
    # representation is a from the game board whose hash value is s.
    # Finally, we have P[s][a], which returns the initial probablility of making a move whose string
    # representation is a from the game board whose hash value is s. (aka the policy)
    # These will all be stored as dictionaries (hash tables) with the board hash as a key and an array
    # of size 4672 as values.
    def __init__(self):
        self.Q = {}
        self.N = {}
        self.P = {}
        self.visited = set()
        # visited and P should have the same number of elements in them

        # c_punct "is a hyperparameter that controls the degree of exploration"
        # hyperparameter means that it is external to the model itself
        self.c_punct = 0.2

    def search(self, game, nnet):
        end_value = game.is_game_over()
        if (end_value != -1):
            return -end_value

        s = game.get_board_hash()

        if (s not in self.visited):
            self.visited.add(s)
            self.P[s], v = nnet.predict([game.get_nnet_inputs()])
            self.Q[s] = np.zeros([4672], np.dtype(float))
            self.N[s] = np.zeros([4672], np.dtype(float))
            return -v

        max_u, best_move = -float("inf"), -1

        for move in game.get_legal_moves():
            a = move.get_nnet_index(game.get_team_to_move)
            u = self.Q[s][a] + (self.c_punct * self.P[s][a] * sqrt(sum(self.N[s])) / (1 + self.N[s][a]))
            if u > max_u:
                max_u = u
                best_move = move

        move = best_move

        game.do_move(move)
        v = self.search(game, nnet)
        game.undo_move()

        self.Q[s][a] = (self.N[s][a] * self.Q[s][a] + v) / (self.N[s][a] + 1)
        self.N[s][a] += 1
        return -v

    def pi(self, s):
        if (s in self.P):
            return self.P[s]
        else:
            print('error, gamestate not found')
            return None
    






# https://web.stanford.edu/~surag/posts/alphazero.html
