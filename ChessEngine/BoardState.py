import numpy as np
import secrets
import Pieces


# set up the zobrist hashing
def random_num():
    return secrets.randbits(32)

zobrist_keys = []
for i in range(781):
    zobrist_keys.append(random_num())

# Index meanings of zobrist keys
# 0 is the hash for who is moving
# 1 is for if white can queenside castle, 2 is if white can kingside castle
# 3 is for if black can queenside castle, 4 is if black can queenside castle
# 5 through 12 inclusive are for the column in which en passant is available, if applicable
# 13 through 780 inclusive are for each piece at each square (12 distinct pieces * 64 squares = 768)



class Board:
    def __init__(self):
        self.pieces = []
        self.kings = [] # kings are stored apart from the other pieces
                        # so we can easily test if they are in check
                        # index 0: white king
                        # index 1: black king
        # chess boards are 8 by 8
        self.num_rows = 8
        self.num_cols = 8
        self.en_passant_col = -1

        self.team_to_move = True

        self.moves_since_advancement = 0 # used to determine if the game is drawn'
        self.total_moves = 0

        self.reset_board()

    def reset_board(self):
        main_rows = [0, 7]
        pawn_rows = [1, 6]
        teams = [True, False]

        piece_id_counter = 0
        
        for i in range(len(teams)):
            main_row = main_rows[i]
            pawn_row = pawn_rows[i]
            team = teams[i]

            self.pieces.append(Pieces.Rook(main_row, 0, team, piece_id_counter))
            piece_id_counter += 1
            self.pieces.append(Pieces.Knight(main_row, 1, team, piece_id_counter))
            piece_id_counter += 1
            self.pieces.append(Pieces.Bishop(main_row, 2, team, piece_id_counter))
            piece_id_counter += 1
            self.pieces.append(Pieces.Queen(main_row, 3, team, piece_id_counter))
            piece_id_counter += 1
            self.kings.append(Pieces.King(main_row, 4, team, piece_id_counter))
            piece_id_counter += 1
            self.pieces.append(Pieces.Bishop(main_row, 5, team, piece_id_counter))
            piece_id_counter += 1
            self.pieces.append(Pieces.Knight(main_row, 6, team, piece_id_counter))
            piece_id_counter += 1
            self.pieces.append(Pieces.Rook(main_row, 7, team, piece_id_counter))
            piece_id_counter += 1

            for col in range(8):
                self.pieces.append(Pieces.Pawn(pawn_row, col, team, piece_id_counter))
                piece_id_counter += 1
            
        for piece in self.pieces:
            piece = piece.gen_moves(self, None)
        for king in self.kings:
            king = king.gen_moves(self, None)

        self.gen_legal_moves()

    def nnet_inputs(self):
        inputs = []
        
        player_pawns = np.zeros([8,8], np.dtype(bool))
        player_rooks = np.zeros([8,8], np.dtype(bool))
        player_bishops = np.zeros([8,8], np.dtype(bool))
        player_knights = np.zeros([8,8], np.dtype(bool))
        player_queens = np.zeros([8,8], np.dtype(bool))
        player_kings = np.zeros([8,8], np.dtype(bool))
        enemy_pawns = np.zeros([8,8], np.dtype(bool))
        enemy_rooks = np.zeros([8,8], np.dtype(bool))
        enemy_bishops = np.zeros([8,8], np.dtype(bool))
        enemy_knights = np.zeros([8,8], np.dtype(bool))
        enemy_queens = np.zeros([8,8], np.dtype(bool))
        enemy_kings = np.zeros([8,8], np.dtype(bool))
        player_color = self.team_to_move
        total_moves = self.total_moves
        moves_since_advancement = self.moves_since_advancement

        player_castling = self.get_castling_rights(player_color)
        enemy_castling = self.get_castling_rights(not player_color)

        all_pieces = []
        for piece in self.pieces:
            if (piece.alive):
                all_pieces.append(piece)
        for king in self.kings:
            if (king.alive):
                all_pieces.append(king)
        
        for piece in all_pieces:
            if (player_color):
                row = piece.row
                col = piece.col
            else:
                row = 7 - piece.row # the board needs to be input oriented according to the player moving
                col = piece.col
            if (piece.name == "Pawn"):
                if (piece.team == player_color):
                    player_pawns[row][col] = True
                else:
                    enemy_pawns[row][col] = True
            elif (piece.name == "Rook"):
                if (piece.team == player_color):
                    player_rooks[row][col] = True
                else:
                    enemy_rooks[row][col] = True
            elif (piece.name == "Bishop"):
                if (piece.team == player_color):
                    player_bishops[row][col] = True
                else:
                    enemy_bishops[row][col] = True
            elif (piece.name == "Knight"):
                if (piece.team == player_color):
                    player_knights[row][col] = True
                else:
                    enemy_knights[row][col] = True
            elif (piece.name == "Queen"):
                if (piece.team == player_color):
                    player_queens[row][col] = True
                else:
                    enemy_queens[row][col] = True
            elif (piece.name == "King"):
                if (piece.team == player_color):
                    player_kings[row][col] = True
                else:
                    enemy_kings[row][col] = True
        
        inputs.append(player_pawns)
        inputs.append(player_rooks)
        inputs.append(player_bishops)
        inputs.append(player_knights)
        inputs.append(player_queens)
        inputs.append(player_kings)
        inputs.append(enemy_pawns)
        inputs.append(enemy_rooks)
        inputs.append(enemy_bishops)
        inputs.append(enemy_knights)
        inputs.append(enemy_queens)
        inputs.append(enemy_kings)
        #inputs.append(player_color)
        #inputs.append(total_moves)
        #inputs.append(moves_since_advancement)
        #inputs.append(player_castling)
        #inputs.append(enemy_castling)

        return inputs
        

    def get_board_hash(self):
        ret_val = None
        for piece in self.pieces:
            if (piece.alive):
                index = self.get_piece_zobrist_index(piece)
                val = zobrist_keys[index]
                if (ret_val == None):
                    ret_val = val
                else:
                    ret_val = ret_val ^ val
        for piece in self.kings:
            if (piece.alive):
                index = self.get_piece_zobrist_index(piece)
                val = zobrist_keys[index]
                if (ret_val == None):
                    ret_val = val
                else:
                    ret_val = ret_val ^ val

        if (not self.team_to_move):
            ret_val = ret_val ^ zobrist_keys[0]
            
        white_castling = self.get_castling_rights(True)
        black_castling = self.get_castling_rights(False)
        
        if (self.en_passant_col != -1):
            ret_val = ret_val ^ zobrist_keys[5 + self.en_passant_col]

        if (white_castling[0]):
            ret_val = ret_val ^ zobrist_keys[1]
        if (white_castling[1]):
            ret_val = ret_val ^ zobrist_keys[2]
        if (black_castling[0]):
            ret_val = ret_val ^ zobrist_keys[3]
        if (black_castling[1]):
            ret_val = ret_val ^ zobrist_keys[4]
            
        return ret_val

    def get_piece_zobrist_index(self, piece):
        if (piece.name == "Pawn"):
            index = 0
        elif (piece.name == "Knight"):
            index = 1
        elif (piece.name == "Bishop"):
            index = 2
        elif (piece.name == "Rook"):
            index = 3
        elif (piece.name == "Queen"):
            index = 4
        elif (piece.name == "King"):
            index = 5
        index *= 64
        if (not piece.team):
            index += 384 # 6 x 64, 6 pieces, 64 squares
        index += ((piece.row * 8) + piece.col)
        return index
        

    def get_piece_at(self, row, col):
        ret_piece = None # if it doesn't find a piece at the position it returns None
        for piece in self.pieces:
            if (piece.alive and piece.row == row and piece.col == col):
                return piece
        for king in self.kings:
            if (king.alive and king.row == row and king.col == col):
                return king
        
        return ret_piece

    def kill_piece_at(self, row, col):
        for piece in self.pieces:
            if (piece.alive and piece.row == row and piece.col == col):
                piece.alive = False
                return True
        for king in self.kings:
            if (king.alive and king.row == row and king.col == col):
                king.alive = False # this probably shouldn't be happening
                return True

        print('failed to kill piece')
        return False

    def revive_piece_at(self, row, col, team, piece_id): # this is more of a revival than an addition
        for piece in self.pieces:
            if (not piece.alive and piece.row == row and piece.col == col and piece.piece_id == piece_id):
                piece.alive = True
                piece.dependent_on_square[row][col] = True
                return True
        for king in self.kings:
            if (not king.alive and king.row == row and king.col == col and king.piece_id == piece_id):
                king.alive = False # this probably shouldn't be happening
                king.dependent_on_square[row][col] = True
                return True
        print('failed to revive piece with id ' + str(piece_id) + ' at row' + str(row) + ' col ' + str(col))
        print(len(self.pieces))
        
        for piece in self.pieces:
            if (not piece.alive):
                print(str(piece) + ' with id ' + str(piece.piece_id) + ' at row ' + str(piece.row) + ' col ' + str(piece.col))
        
        return False

    def swap_piece(self, piece_id, row, col, team, new_name): # used for promotion and undoing promotion
        if (new_name == "Queen"):
            new_piece = Pieces.Queen(row, col, team, piece_id)
        elif (new_name == "Knight"):
            new_piece = Pieces.Knight(row, col, team, piece_id)
        elif (new_name == "Rook"):
            new_piece = Pieces.Rook(row, col, team, piece_id)
        elif (new_name == "Bishop"):
            new_piece = Pieces.Bishop(row, col, team, piece_id)
        elif (new_name == "Pawn"):
            new_piece = Pieces.Pawn(row, col, team, piece_id)
        else:
            print('error')
            
        for i in range(len(self.pieces)):
            piece = self.pieces[i]
            if (piece.piece_id == piece_id):
                self.pieces[i] = new_piece
                self.pieces[i].gen_moves(self, None)
                return True
        return False

    def __str__(self):
        board_representation = np.empty([8,8], dtype=object)

        for piece in self.pieces:
            board_representation[piece.row][piece.col] = str(piece)
        for king in self.kings:
            board_representation[king.row][king.col] = str(king)
            
        return str(board_representation)

    def do_str_move(self, str_move):
        moves = self.get_moves_from_state()
        for move in moves:
            if (str_move == str(move)):
                castling_rights = self.get_castling_rights(self.team_to_move)
                ep_col = self.en_passant_col
                moves_since_advancement = self.moves_since_advancement
                self.do_move(move)
                return move, ep_col, castling_rights, moves_since_advancement
        # print('invalid move') happens too frequently with the GUI to be uncommented
        return None

    def get_moves_from_state(self):
        return self.legal_moves

    def gen_legal_moves(self):
        moves = []
        num_checked = 0
        for piece in self.pieces:
            if (piece.alive and piece.team == self.team_to_move):
                for move in piece.possible_moves:
                    ep_col = self.en_passant_col
                    castling_rights = self.get_castling_rights(self.team_to_move)
                    team = self.team_to_move
                    self.do_move(move, is_test = True)
                    if (not self.team_in_check(team)): # moves are only legal if they do not put your king in check
                        moves.append(move)
                    self.undo_move(move, ep_col, castling_rights, 0, is_test = True)
                    num_checked += 1
        for king in self.kings:
            if (king.alive and king.team == self.team_to_move):
                for move in king.possible_moves:
                    ep_col = self.en_passant_col
                    castling_rights = self.get_castling_rights(self.team_to_move)
                    team = self.team_to_move
                    self.do_move(move, is_test = True)
                    if (not self.team_in_check(team)): # moves are only legal if they do not put your king in check
                        moves.append(move)
                    self.undo_move(move, ep_col, castling_rights, 0, is_test = True)
                    num_checked += 1
                
        self.legal_moves = moves

    def team_in_check(self, team):
        if (team):
            return self.kings[0].is_in_check(self)
        else:
            return self.kings[1].is_in_check(self)

    def get_castling_rights(self, team):
        if (team):
            return (self.kings[0].can_castle_queenside, self.kings[0].can_castle_kingside)
        else:
            return (self.kings[1].can_castle_queenside, self.kings[1].can_castle_kingside)

    def do_move(self, move, is_test = False): # it is a test if the move is only being performed to see if it would lead to the king being in check, and therefore shouldn't update moves
        # remove the piece that was captured if applicable
        castling_rights = self.get_castling_rights(self.team_to_move)
        ep_col = self.en_passant_col
        moves_since_advancement = self.moves_since_advancement
        
        
        if (move.is_capture):
            if (move.is_ep): # with en passant, the piece that is captured is not on the tile that is moved to
                capture_row = move.start_row # instead, the captured piece is on the same row as the pawn
                capture_col = move.end_col
            else:
                capture_row = move.end_row
                capture_col = move.end_col
            self.kill_piece_at(capture_row, capture_col)

        # update en passant information
        self.en_passant_col = -1 # en passant capture is only available for one ply
        if (move.piece_name == "Pawn" and abs(move.start_row - move.end_row) == 2):
            self.en_passant_col = move.start_col
            #if (not is_test):
                #print('en peasant')
        

        if (move.is_qs_castle or move.is_ks_castle): # king will be moved later during move generation
            if (move.is_qs_castle):
                self.get_piece_at(move.start_row, 0).col = (move.end_col + 1) # rook ends to the right of the king
            else: # means it is a kingside castle
                self.get_piece_at(move.start_row, 7).col = (move.end_col - 1) # rook ends to the left of the king
        # the rook should be dependent on both the starting and end squares of the castling move if it is valid

        # have to update the piece that moves before all of the others because it's new position needs to be known
        move_piece = self.get_piece_at(move.start_row, move.start_col)
        if (move.is_promotion):
            self.swap_piece(move_piece.piece_id, move.end_row, move.end_col, move_piece.team, move.piece_name)
        else:
            move_piece.gen_moves(self, move)
        
        if (not is_test):
            for piece in self.pieces:
                if (piece.alive and piece != move_piece and piece.dependent_on_move(move)):
                    piece.gen_moves(self, move)
            for king in self.kings:
                if (king.alive and king != move_piece and king.dependent_on_move(move)):
                    king.gen_moves(self, move)
                
        # swaps the team to move
        self.team_to_move = not self.team_to_move

        if (not is_test):
            self.total_moves += 1
            # updates information for the 50 move rule
            if (not(move.is_capture or move_piece.name == "Pawn")):
                self.moves_since_advancement += 1
            else:
                self.moves_since_advancement = 0

            # finally, generates the legal moves for the next player
            self.gen_legal_moves()

        return move, ep_col, castling_rights, moves_since_advancement

    def undo_move(self, move, ep_col, castling_rights, moves_since_advancement, is_test = False): # this information needs to be stored somewhere, because
                                                        # it is impossible to know with certainty how these values change
                                                        # on an undone move
        # starts by fixing the team to move
        self.team_to_move = not self.team_to_move


        # adjusts the 50 move rule to where it should be
        if (not is_test):
            self.total_moves -= 1
            self.moves_since_advancement = moves_since_advancement
        
        # update en passant information
        self.en_passant_col = ep_col
        #if (ep_col != -1):
            #print('restored en passant col to ' + str(ep_col))

        # undoes castling
        if (move.is_qs_castle or move.is_ks_castle): # king will be moved later during move generation
            if (move.is_qs_castle):
                self.get_piece_at(move.start_row, move.end_col + 1).col = 0 # rook ends up on the far left
            else: # means it is a kingside castle
                self.get_piece_at(move.start_row, move.end_col - 1).col = 7 # rook ends up on the far right
        # the rook should be dependent on both the starting and end squares of the castling move if it is valid

        # updates castling rights for the correct king
        if (self.team_to_move):
            self.kings[0].can_castle_queenside = castling_rights[0]
            self.kings[0].can_castle_kingside = castling_rights[1]
        else:
            self.kings[1].can_castle_queenside = castling_rights[0]
            self.kings[1].can_castle_kingside = castling_rights[1]

        
        # first needs to figure out the piece that moved there
        move_piece = self.get_piece_at(move.end_row, move.end_col)
        if (move_piece == None):
            print('cant find piece that moved')
        # then adds back the piece that was captured if applicable (must be done later because the added piece generates moves)
        if (move.is_capture):
            if (move.is_ep): # with en passant, the piece that is captured is not on the tile that is moved to
                capture_row = move.start_row # instead, the captured piece is on the same row as the pawn
                capture_col = move.end_col
            else:
                capture_row = move.end_row
                capture_col = move.end_col
            self.revive_piece_at(capture_row, capture_col, not self.team_to_move, move.capture_id)

        # needs to move back the piece that moved
        if (move.is_promotion):
            self.swap_piece(move_piece.piece_id, move.start_row, move.start_col, move_piece.team, "Pawn")
        else:
            move_piece.gen_moves(self, move, True)
        
        for piece in self.pieces:
            if (piece.alive and piece != move_piece and piece.dependent_on_move(move)):
                piece.gen_moves(self, move, True)
        for king in self.kings:
            if (king.alive and king != move_piece and king.dependent_on_move(move)):
                king.gen_moves(self, move, True)

        if (not is_test):
            self.gen_legal_moves()
            

            
