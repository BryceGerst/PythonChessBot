import pygame, sys, random
sys.path.append('../ChessEngine/')
from Game import Game
sys.path.append('../Bot/')
import Bot
from NNet import init_nnet, train_nnet
from MonteCarloTreeSearch import MCTS
import numpy as np
import tensorflow as tf


pygame.init()
pygame.mixer.init()

# screen parameters
square_side_length = 80 # in pixels
screen_w = square_side_length * 8
screen_h = square_side_length * 8

# image loading
def load_piece(file_name): # The file_name parameter should include .png, .jpg, etc.
    return pygame.transform.scale(pygame.image.load('Images/' + file_name), (square_side_length, square_side_length))

black_pawn = load_piece('blackPawn.png')
black_rook = load_piece('blackRook.png')
black_bishop = load_piece('blackBishop.png')
black_knight = load_piece('blackKnight.png')
black_queen = load_piece('blackQueen.png')
black_king = load_piece('blackKing.png')
white_pawn = load_piece('whitePawn.png')
white_rook = load_piece('whiteRook.png')
white_bishop = load_piece('whiteBishop.png')
white_knight = load_piece('whiteKnight.png')
white_queen = load_piece('whiteQueen.png')
white_king = load_piece('whiteKing.png')

dark_square = load_piece('darkSquare.png')
light_square = load_piece('lightSquare.png')
highlight_square = load_piece('highlightSquare.png')

possibility_circle = load_piece('possibleMove.png')

def get_piece_image(piece_str):
    team = (piece_str[0:1] == 'w')
    piece_name = piece_str[1:]
    if (team):
        if (piece_name == 'Pa'):
            return white_pawn
        elif (piece_name == 'Ro'):
            return white_rook
        elif (piece_name == 'Bi'):
            return white_bishop
        elif (piece_name == 'Kn'):
            return white_knight
        elif (piece_name == 'Qu'):
            return white_queen
        elif (piece_name == 'Ki'):
            return white_king
    else:
        if (piece_name == 'Pa'):
            return black_pawn
        elif (piece_name == 'Ro'):
            return black_rook
        elif (piece_name == 'Bi'):
            return black_bishop
        elif (piece_name == 'Kn'):
            return black_knight
        elif (piece_name == 'Qu'):
            return black_queen
        elif (piece_name == 'Ki'):
            return black_king

    return None

# audio loading

def load_sound(file_name):
    return pygame.mixer.Sound('Audio/' + file_name)

move_noises = []
for i in range(0, 7):
    move_noises.append(load_sound('pieceMove' + str(i) + '.wav'))


# manual input to bot example
def make_policy(move, team):
    policy = np.zeros([4672], np.dtype(float))
    policy[move.get_nnet_index(team)] = 1
    return policy

# main loop

ChessGame = Game()#test_game.give_game()
screen = pygame.display.set_mode([screen_w, screen_h])
playing = True

click1_pos = (-1, -1)
click2_pos = (-1, -1)
highlight_coords = (-1, 1)
possible_move_coords = []
A = 97 # char(97) is 'a'

mouse_down_last_frame = False
keys_down_last_frame = []
for i in range(512):
    keys_down_last_frame.append(False)
refresh_display = True

num_games = 1
games_played = 0
is_bot_turn = False

total_examples = []
current_example = []

#nnet = tf.keras.models.load_model('model2')#init_nnet() # later I will load one in
nnet = init_nnet()
nnet.load_weights('weights/model_10_weights')
mcts = MCTS()

