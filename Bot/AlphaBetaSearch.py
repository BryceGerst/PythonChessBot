import numpy as np
from math import sqrt
import time

board_height = 8
board_width = 8
num_channels = 20

class MemNode:
    def __init__(self, best_move, depth_searched, node_value):
        self.best_move = best_move
        self.depth_searched = depth_searched
        self.node_value = node_value

class ABS:
    def __init__(self):
        self.memory = {}
        self.quiesce_memory = {}

    def get_move(self, game, nnet, max_depth=5):
        best_move = None
        best_score = -100
        depth = 1
        while depth <= max_depth:
            for move in game.get_legal_moves():
                game.do_move(move)
                result = self.alpha_beta(game, nnet, -100, 100, depth-1)
                game.undo_move()
                score = -result
                if score > best_score:
                    best_score = score
                    best_move = move
            if best_score == 1:
                return best_move # found mate
            depth += 1
        return best_move

    def alpha_beta(self, game, nnet, alpha, beta, depth_left):
        if depth_left == 0:
            return self.quiesce(game, nnet, alpha, beta)

        end_value = game.is_game_over()
        if end_value != -1:
            return -end_value
        
        s = game.get_board_hash()
        best_move = None
        remembered_board = False
        if s in self.memory:
            mem_node = self.memory[s]
            best_move = mem_node.best_move
            remember_depth = mem_node.depth_searched
            remembered_board = True
            if True: # if we were not overconfident we would check if the move we remember is valid
                if remember_depth >= depth_left:
                    return mem_node.node_value
                game.do_move(best_move)
                result = alpha_beta(-beta, -alpha, depth_left - 1)
                game.undo_move()

                score = -result

                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score

        for move in game.get_legal_moves():
            if (best_move is None) or (str(move) != str(best_move)):
                game.do_move(move)
                result = self.alpha_beta(game, nnet, -beta, -alpha, depth_left - 1)
                game.undo_move()

                score = -result

                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
                    best_move = move

        if best_move is not None and (not remembered_board or depth_left > remember_depth):
            self.memory[s] = MemNode(best_move, depth_left, alpha)

        return alpha

    def quiesce(self, game, nnet, alpha, beta):
        end_value = game.is_game_over()
        if end_value != -1:
            return -end_value
        
        s = game.get_board_hash()
        best_move = None
        if s in self.quiesce_memory:
            mem_node = self.quiesce_memory[s]
            best_move = mem_node.best_move
            remember_depth = mem_node.depth_searched
            if True: # if we were not overconfident we would check if the move we remember is valid
                return mem_node.node_value

        inputs = game.get_nnet_inputs()
        inputs = np.array(inputs)
        inputs = inputs.reshape(1, board_height, board_width, num_channels)
        current_score = nnet(inputs)

        if current_score >= beta:
            return beta
        if alpha < current_score:
            alpha = current_score

##        for move in game.get_legal_moves():
##            if move.is_capture:
##                game.do_move(move)
##                result = self.quiesce(game, nnet, -beta, -alpha)
##                game.undo_move()
##
##                score = -result
##
##                if score >= beta:
##                    return beta
##                if score > alpha:
##                    alpha = score
##                    best_move = move

        self.quiesce_memory[s] = MemNode(best_move, 0, alpha)

        return alpha
