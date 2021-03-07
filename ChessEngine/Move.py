
# this class essentially serves as a data structure with some extra functionality

class Move:
    def __init__(self, start_row, start_col, end_row, end_col, piece_name, is_capture = False, capture_name = None, capture_id = -1, is_promotion = False, is_ep = False, is_qs_castle = False, is_ks_castle = False):
        self.start_row = start_row
        self.start_col = start_col
        self.end_row = end_row
        self.end_col = end_col
        self.piece_name = piece_name
        self.is_capture = is_capture
        self.capture_name = capture_name
        self.capture_id = capture_id
        self.is_promotion = is_promotion
        self.is_ep = is_ep
        self.is_qs_castle = is_qs_castle
        self.is_ks_castle = is_ks_castle


    def __str__(self):
        A = 97
        return (chr(self.start_col + A) + str(self.start_row + 1) + chr(self.end_col + A) + str(self.end_row + 1))

    def get_nnet_index(self, team):
        start_row = self.start_row
        start_col = self.start_col
        end_row = self.end_row
        end_col = self.end_col

        if (not team): # the moves, like the board need to be oriented all the same way for the nnet input
            start_row = 7 - start_row
            end_row = 7 - end_row
        
        if (not self.is_promotion):
            code = encode(start_row, start_col, end_row, end_col)
        else:
            direction = end_col - start_col
            code = encode(start_row, start_col, end_row, end_col, is_promotion = True, end_piece = self.piece_name, direction = direction)
            
        if (code == -1):
            print('Critical error: move encoding failed!')
        if code in nnet_ids:
            index = nnet_ids[code]
            return index
        else:
            print('Critical error: code ' + str(code) + ' not found for move ' + str(self))
            return -1
        


def encode(row_1, col_1, row_2, col_2, is_promotion = False, end_piece = "Queen", direction = 0):
    if ((0 <= row_1 <= 7) and (0 <= col_1 <= 7) and (0 <= row_2 <= 7) and (0 <= col_2 <= 7)):
        if (not is_promotion or end_piece == "Queen"):
            final_digit = 0
        else:
            if (end_piece == "Knight"):
                final_digit = 1
            elif (end_piece == "Bishop"):
                final_digit = 2
            elif (end_piece == "Rook"):
                final_digit = 3

            if (direction == -1):
                final_digit += 0
            elif (direction == 0):
                final_digit += 3
            else:
                final_digit += 6

        encoded_num = final_digit + (10 * col_2) + (100 * row_2) + (1000 * col_1) + (10000 * row_1)
        return encoded_num
    else:
        return -1
    

count = 0

nnet_ids = {}

directions = [-1, 0, 1]
under_promotions = ["Knight", "Bishop", "Rook"]
knight_directions = [-2, -1, 1, 2]


for row in range(8):
    for col in range(8):
        for y_dir in directions:
            for x_dir in directions:
                if (not(x_dir == 0 and y_dir == 0)):
                    for magnitude in range(7):
                        new_row = row + (y_dir * (magnitude + 1))
                        new_col = col + (x_dir * (magnitude + 1))
                        num = encode(row, col, new_row, new_col)
                        if (num != -1):
                            nnet_ids[num] = count
                        count += 1
        for y_dir in knight_directions:
            for x_dir in knight_directions:
                if (abs(y_dir * x_dir) == 2):
                    new_row = row + y_dir
                    new_col = col + x_dir
                    num = encode(row, col, new_row, new_col)
                    if (num != -1):
                        nnet_ids[num] = count
                    count += 1
        for x_dir in directions:
            for name in under_promotions:
                new_row = row + 1 # the board should be oriented for the player moving as far as the neural network is concerned
                new_col = col
                num = encode(row, col, new_row, new_col, is_promotion = True, end_piece = name, direction = x_dir)
                if (num != -1):
                    nnet_ids[num] = count
                count += 1
                    
#print(count)
#print(len(nnet_ids))
