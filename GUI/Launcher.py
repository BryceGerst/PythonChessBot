import pygame, sys, random
sys.path.append('../ChessEngine/')
from Game import Game
#import test_game


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

while (playing):
    for event in pygame.event.get():
        if (event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]): # key 27 is escape
            playing = False

    keys_down = pygame.key.get_pressed()
    if (keys_down[pygame.K_u]):# and not keys_down_last_frame[pygame.K_u]):
        ChessGame.undo_move()
        print('undo')
        refresh_display = True
        click1_pos = (-1, -1)
        click2_pos = (-1, -1)
        highlight_coords = (-1, 1)
        possible_move_coords = []
    elif (keys_down[pygame.K_b]):# and not keys_down_last_frame[pygame.K_b]):
        moves = ChessGame.get_legal_moves()
        if (len(moves) > 0):
            move = random.choice(moves)
            ChessGame.do_move(move)
            print(move)
            random.choice(move_noises).play() # make a noise if the move was valid

        refresh_display = True
        click1_pos = (-1, -1)
        click2_pos = (-1, -1)
        highlight_coords = (-1, 1)
        possible_move_coords = []

    clicked = False
    mouse_down = pygame.mouse.get_pressed()[0]
    clicked = mouse_down and not mouse_down_last_frame

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
                if (ChessGame.do_str_move(move_str)):
                    print(move_str)
                    random.choice(move_noises).play() # make a noise if the move was valid
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
    keys_down_last_frame = keys_down
    refresh_display = False



pygame.quit()
sys.exit()

    


