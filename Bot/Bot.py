import sys, random
sys.path.append('../ChessEngine/')
from MonteCarloTreeSearch import MCTS
from Game import Game
from NNet import NNetWrapper
import numpy as np

def init_nnet():
    return NNetWrapper()

def train_nnet(num_iters, num_episodes):
    nnet = init_nnet()
    examples = []
    improvement = 0
    for i in range(num_iters):
        for e in range(num_episodes):
            example = execute_episode(nnet)
            examples += example

        # examples[0] has gamestate neural network inputs
        # examples[1] has the desired policy
        # examples[2] has the desired evaluation
        new_nnet = nnet.train(examples)
        win_percentage = pit(new_nnet, nnet)
        
        if (win_percentage > 0.55):
            improvements += 1
            nnet = new_nnet
            nnet.save_checkpoint(filename = ('model' + str(improvement)))
    return nnet


def execute_episode(nnet, num_sims = 1): # 800 is probably too big for our tastes, but it is what AlphaZero used
    examples = []
    mcts = MCTS()

    game = Game()

    whites_turn = True

    print('episode start')

    while True:
        for i in range(num_sims):
            mcts.search(game, nnet)
            
        s = game.get_board_hash()
        policy = mcts.pi(s)
        examples.append([game.get_nnet_inputs(), policy, None]) # none is because we don't know what the desired result should be yet
        move = None
        max_policy = -1
        for test_move in game.get_legal_moves():
            index = test_move.get_nnet_index(whites_turn)
            policy_val = policy[index]
            if (policy_val > max_policy): # find the maximum likelihood move that is legal
                max_policy = policy_val
                move = test_move
                
        if (move == None):
            print('error, policy move does not correspond to legal move')
            move = random.choice(game.get_legal_moves())

        game.do_move(move)
        status = game.is_game_over()
        if (status != -1):
            examples = assign_rewards(examples, status, whites_turn)
            return examples
            
        whites_turn = not whites_turn

def assign_rewards(examples, reward, whites_turn):
    if (whites_turn):
        start = reward
    else:
        start = -reward

    current = start
    for example in examples:
        example[2] = current
        current = -current

    return examples

def pit(nnet_one, nnet_two, num_games = 10):
    for i in range(num_games):
        if (i < (num_games / 2)):
            player_one = nnet_one
            player_two = nnet_two
        else:
            player_one = nnet_two
            player_two = nnet_one















        
        