while (playing and games_played < num_games):
    for event in pygame.event.get():
        if (event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]): # key 27 is escape
            playing = False

    if (not is_bot_turn):
        clicked = False
        mouse_down = pygame.mouse.get_pressed()[0]
        clicked = mouse_down and not mouse_down_last_frame
    else:
        bot_move = Bot.get_bot_move(ChessGame, nnet, ChessGame.get_team_to_move(), mcts = mcts, examples = current_example, best_move_only = True)
        ChessGame.do_move(bot_move)
        random.choice(move_noises).play()
        refresh_display = True
        click1_pos = (-1, -1)
        click2_pos = (-1, -1)
        clicked = False
        highlight_coords = (-1, 1)
        possible_move_coords = []
        is_bot_turn = False

    refresh_display = (refresh_display or clicked)

    if (refresh_display):
        screen.fill((255, 255, 255))
        
        if (clicked and click1_pos != (-1, -1)):
            click2_pos = pygame.mouse.get_pos()
        elif (clicked):
            click1_pos = pygame.mouse.get_pos()
            click2_pos = (-1, -1)
            
        if (click2_pos != (-1, -1)):
            # rows are inverted since we put the black pieces on the top
            end_row = 7 - (click2_pos[1] // square_side_length)
            end_col = (click2_pos[0] // square_side_length)
            if (ChessGame.is_square_friendly(end_row, end_col)): # changing the piece you want to move
                click1_pos = click2_pos
                click2_pos = (-1, -1)
                highlight_coords = (-1, 1)
                possible_move_coords = []
            else:
                move_str = (chr(start_col + A) + str(start_row + 1) + chr(end_col + A) + str(end_row + 1))
                team = ChessGame.get_team_to_move()
                nnet_inputs = ChessGame.get_nnet_inputs()
                real_move = ChessGame.do_str_move(move_str)
                if (real_move is not None):
                    policy = make_policy(real_move, team) # the team just changed, but we want the old
                    current_example.append([nnet_inputs, policy, None])
                    random.choice(move_noises).play()
                    is_bot_turn = True
                click1_pos = (-1, -1)
                click2_pos = (-1, -1)
                highlight_coords = (-1, 1)
                possible_move_coords = []
            
        if (click1_pos != (-1, 1)):
            start_row = 7 - (click1_pos[1] // square_side_length)
            start_col = (click1_pos[0] // square_side_length)
            highlight_coords = (start_col * square_side_length, (7 - start_row) * square_side_length)
            if (not ChessGame.is_square_friendly(start_row, start_col)):
                click1_pos = (-1, -1)
                click2_pos = (-1, -1)
                highlight_coords = (-1, 1)
                possible_move_coords = []
            else:
                legal_move_squares = ChessGame.legal_moves_from_square(start_row, start_col)
                for square in legal_move_squares:
                    possible_coord = (square[1] * square_side_length, ((7 - square[0]) * square_side_length))
                    possible_move_coords.append(possible_coord)
        
        is_dark_square = False
        for y in range(0, screen_h, square_side_length):
            for x in range(0, screen_w, square_side_length):
                if ((x, y) == highlight_coords):
                    screen.blit(highlight_square, (x, y))
                elif (is_dark_square):
                    screen.blit(dark_square, (x, y))
                else:
                    screen.blit(light_square, (x, y))
                is_dark_square = not is_dark_square
            is_dark_square = not is_dark_square
        
        pieces = ChessGame.get_pieces()
        for piece in pieces:
            piece_sprite = get_piece_image(str(piece))
            x = (piece.col * square_side_length)
            y = ((7 - piece.row) * square_side_length)
            screen.blit(piece_sprite, (x, y))

        for coord in possible_move_coords:
            screen.blit(possibility_circle, coord)
            
        pygame.display.update()
            
    mouse_down_last_frame = mouse_down
    refresh_display = False

    result = ChessGame.is_game_over(print_reason = True)
    if (result != -1):
        current_example = Bot.assign_rewards(current_example, result)
        games_played += 1
        total_examples += current_example
        is_bot_turn = not (games_played < (num_games / 2))
        ChessGame = Game()
        refresh_display = True
        current_example = []

pygame.quit()

if (playing):
    new_nnet = train_nnet(nnet, total_examples)
    new_nnet.save_weights('weights/model_11_weights')



sys.exit()

    


