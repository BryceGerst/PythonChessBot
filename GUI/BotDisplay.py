import pygame, sys, random
sys.path.append('../ChessEngine/')
from Game import Game
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

#import test_game


pygame.init()
pygame.mixer.init()

# screen parameters
square_side_length = 80 # in pixels
screen_w = square_side_length * 8
screen_h = square_side_length * 8

# image loading
def load_piece(file_name): # The file_name parameter should include .png, .jpg, etc.
    return pygame.transform.scale(pygame.image.load(dir_path + '/Images/' + file_name), (square_side_length, square_side_length))

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
    return pygame.mixer.Sound(dir_path + '/Audio/' + file_name)

move_noises = []
for i in range(0, 7):
    move_noises.append(load_sound('pieceMove' + str(i) + '.wav'))

class Display:
    def __init__(self):
        self.ChessGame = None
        self.screen = pygame.display.set_mode([screen_w, screen_h])
        self.refresh()

    def set_game(self, game):
        self.ChessGame = game

    def refresh(self):
        pygame.event.get()
        self.screen.fill((255, 255, 255))
        random.choice(move_noises).play()
        is_dark_square = False
        for y in range(0, screen_h, square_side_length):
            for x in range(0, screen_w, square_side_length):
                if (is_dark_square):
                    self.screen.blit(dark_square, (x, y))
                else:
                    self.screen.blit(light_square, (x, y))
                is_dark_square = not is_dark_square
            is_dark_square = not is_dark_square

        if (self.ChessGame is not None):
            pieces = self.ChessGame.get_pieces()
            for piece in pieces:
                piece_sprite = get_piece_image(str(piece))
                x = (piece.col * square_side_length)
                y = ((7 - piece.row) * square_side_length)
                self.screen.blit(piece_sprite, (x, y))

        pygame.display.update()


































        
