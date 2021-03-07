import numpy as np
from Move import Move

class Piece:
    def __init__(self, row, col, team, piece_id):
        # row and col are integers 0 through 7 inclusive
        self.row = row
        self.col = col
        # the piece_id is the unique number that corresponds to each piece. This is used for keeping track of which piece is captured and on which turn
        self.piece_id = piece_id
        # team is a boolean where True means white and False means black
        self.team = team
        # possible_moves keeps track of the piece's available moves to make
        # move generation more efficient
        self.possible_moves = []
        # alive is used by the board to determine if it should consider any actions with this piece
        self.alive = True
        # dependent_on_square keeps track of the squares where this piece's
        # available moves are dependent on
        self.dependent_on_square = np.zeros([8,8], np.dtype(bool))

    def can_move_to(self, end_row, end_col, board):
        if (end_row >= 0 and end_row < board.num_rows and end_col >= 0 and end_col < board.num_cols):
            self.dependent_on_square[end_row][end_col] = True
            check_piece = board.get_piece_at(end_row, end_col)
            if (check_piece == None): # means the square is empty, so yes the piece can move there
                self.possible_moves.append(Move(self.row, self.col, end_row, end_col, self.name))
            elif (check_piece.team != self.team): # means it is an enemy piece, so the piece can move there and it is a capture
                self.possible_moves.append(Move(self.row, self.col, end_row, end_col, self.name, is_capture = True, capture_name = check_piece.name, capture_id = check_piece.piece_id))
            return True
        
        else: # means either the desired square is occupied by a friendly piece or the index is out of bounds
            return False

    def dependent_on_move(self, move):
        end_dependent = self.dependent_on_square[move.end_row][move.end_col]
        if (move.is_qs_castle):
            end_dependent = end_dependent or self.dependent_on_square[move.end_row][move.end_col + 1] or self.dependent_on_square[move.end_row][move.end_col - 1] or self.dependent_on_square[move.end_row][move.end_col - 2]
        if (move.is_ks_castle):
            end_dependent = end_dependent or self.dependent_on_square[move.end_row][move.end_col - 1] or self.dependent_on_square[move.end_row][move.end_col + 1]
            
        start_dependent = self.dependent_on_square[move.start_row][move.start_col]
        capture_dependent = move.is_ep and self.dependent_on_square[move.start_row][move.end_col]
        return (start_dependent or end_dependent or capture_dependent)

    def __str__(self):
        return (('w' if self.team else 'b') + self.name[0:2])

# all the names of pieces that a pawn could potentially promote to
promotion_names = ["Queen", "Knight", "Rook", "Bishop"]

