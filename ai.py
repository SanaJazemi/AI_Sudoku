import json
import numpy as np
from random import shuffle, random, sample, randint
from copy import deepcopy
from math import exp

class AI:

    def __init__(self, data=None, original_entries=None):
        if data is None:
            self.data = np.array([8,0,2,0,0,3,5,1,0,
                                0,6,0,0,9,1,0,0,3,
                                7,0,1,0,0,0,8,9,4,
                                6,0,8,0,0,4,0,2,1,
                                0,0,0,2,5,8,0,6,0,
                                9,2,0,3,1,0,4,0,0,
                                0,0,0,4,0,2,7,8,0,
                                0,0,5,0,8,9,0,0,0,
                                2,0,0,0,0,7,1,0,0])
        else:
            self.data = data
    
        if original_entries is None:
            self.original_entries = np.arange(81)[self.data > 0]
        else:
            self.original_entries = original_entries

    def fill_zeroes_randomely(self):
        for block_num in range(9):
            block_indices = self.get_block_indices(block_num)
            block = self.data[block_indices]
            zero_indices = [ind for i,ind in enumerate(block_indices) if block[i] == 0]
            available_values = [i for i in range(1,10) if i not in block]
            shuffle(available_values)
            for ind, random_value in zip(zero_indices, available_values):
                self.data[ind] = random_value
            
    def get_block_indices(self, k, ignore_originals=False):
        #Get data indices for kth block of puzzle.
        row_offset = (k // 3) * 3
        col_offset = (k % 3)  * 3
        indices = [col_offset + (j%3) + 9*(row_offset + (j//3)) for j in range(9)]
        if ignore_originals:
            indices = list(filter(lambda x:x not in self.original_entries, indices))
        return indices
        
    def get_column_indices(self, i):
        indices = [i + 9 * j for j in range(9)]
        return indices
        
    def get_row_indices(self, i):
        indices = [j + 9*i for j in range(9)]
        return indices
        
    def sudoku_json(self):
        def notzero(s):
            if s < 0 or s > 0: return str(s)
            if s == 0: return "0"
        
        results = np.array([self.data[self.get_row_indices(j)] for j in range(9)])
        out_s = ""
        out_s += '{\n'
        for i, row in enumerate(results):
            if i==0 or i==9: 
                out_s += '"sudoku":['+'\n'
            out_s += '      ['
            if i==8:
                out_s += ", ".join([",".join(notzero(s) for s in list(row)[3*(k-1):3*k]) for k in range(1,4)]) + "]\n"
            else:
                out_s += ", ".join([",".join(notzero(s) for s in list(row)[3*(k-1):3*k]) for k in range(1,4)]) + "],\n"
        out_s += '  ]\n'
        out_s += '}'
        print (out_s)
        
    def score_board(self):
        score = 0
        for row in range(9):
            score -= len(set(self.data[self.get_row_indices(row)]))
        for col in range(9):
            score -= len(set(self.data[self.get_column_indices(col)]))
        return score
        
    def make_candidate_data(self):
        new_data = deepcopy(self.data)
        block = randint(0,8)
        num_in_block = len(self.get_block_indices(block, ignore_originals=True))
        if num_in_block>1:
            random_squares = sample(range(num_in_block),2)
            square1, square2 = [self.get_block_indices(block, ignore_originals=True)[ind] for ind in random_squares]
            new_data[square1], new_data[square2] = new_data[square2], new_data[square1]
        return new_data


def solve(problem=None):

    SP = AI(problem)
    if problem is None:
        print("Default Puzzle:")
    else:
        print("Original Puzzle:")
    SP.sudoku_json()
    print("Calculating...")
    SP.fill_zeroes_randomely()
    best_SP = deepcopy(SP)
    current_score = SP.score_board()
    best_score = current_score
    T = .5
    count = 0

    while (count < 400000):
            candidate_data = SP.make_candidate_data()
            SP_candidate = AI(candidate_data, SP.original_entries)
            candidate_score = SP_candidate.score_board()
            delta_S = float(current_score - candidate_score)
            
            if exp(delta_S/T) - random() > 0:
                SP = SP_candidate
                current_score = candidate_score 
        
            if current_score < best_score:
                best_SP = deepcopy(SP)
                best_score = best_SP.score_board()
        
            if candidate_score == -162:
                SP = SP_candidate
                break
    
            T = .99999*T
            count += 1  
    if best_score == -162:
        print ("\nSOLVED THE PUZZLE.")
    else:
        print ("\nDIDN'T SOLVE. It's a random algorithm so Please try again.")
    print ("\nSolution:")
    SP.sudoku_json()

if __name__ == "__main__":
    print("Sudoko Puzzle Json File Location on Your device: (Press 0 button if you don't have one)")
    loc = input()
    if loc=="0":
        data = None
        solve(data)
    else:
        with open(loc) as file:
            file_content = file.read()
        read_file = json.loads(file_content)
        json_sudoku = read_file["sudoku"]
        problem = []
        for i in range (9):
            rows = json.dumps(json_sudoku[i])
            rows = eval(rows)
            problem = problem + rows
        sudoku = eval(str(problem))
        data = np.array(sudoku)
        solve(data)
