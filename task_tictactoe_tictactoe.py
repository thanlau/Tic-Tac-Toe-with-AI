# write your code here
import string
from random import randint
import sys


class TicTacToe:
    def __init__(self):
        self.board = [['_' for _ in range(3)] for _ in range(3)]
        self.print_matrix(self.board)
        self.option = ['X','O']
        self.move_function =[self.get_player_move, self.get_computer_move]
        self.player = 0
        self.computer = 1
        self.turn = 0
        self.play_game()


    def print_matrix(self, matrix):
        print("---------")
        for i in range(3):
            print('|', *matrix[i], '|')
        print("---------")

    def get_cell(self, x, y):
        return self.board[x-1][y-1]

    def set_cell(self, x, y, value):
        self.board[x-1][y-1] = value

    def is_valid_move(self, x, y):
        return self.board[x-1][y-1] == '_'

    def get_player_move(self):
        while True:
            print("Enter the coordinates:")
            input_x, input_y = (int(x) for x in input().split(" "))
            if str(input_x) not in string.digits or str(input_y) not in string.digits:
                print("You should enter numbers!")
            elif input_x < 0 or input_x > 3 or input_y < 0 or input_y > 3:
                print("Coordinates should be from 1 to 3!")
            elif not self.is_valid_move(input_x, input_y):
                print("This cell is occupied! Choose another one!")
            else:
                return input_x, input_y

    def get_computer_move(self):
        print('Making move level "easy"')
        while True:
            coord_x, coord_y = randint(1,3), randint(1,3)
            if self.is_valid_move(coord_x, coord_y):
                return coord_x, coord_y

    def get_computer_move_medium(self):
        print('Making move level "medium"')
        if self.check_next_move():
            coord_x, coord_y = self.check_next_move()
            return coord_x, coord_y
        else:
            while True:
                coord_x, coord_y = randint(1,3), randint(1,3)
                if self.is_valid_move(coord_x, coord_y):
                    return coord_x, coord_y

    def get_computer_move_hard(self):
        print('Making move level "hard"')
        while True:
            m, coord_x, coord_y = self.max_value()
            if self.is_valid_move(coord_x, coord_y):
                return coord_x, coord_y

    def max_value(self):
        """
        -10: loss
        0 : tie
        10: win
        :return: score with x, y
        """
        maxv = -11 # initial wth -11 as worse than the worst case
        x = 1
        y = 1
        res = self.check_win(self.board)
        if res == 'X wins':
            return 10, 0, 0
        elif res == 'O wins':
            return -10, 0, 0
        elif res == 'Draw':
            return 0, 0, 0
        for i in range(1,4):
            for j in range(1,4):
                if self.is_valid_move(i, j):
                    self.set_cell(i, j, self.option[self.turn])
                    m, min_i, min_j = self.min_value()
                    if m > maxv:
                        maxv = m
                        x = i
                        y = j
                    self.set_cell(i, j, '_')
        return maxv, x, y

    def min_value(self):
        minv = 11
        x = -1
        y = -1
        res = self.check_win(self.board)
        if res == 'X wins':
            return 10, 0, 0
        elif res == 'O wins':
            return -10, 0, 0
        elif res == 'Draw':
            return 0, 0, 0
        for i in range(3):
            for j in range(3):
                if self.is_valid_move(x, y):
                    self.set_cell(x, y, self.option[self.turn])
                    m, min_i, min_j = self.max_value()
                    if m < minv:
                        minv = m
                        x = i
                        y = j
                    self.set_cell(x, y, '_')
        return minv, x, y


    def play_game(self):
        while True:
            usr1, usr2 = self.menu()
            self.set_difficulty(usr1, usr2)
            while True:
                move = self.move_function[self.turn]
                x, y = move()
                self.set_cell(x, y, self.option[self.turn])
                self.print_matrix(self.board)
                res = self.check_win(self.board)
                if res:
                    print(res)
                    break
                self.turn = 1 - self.turn

    def set_difficulty(self, usr1, usr2):
        if usr1 == 'easy' and usr2 =='easy':
            self.move_function = [self.get_computer_move, self.get_computer_move]
        elif usr1 == 'easy' and usr2 =='user':
            self.move_function = [self.get_computer_move, self.get_player_move]
        elif usr1 == 'user' and usr2 == 'user':
            self.move_function = [self.get_player_move, self.get_player_move]
        elif usr1 == 'medium' and usr2 =='medium':
            self.move_function = [self.get_computer_move_medium, self.get_computer_move_medium]
        elif usr1 == 'medium' and usr2 =='user':
            self.move_function = [self.get_computer_move_medium, self.get_player_move]
        elif usr1 == 'user' and usr2 == 'medium':
            self.move_function = [self.get_player_move, self.get_computer_move_medium]
        elif usr1 == 'hard' and usr2 =='hard':
            self.move_function = [self.get_computer_move_hard, self.get_computer_move_hard]
        elif usr1 == 'hard' and usr2 =='user':
            self.move_function = [self.get_computer_move_hard, self.get_player_move]
        elif usr1 == 'user' and usr2 == 'hard':
            self.move_function = [self.get_player_move, self.get_computer_move_hard]


    def menu(self):
        while True:
            print("Input command:")
            command = input().split()
            if command[0] == "exit":
                exit()
            elif len(command) != 3:
                print("Bad parameters!")
            elif command[0] != 'start':
                print("Bad parameters!")
            elif any(command[i] not in ['user','easy','medium','hard'] for i in range(1, 3)):
                print("Bad parameters!")
            else:
                return command[1], command[2]

    def check_next_move(self):
        for x in range(3):
            for y in range(3):
                if self.is_valid_move(x, y):
                    self.set_cell(x, y, self.option[self.turn])
                    res = self.check_win(self.board)
                    self.set_cell(x, y, '_')
                    if res:
                        return x,y
        return False


    def check_win(self,matrix):
        #check vertical and horizontal
        for i in range(3):
            if all(matrix[i][j] == 'X' for j in range(3)) or\
                all(matrix[j][i] == 'X' for j in range(3)):
                return "X wins"
            elif all(matrix[i][j] == 'O' for j in range(3)) or\
                all(matrix[j][i] == 'O' for j in range(3)):
                return "O wins"
        #check diagonal
        if all(matrix[i][i] == 'X' for i in range(3)) or \
            all(matrix[i][-(i+1)] == 'X' for i in range(3)):
            return "X wins"
        elif all(matrix[i][i] == 'O' for i in range(3)) or \
            all(matrix[i][-(i+1)] == 'O' for i in range(3)):
            return "O wins"
        if any(matrix[i][j] == '_' for i in range(3) for j in range(3)):
            return False
        else:
            return 'Draw'

TicTacToe()