class Pawn(Piece):
    def __init__(self, row, col, team, piece_id):
        super().__init__(row, col, team, piece_id)
        self.name = "Pawn"
        # the following condition initializes values for pawn movement, since they can only move in one direction from where they begin
        if (team): # true if on white team
            self.start_row = 1
            self.direction = 1
        else: # false if on black team
            self.start_row = 6
            self.direction = -1

    def gen_moves(self, board, latest_move, is_undo = False): # returns a Piece object, in most situations it will be this pawn, but in the case of a promotion it may not be
        self.dependent_on_square = np.zeros([8,8], np.dtype(bool))
        self.possible_moves = []
        signs = [-1, 0, 1]

        my_pos = (self.row, self.col)
        # lm is short for latest move
        if (latest_move != None):
            lm_start_pos = (latest_move.start_row, latest_move.start_col)
            lm_end_pos = (latest_move.end_row, latest_move.end_col)

            if (is_undo and my_pos == lm_end_pos and not self.piece_id == latest_move.capture_id):
                self.row, self.col = lm_start_pos

        if (latest_move != None and not is_undo and lm_start_pos == my_pos): # means this piece moved on the latest move
            self.row, self.col = lm_end_pos
            
            if (latest_move.is_promotion):
                #print('promoting pawn')
                if (latest_move.piece_name == "Queen"):
                    new_piece = Queen(self.row, self.col, self.team, self.piece_id)
                elif (latest_move.piece_name == "Knight"):
                    new_piece = Knight(self.row, self.col, self.team, self.piece_id)
                elif (latest_move.piece_name == "Rook"):
                    new_piece = Rook(self.row, self.col, self.team, self.piece_id)
                elif (latest_move.piece_name == "Bishop"):
                    new_piece = Bishop(self.row, self.col, self.team, self.piece_id)
                else: # this should never be reached, but if for whatever reason it is, we will default the promotion to a queen
                    new_piece = Queen(self.row, self.col, self.team, self.piece_id)
                    
                new_piece.gen_moves(board, None)
                return new_piece

        self.dependent_on_square[self.row][self.col] = True
        end_row = self.row + self.direction
        for sign in signs: # checks if it can move forward, forward left, or forward right
            end_col = self.col + sign
            self.can_move_to(end_row, end_col, board)
        if (self.row == self.start_row): # checks if it is on the starting rank, and if it is, checks if it can move forward twice
            self.can_move_to(self.row + (2 * self.direction), self.col, board)
        if (self.row == (self.start_row + (3 * self.direction))): # checks if it is on a potential en passant row, and sets dependencies to its left and right if it is
            if (self.col - 1 >= 0):
                self.dependent_on_square[self.row][self.col - 1] = True
            if (self.col + 1 < board.num_cols):
                self.dependent_on_square[self.row][self.col + 1] = True
            
        return self

        

    def can_move_to(self, end_row, end_col, board):
        if (end_row >= 0 and end_row < board.num_rows and end_col >= 0 and end_col < board.num_cols):
            self.dependent_on_square[end_row][end_col] = True
            check_piece = board.get_piece_at(end_row, end_col)

            if (self.col == end_col and check_piece == None): # moving forwards to an empty square
                if (end_row == (self.start_row + (6 * self.direction))): # moving forwards to a promotion square
                    for piece_name in promotion_names:
                        self.possible_moves.append(Move(self.row, self.col, end_row, end_col, piece_name, is_promotion = True))
                    return True
                elif (self.row == self.start_row and end_row == (self.start_row + (2 * self.direction))): # moving forwards twice from starting rank
                    if (board.get_piece_at(self.start_row + self.direction, end_col) == None): # if the square directly ahead is also empty
                        self.possible_moves.append(Move(self.row, self.col, end_row, end_col, self.name))
                        return True
                else: # moving forwards one square under normal circumstances
                    self.possible_moves.append(Move(self.row, self.col, end_row, end_col, self.name))
                    return True
                
            else:
                if (check_piece != None and end_col != self.col and check_piece.team != self.team): # diagonal capture
                    if (end_row == (self.start_row + (6 * self.direction))): # capturing diagonally onto a promotion square
                        for piece_name in promotion_names:
                            self.possible_moves.append(Move(self.row, self.col, end_row, end_col, piece_name, is_capture = True, capture_name = check_piece.name, capture_id = check_piece.piece_id, is_promotion = True))
                        return True
                    else: # good old fashioned regular diagonal capture
                        self.possible_moves.append(Move(self.row, self.col, end_row, end_col, self.name, is_capture = True, capture_name = check_piece.name, capture_id = check_piece.piece_id))
                        return True
                elif (end_col == board.en_passant_col and self.row == (self.start_row + (3 * self.direction))): # capturing en passant
                    check_piece = board.get_piece_at(self.row, end_col)
                    if (check_piece != None and check_piece.team != self.team and check_piece.name == "Pawn"):
                        self.possible_moves.append(Move(self.row, self.col, end_row, end_col, self.name, is_capture = True, capture_name = check_piece.name, capture_id = check_piece.piece_id, is_ep = True))
                        return True
                
        return False


