from BoardState import Board

class Game:
    def __init__(self):
        self.board = Board()
        self.undo_info_history = []
        self.times_at_board = {}
        self.board_id = self.board.get_board_hash()
        self.times_at_board[self.board_id] = 1

    def do_str_move(self, str_move):
        undo_info = self.board.do_str_move(str_move)
        if (undo_info != None):
            self.undo_info_history.append(undo_info)

            board_id = self.board.get_board_hash()
            self.board_id = board_id
            if (board_id in self.times_at_board):
                self.times_at_board[board_id] = self.times_at_board[board_id] + 1
                # print('duplicate board')
            else:
                self.times_at_board[board_id] = 1
            
            #game_status = self.is_game_over()
            return True
        return False

    def do_move(self, move):
        undo_info = self.board.do_move(move)
        if (undo_info != None):
            self.undo_info_history.append(undo_info)

            board_id = self.board.get_board_hash()
            self.board_id = board_id
            if (board_id in self.times_at_board):
                self.times_at_board[board_id] = self.times_at_board[board_id] + 1
                # print('duplicate board')
            else:
                self.times_at_board[board_id] = 1
            
            #game_status = self.is_game_over()
            return True
        return False

    def get_legal_moves(self):
        return self.board.get_moves_from_state()

    def get_team_to_move(self):
        return self.board.team_to_move

    def undo_move(self):
        if (len(self.undo_info_history) > 0):
            undo_info = self.undo_info_history.pop()
            
            if (not self.board_id in self.times_at_board):
                print('got tripped up when undoing')
            self.times_at_board[self.board_id] = self.times_at_board[self.board_id] - 1
            if (self.times_at_board[self.board_id] == 0):
                del self.times_at_board[self.board_id]
            
            self.board.undo_move(undo_info[0], undo_info[1], undo_info[2], undo_info[3])
            board_id = self.board.get_board_hash()
            self.board_id = board_id
        else:
            print('cannot undo past starting board')

    def get_board_hash(self):
        return self.board_id

    def get_nnet_inputs(self):
        base = self.board.nnet_inputs()
        #base.append(self.times_at_board[self.board_id]) # the board doesn't store this information so it needs to be added on
        return base

    def is_game_over(self):

        # insufficient material list:
        # king vs king
        # king and bishop vs king
        # king and knight vs king
        # king and bishop vs king and same color bishop
        insufficient_material = True
        bishop_counts = [0, 0]
        bishop_colors = [False, False]
        knight_count = 0
        
        for piece in self.board.pieces:
            if (insufficient_material and piece.alive):
                if (piece.name != "Bishop" and piece.name != "Knight"):
                    insufficient_material = False
                elif (piece.name == "Bishop"):
                    bishop_color = ((piece.row + piece.col) % 2 == 0)
                    if (piece.team):
                        bishop_counts[0] = bishop_counts[0] + 1
                        if (bishop_counts[0] > 1):
                            insufficient_material = False
                        else:
                            bishop_colors[0] = bishop_color
                    else:
                        bishop_counts[1] = bishop_counts[1] + 1
                        if (bishop_counts[1] > 1):
                            insufficient_material = False
                        else:
                            bishop_colors[1] = bishop_color
                elif (piece.name == "Knight"):
                    knight_count += 1
                    if (knight_count > 1):
                        insufficient_material = False
                        
        if (insufficient_material):
            if (knight_count > 0 and (bishop_counts[0] + bishop_counts[1] > 0)):
                insufficient_material = False
            elif (bishop_counts[0] == 1 and bishop_counts[1] == 1):
                if (bishop_colors[0] != bishop_colors[1]):
                    insufficient_material = False

        if (insufficient_material):
            print('Draw by insufficient material')
            return 0 # draw by insufficient material

        # threefold repetition
        if self.board_id not in self.times_at_board:
            print(self.board_id)
            print(self.times_at_board)

        if (not self.board_id in self.times_at_board):
                print('got tripped up when checking for 3fold repetition')
        if (self.times_at_board[self.board_id] == 3):
            print('Draw by threefold repetition')
            return 0 # draw by threefold repetition

        
        # 50 moves without capturing or moving any pawns
        if (self.board.moves_since_advancement >= 100): # 100 because the board is counting plys, or half-moves
            print('Draw due to 50 moves without advancement')
            return 0 # draw by the 50 move rule
            
        
        move_list = self.board.get_moves_from_state()
        if (len(move_list) == 0):
            if (self.board.team_in_check(self.board.team_to_move)):
                print('Checkmate')
                return 1 # checkmate
            else:
                print('Stalemate')
                return 0 # stalemate
        else:
            return -1 # game still going

    def get_pieces(self):
        pieces = []
        for piece in self.board.pieces:
            if (piece.alive):
                pieces.append(piece)
        for king in self.board.kings:
            if (king.alive):
                pieces.append(king)
        return pieces

    def is_square_friendly(self, row, col):
        piece_on_square = self.board.get_piece_at(row, col)
        if (piece_on_square != None):
            return piece_on_square.team == self.board.team_to_move
        return False

    def legal_moves_from_square(self, row, col):
        legal_move_positions = []
        for move in self.board.get_moves_from_state():
            if (move.start_row == row and move.start_col == col):
                end_pos = (move.end_row, move.end_col)
                legal_move_positions.append(end_pos)
        return legal_move_positions

    
