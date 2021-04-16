import sys, random
sys.path.append('../ChessEngine/')
from MonteCarloTreeSearch import MCTS
from Game import Game
from NNet import init_nnet, train_nnet
import numpy as np
import tensorflow as tf
import time

def do_self_play(num_iters, num_episodes, display = None):
    nnet = init_nnet()
    nnet.load_weights('weights/model_08_weights')
    examples = []
    improvements = 8
    for i in range(num_iters):
        for e in range(num_episodes):
            example = execute_episode(nnet, display)
            examples += example

        # examples[0] has gamestate neural network inputs
        # examples[1] has the desired policy
        # examples[2] has the desired evaluation
        print('generated examples')
        new_nnet = train_nnet(nnet, examples)
        print('trained new network')
        win_percentage = pit(new_nnet, nnet, display)
        print('pit old and new networks')
        print('win percentage:')
        print(win_percentage)
        
        if (win_percentage > 0.55):
            improvements += 1
            nnet = new_nnet
            new_nnet.save_weights('weights/model_0' + str(improvements) + '_weights')
    return nnet

def get_bot_move(game, nnet, whites_turn, mcts = None, examples = None, best_move_only = False, num_sims = 10): # 800 is probably too big for our tastes, but it is what AlphaZero used
    if (mcts is None):
        mcts = MCTS()

    for i in range(num_sims):
        #start = time.perf_counter()
        mcts.search(game, nnet)
        #end = time.perf_counter()
        #print('search took: ' + str(end - start))
            
    s = game.get_board_hash()
    policy = mcts.pi(s)
    if (examples is not None):
        examples.append([game.get_nnet_inputs(), policy, None]) # none is because we don't know what the desired result should be yet
    move = None
    max_policy = -1
    valid_moves = []
    valid_move_probs = []
    for test_move in game.get_legal_moves():
        index = test_move.get_nnet_index(whites_turn)
        policy_val = policy[index]
        if (not best_move_only):
            valid_moves.append(test_move)
            valid_move_probs.append(policy_val)
        elif (policy_val > max_policy): # find the maximum likelihood move that is legal
            max_policy = policy_val
            move = test_move

    if (not best_move_only):
        #print(valid_moves)
        #print(valid_move_probs)
        try:
            move = np.random.choice(valid_moves, 1, p = valid_move_probs)[0]
        except:
            print('couldnt randomly select move from policy')
            move = random.choice(game.get_legal_moves())
        #print(move)
            
    if (move == None):
        print('error, policy move does not correspond to legal move')
        move = random.choice(game.get_legal_moves())

    return move

def execute_episode(nnet, display):
    examples = []
    mcts = MCTS()

    game = Game()

    if (display is not None):
        display.set_game(game)
        display.refresh()

    whites_turn = True

    print('episode start')

    while True:
        move = get_bot_move(game, nnet, whites_turn, mcts = mcts, examples = examples)
        #print(move)
        game.do_move(move)
        
        if (display is not None):
            display.refresh()
            
        status = game.is_game_over(print_reason = True)
        if (status != -1):
            examples = assign_rewards(examples, status)
            return examples
            
        whites_turn = not whites_turn

def assign_rewards(examples, reward):
    for example in examples[::-1]:
        example[2] = reward
        reward = -reward

    return examples

def pit(nnet_one, nnet_two, display, num_games = 5):
    num_wins = 0
    for i in range(num_games):
        print('------------------New game------------------')
        if (i < (num_games / 2)):
            print('new net with the white pieces, old net with the black')
            player_one = nnet_one
            player_two = nnet_two
        else:
            print('old net with the white pieces, new net with the black')
            player_one = nnet_two
            player_two = nnet_one
        mcts_one = MCTS()
        mcts_two = MCTS()
        
        playing = True
        whites_turn = True
        game = Game()

        if (display is not None):
            display.set_game(game)
            display.refresh()
        
        while playing:
            if (whites_turn):
                player_nnet = player_one
                player_mcts = mcts_one
            else:
                player_nnet = player_two
                player_mcts = mcts_two
            
            move = get_bot_move(game, player_nnet, whites_turn, mcts = player_mcts)
            #print(move)
            if (display is not None):
                display.refresh()

            game.do_move(move)
            status = game.is_game_over(print_reason = True)
            if (status != -1):
                if (status == 0):
                    print('new bot drew')
                    num_wins += 0.5
                elif (whites_turn == (i < (num_games / 2))):
                    print('new bot won')
                    num_wins += 1
                    
                playing = False
                
            whites_turn = not whites_turn

    return (num_wins / num_games)














        
        