class Queen(Piece):
    def __init__(self, row, col, team, piece_id):
        super().__init__(row, col, team, piece_id)
        self.name = "Queen"

    def gen_moves(self, board, latest_move, is_undo = False):
        self.dependent_on_square = np.zeros([8,8], np.dtype(bool))
        self.possible_moves = []
        signs = [-1, 0, 1]

        my_pos = (self.row, self.col)
        # lm is short for latest move
        if (latest_move != None):
            lm_start_pos = (latest_move.start_row, latest_move.start_col)
            lm_end_pos = (latest_move.end_row, latest_move.end_col)

            if (is_undo and my_pos == lm_end_pos and not self.piece_id == latest_move.capture_id):
                self.row, self.col = lm_start_pos
            elif (not is_undo and my_pos == lm_start_pos):
                self.row, self.col = lm_end_pos

        self.dependent_on_square[self.row][self.col] = True
        for x_sign in signs:
            for y_sign in signs:
                if (not(x_sign == 0 and y_sign == 0)):
                    magnitude = 1
                    has_los = True # los stands for line of sight

                    while (has_los):
                        test_row = self.row + (magnitude * y_sign)
                        test_col = self.col + (magnitude * x_sign)

                        if (test_row >= 0 and test_row < board.num_rows and test_col >= 0 and test_col < board.num_cols): # checks if the test location is in bounds, not redundent because we need to check the board itself too
                            self.can_move_to(test_row, test_col, board)
                            if (board.get_piece_at(test_row, test_col) != None): # line of sight is lost after hitting any piece
                                has_los = False
                        else: # if the test position is out of bounds line of sight is certainly broken
                            has_los = False

                        magnitude += 1

        return self


class Rook(Piece):
    def __init__(self, row, col, team, piece_id):
        super().__init__(row, col, team, piece_id)
        self.name = "Rook"

    def gen_moves(self, board, latest_move, is_undo = False):
        self.dependent_on_square = np.zeros([8,8], np.dtype(bool))
        self.possible_moves = []
        signs = [-1, 0, 1]

        my_pos = (self.row, self.col)
        # lm is short for latest move
        if (latest_move != None):
            lm_start_pos = (latest_move.start_row, latest_move.start_col)
            lm_end_pos = (latest_move.end_row, latest_move.end_col)

            if (is_undo and my_pos == lm_end_pos and not self.piece_id == latest_move.capture_id):
                self.row, self.col = lm_start_pos
            elif (not is_undo and my_pos == lm_start_pos):
                self.row, self.col = lm_end_pos

        self.dependent_on_square[self.row][self.col] = True
        for x_sign in signs:
            for y_sign in signs:
                if (x_sign * y_sign == 0 and x_sign + y_sign != 0):
                    magnitude = 1
                    has_los = True # los stands for line of sight

                    while (has_los):
                        test_row = self.row + (magnitude * y_sign)
                        test_col = self.col + (magnitude * x_sign)

                        if (test_row >= 0 and test_row < board.num_rows and test_col >= 0 and test_col < board.num_cols): # checks if the test location is in bounds, not redundent because we need to check the board itself too
                            self.can_move_to(test_row, test_col, board)
                            if (board.get_piece_at(test_row, test_col) != None): # line of sight is lost after hitting any piece
                                has_los = False
                        else: # if the test position is out of bounds line of sight is certainly broken
                            has_los = False

                        magnitude += 1

        return self


class Bishop(Piece):
    def __init__(self, row, col, team, piece_id):
        super().__init__(row, col, team, piece_id)
        self.name = "Bishop"

    def gen_moves(self, board, latest_move, is_undo = False):
        self.dependent_on_square = np.zeros([8,8], np.dtype(bool))
        self.possible_moves = []
        signs = [-1, 1]

        my_pos = (self.row, self.col)
        # lm is short for latest move
        if (latest_move != None):
            lm_start_pos = (latest_move.start_row, latest_move.start_col)
            lm_end_pos = (latest_move.end_row, latest_move.end_col)

            if (is_undo and my_pos == lm_end_pos and not self.piece_id == latest_move.capture_id):
                self.row, self.col = lm_start_pos
            elif (not is_undo and my_pos == lm_start_pos):
                self.row, self.col = lm_end_pos

        self.dependent_on_square[self.row][self.col] = True
        for x_sign in signs:
            for y_sign in signs:
                magnitude = 1
                has_los = True # los stands for line of sight

                while (has_los):
                    test_row = self.row + (magnitude * y_sign)
                    test_col = self.col + (magnitude * x_sign)

                    if (test_row >= 0 and test_row < board.num_rows and test_col >= 0 and test_col < board.num_cols): # checks if the test location is in bounds, not redundent because we need to check the board itself too
                        self.can_move_to(test_row, test_col, board)
                        if (board.get_piece_at(test_row, test_col) != None): # line of sight is lost after hitting any piece
                            has_los = False
                    else: # if the test position is out of bounds line of sight is certainly broken
                        has_los = False

                    magnitude += 1

        return self


