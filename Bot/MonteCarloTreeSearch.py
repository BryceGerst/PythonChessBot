import numpy as np
from math import sqrt
import time

board_height = 8
board_width = 8
num_channels = 20

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

        # c_puct "is a hyperparameter that controls the degree of exploration"
        # hyperparameter means that it is external to the model itself
        self.c_puct = 0.2

    def search(self, game, nnet):
        end_value = game.is_game_over()
        if (end_value != -1):
            return -end_value

        s = game.get_board_hash()

        if (s not in self.visited):
            self.visited.add(s)
            
            inputs = game.get_nnet_inputs()
            inputs = np.array(inputs)
            inputs = inputs.reshape(1, board_height, board_width, num_channels)
            
            #start = time.perf_counter()
            policy, value = nnet(inputs)
            #end = time.perf_counter()
            #print('nnet access took: ' + str(end - start))
            
            self.P[s] = policy[0]
            #print(self.P[s])
            v = value[0]
            self.Q[s] = np.zeros([4672], np.dtype(float))
            self.N[s] = np.zeros([4672], np.dtype(float))
            return -v

        max_u, best_move, best_a = -float("inf"), -1, -1

        for move in game.get_legal_moves():
            a = move.get_nnet_index(game.get_team_to_move())
            u = self.Q[s][a] + (self.c_puct * self.P[s][a] * sqrt(sum(self.N[s])) / (1 + self.N[s][a]))
            if u > max_u:
                max_u = u
                best_move = move
                best_a = a

        #move = best_move

        game.do_move(best_move)
        v = self.search(game, nnet)
        game.undo_move()

        self.Q[s][best_a] = (self.N[s][best_a] * self.Q[s][best_a] + v) / (self.N[s][best_a] + 1)
        self.N[s][best_a] += 1
        return -v

    def pi(self, s):
        if (s in self.N):
            improved_policy = np.zeros([4672], np.dtype(float))
            total_actions_checked = sum(self.N[s])
            #print('checked:')
            #print(total_actions_checked)
            
            for i in range(len(self.N[s])):
                improved_policy[i] = (self.N[s][i] / total_actions_checked)
                
            return improved_policy
        else:
            print('error, gamestate not found')
            return None
    






# https://web.stanford.edu/~surag/posts/alphazero.html