class Knight(Piece):
    def __init__(self, row, col, team, piece_id):
        super().__init__(row, col, team, piece_id)
        self.name = "Knight"

    def gen_moves(self, board, latest_move, is_undo = False):
        self.dependent_on_square = np.zeros([8,8], np.dtype(bool))
        self.possible_moves = []
        signs = [-2, -1, 1, 2]

        my_pos = (self.row, self.col)
        # lm is short for latest move
        if (latest_move != None):
            lm_start_pos = (latest_move.start_row, latest_move.start_col)
            lm_end_pos = (latest_move.end_row, latest_move.end_col)

            if (is_undo and my_pos == lm_end_pos and not self.piece_id == latest_move.capture_id):
                self.row, self.col = lm_start_pos
            elif (not is_undo and my_pos == lm_start_pos):
                self.row, self.col = lm_end_pos

        self.dependent_on_square[self.row][self.col] = True
        for x_sign in signs:
            for y_sign in signs:
                if (abs(x_sign * y_sign) == 2):
                    test_row = self.row + y_sign
                    test_col = self.col + x_sign
                    self.can_move_to(test_row, test_col, board)

        return self


class King(Piece):
    def __init__(self, row, col, team, piece_id):
        super().__init__(row, col, team, piece_id)
        self.name = "King"
        self.can_castle_queenside = True
        self.can_castle_kingside = True
        if (team):
            self.start_pos = (0, 4)
            self.queenside_rook_pos = (0, 0)
            self.kingside_rook_pos = (0, 7)
        else:
            self.start_pos = (7, 4)
            self.queenside_rook_pos = (7, 0)
            self.kingside_rook_pos = (7, 7)

    def gen_moves(self, board, latest_move, is_undo = False):
        self.dependent_on_square = np.zeros([8,8], np.dtype(bool))
        self.possible_moves = []
        signs = [-1, 0, 1]

        my_pos = (self.row, self.col)
        # lm is short for latest move
        if (latest_move != None):
            lm_start_pos = (latest_move.start_row, latest_move.start_col)
            lm_end_pos = (latest_move.end_row, latest_move.end_col)

            if (is_undo and my_pos == lm_end_pos and not self.piece_id == latest_move.capture_id):
                self.row, self.col = lm_start_pos
            elif (not is_undo and my_pos == lm_start_pos):
                self.row, self.col = lm_end_pos

        self.dependent_on_square[self.row][self.col] = True
        # normal king movement in all 8 directions
        for x_sign in signs:
            for y_sign in signs:
                if (not(x_sign == 0 and y_sign == 0)):
                    test_row = self.row + y_sign
                    test_col = self.col + x_sign
                    self.can_move_to(test_row, test_col, board)
                    
        # removes castling rights if necessary
        
        if (latest_move != None and not is_undo):
            if (lm_start_pos == self.start_pos or lm_end_pos == self.start_pos): # if the king moves you can't castle
                self.can_castle_queenside = False
                self.can_castle_kingside = False
                #print(str(self) + 'lost castling because king moved')
            if (self.can_castle_queenside and (lm_start_pos == self.queenside_rook_pos or lm_end_pos == self.queenside_rook_pos)): # if the queenside rook moves you can't castle queenside
                self.can_castle_queenside = False
                #print(str(self) + 'lost castling because queenside rook moved')
            if (self.can_castle_kingside and (lm_start_pos == self.kingside_rook_pos or lm_end_pos == self.kingside_rook_pos)): # if the kingside rook moves you can't castle kingside
                self.can_castle_kingside = False
                #print(str(self) + 'lost castling because kingside rook moved')

        # adds depedencies for castling as well as adding castling to the possible move list if applicable
        # dependencies for castling shouldn't actually matter because if castling is a possibility then the king is updated after every move, but just in case
        if (not self.is_in_check(board)):
            if (self.can_castle_queenside):
                self.dependent_on_square[self.queenside_rook_pos[0], self.queenside_rook_pos[1]] = True
                original_col = self.col
                clear_skies = True
                for i in range(3):
                    if (board.get_piece_at(self.row, self.col - 1) == None):
                        if (i != 2): # the square the rook moves through can be 'in check' but it cannot be occupied
                            self.col = self.col - 1
                            if (self.is_in_check(board)):
                                clear_skies = False
                                i = 4
                    else:
                        clear_skies = False
                        i = 4

                self.col = original_col
                if (clear_skies):
                    self.possible_moves.append(Move(self.row, self.col, self.row, self.col - 2, "King", is_qs_castle = True))
            if (self.can_castle_kingside):
                self.dependent_on_square[self.kingside_rook_pos[0], self.kingside_rook_pos[1]] = True
                original_col = self.col
                clear_skies = True
                for i in range(2):
                    if (board.get_piece_at(self.row, self.col + 1) == None):
                        self.col = self.col + 1
                        if (self.is_in_check(board)):
                            clear_skies = False
                            i = 3
                    else:
                        clear_skies = False
                        i = 3

                self.col = original_col
                if (clear_skies):
                    self.possible_moves.append(Move(self.row, self.col, self.row, self.col + 2, "King", is_ks_castle = True))
                
        # tests if the king can safely occupy the squares he moves into the squares he would travel through while castling
        

        return self

    def dependent_on_move(self, move):
        if (self.can_castle_queenside or self.can_castle_kingside):
            return True # castling is not only dependent on the pieces in between, but also the pieces putting pressure on the squares in between. Therefore if castling is a possibility, the king is dependent
                        # on every move that is made
        else: # otherwise has the same dependencies as regular pieces
            end_dependent = self.dependent_on_square[move.end_row][move.end_col]
            start_dependent = self.dependent_on_square[move.start_row][move.start_col]
            capture_dependent = move.is_ep and self.dependent_on_square[move.start_row][move.end_col]
            return (start_dependent or end_dependent or capture_dependent)

    def is_in_check(self, board): # to test this, we treat the king as some sort of queen-knight hybrid to see if he could capture anything
        # this first loop checks for enemy queens, rooks, bishops, kings, or pawns
        signs = [-1, 0, 1]
        for x_sign in signs:
            for y_sign in signs:
                if (not(x_sign == 0 and y_sign == 0)):
                    magnitude = 1
                    has_los = True # los stands for line of sight

                    while (has_los):
                        test_row = self.row + (magnitude * y_sign)
                        test_col = self.col + (magnitude * x_sign)

                        is_bishop_movement = (abs(x_sign * y_sign) == 1)
                        is_rook_movement = (x_sign * y_sign == 0)
                        is_queen_movement = is_bishop_movement or is_rook_movement
                        is_king_movement = (magnitude == 1 and is_queen_movement) # a king moves like a queen but with a magnitude of 1
                        enemy_pawn_direction = 1 if self.team else -1 # not the direction the enemy pawn moves, but the direction from which the king would be able to view them
                        is_pawn_movement = (magnitude == 1 and is_bishop_movement and y_sign == enemy_pawn_direction) # a pawn only exerts pressure diagonally, like a bishop, but also only in certain directions

                        if (test_row >= 0 and test_row < board.num_rows and test_col >= 0 and test_col < board.num_cols):
                            check_piece = board.get_piece_at(test_row, test_col)
                            if (check_piece != None): # line of sight is lost after hitting any piece
                                if (check_piece.team != self.team):
                                    if (is_bishop_movement and check_piece.name == "Bishop"):
                                        return True
                                    elif (is_rook_movement and check_piece.name == "Rook"):
                                        return True
                                    elif (is_queen_movement and check_piece.name == "Queen"):
                                        return True
                                    elif (is_king_movement and check_piece.name == "King"):
                                        return True
                                    elif (is_pawn_movement and check_piece.name == "Pawn"):
                                        return True
                                    
                                has_los = False
                        else: # if the test position is out of bounds line of sight is certainly broken
                            has_los = False

                        magnitude += 1
        # this second loop checks for enemy knights
        signs = [-2, -1, 1, 2]
        for x_sign in signs:
            for y_sign in signs:
                if (abs(x_sign * y_sign) == 2):
                    test_row = self.row + y_sign
                    test_col = self.col + x_sign
                    check_piece = board.get_piece_at(test_row, test_col)
                    if (check_piece != None and check_piece.team != self.team and check_piece.name == "Knight"):
                        return True

        return False
