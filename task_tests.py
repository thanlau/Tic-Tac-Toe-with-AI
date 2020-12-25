import random
from copy import deepcopy
from enum import Enum

from hstest.stage_test import *
from hstest.test_case import TestCase

CheckResult.correct = lambda: CheckResult(True, '')
CheckResult.wrong = lambda feedback: CheckResult(False, feedback)


class FieldState(Enum):
    X = 'X'
    O = 'O'
    FREE = ' '


def get_state(symbol):
    if symbol == 'X':
        return FieldState.X
    elif symbol == 'O':
        return FieldState.O
    elif symbol == ' ' or symbol == '_':
        return FieldState.FREE
    else:
        return None


def state2char(state):
    if state == FieldState.X:
        return "X"
    if state == FieldState.O:
        return "O"
    if state == FieldState.FREE:
        return "_"
    else:
        return None


class TicTacToeField:

    def __init__(self, *, field: str = '', constructed=None):

        if constructed is not None:
            self.field = deepcopy(constructed)

        else:
            self.field: List[List[Optional[FieldState]]] = [
                [None for _ in range(3)] for _ in range(3)
            ]

            field = field.replace("\"", "")

            for row in range(3):
                for col in range(3):
                    index = (2 - row) * 3 + col
                    self.field[row][col] = get_state(field[index])

    def equal_to(self, other) -> bool:
        for i in range(3):
            for j in range(3):
                if self.field[i][j] != other.field[i][j]:
                    return False
        return True

    def has_next_as(self, other) -> bool:
        improved: bool = False
        for i in range(3):
            for j in range(3):
                if self.field[i][j] != other.field[i][j]:
                    if self.field[i][j] == FieldState.FREE and not improved:
                        improved = True
                    else:
                        return False
        return improved

    def differ_by_one(self, other) -> bool:
        have_single_difference = False
        for i in range(3):
            for j in range(3):
                if self.field[i][j] != other.field[i][j]:
                    if have_single_difference:
                        return False
                    have_single_difference = True
        return have_single_difference

    def is_close_to(self, other) -> bool:
        return (
                self.equal_to(other)
                or self.has_next_as(other)
                or other.has_next_as(self)
        )

    @staticmethod
    def parse(field_str: str):

        lines = field_str.splitlines()
        lines = [i.strip() for i in lines]
        lines = [i for i in lines if
                 i.startswith('|') and i.endswith('|')]

        for line in lines:
            if len(line) != 9:
                raise WrongAnswerException(
                    f"Line of Tic-Tac-Toe field should be 9 characters long\n"
                    f"found {len(line)} characters in \"{line}\"")
            for c in line:
                if c not in 'XO|_ ':
                    return None

        field: List[List[Optional[FieldState]]] = [
            [None for _ in range(3)] for _ in range(3)
        ]

        y: int = 0

        for line in lines:
            cols = line[2], line[4], line[6]
            x: int = 0
            for c in cols:
                state = get_state(c)
                if state is None:
                    return None
                field[y][x] = state
                x += 1
            y += 1

        return TicTacToeField(constructed=field)

    @staticmethod
    def parse_all(output: str):
        fields = []

        lines = output.splitlines()
        lines = [i.strip() for i in lines]
        lines = [i for i in lines if len(i) > 0]

        candidate_field = ''
        inside_field = False
        for line in lines:
            if '----' in line and not inside_field:
                inside_field = True
                candidate_field = ''
            elif '----' in line and inside_field:
                field = TicTacToeField.parse(candidate_field)
                if field is not None:
                    fields += [field]
                inside_field = False

            if inside_field and line.startswith('|'):
                candidate_field += line + '\n'

        return fields


inputs = [
    "1 1", "1 2", "1 3",
    "2 1", "2 2", "2 3",
    "3 1", "3 2", "3 3"
]


def iterate_cells(initial: str) -> str:
    index: int = -1
    for i in range(len(inputs)):
        if initial == inputs[i]:
            index = i
            break

    if index == -1:
        return ''

    full_input: str = ''
    for i in range(index, index + 9):
        full_input += inputs[i % len(inputs)] + '\n'

    return full_input


class TicTacToeTest(StageTest):
    win = 0
    draw = 0
    turn = 0
    manual_test_turns = [None, [0, 0], [1, 2], [1, 0], [2, 2], [2, 0]]

    def generate(self) -> List[TestCase]:
        return [TestCase(stdin=(["start easy easy", "2 2"] + [self.test for _ in range(50)] + ["exit"]),
                         check_function=self.check_1) for _ in range(50)] + \
               [TestCase(stdin="exit", check_function=self.final_check_easy)] + \
               [TestCase(stdin="start easy easy\nexit", check_function=self.auto_test_check),
                TestCase(stdin=["start user user", self.manual_test_1, self.manual_test_1, self.manual_test_1,
                                self.manual_test_1, self.manual_test_1, self.manual_test_1_check]),
                TestCase(stdin=["start user user", "1 1", self.manual_test_2_1, self.manual_test_2_2,
                                self.manual_test_2_3])] + \
               [TestCase(stdin=["start medium medium", "2 2"] + [self.test for _ in range(50)] + ["exit"],
                         check_function=self.check_1) for _ in range(50)] + \
               [TestCase(stdin="exit", check_function=self.final_check_medium)] + \
               [TestCase(stdin=["start hard hard", "2 2"] + [self.test for _ in range(50)] + ["exit"],
                         check_function=self.check_1) for _ in range(50)] + \
               [TestCase(stdin="exit", check_function=self.final_check_hard)] + \
               [TestCase(stdin=["start hard medium", "2 2"] + [self.test for _ in range(50)] + ["exit"],
                         check_function=self.check_1) for _ in range(50)] + \
               [TestCase(stdin="exit", check_function=self.final_check_hard_vs_medium)]

    # checking overlapping ###################################################
    def manual_test_2_1(self, output):
        tic_tac_toe_field: TicTacToeField = TicTacToeField.parse(output)
        if tic_tac_toe_field is None:
            return CheckResult.wrong("The game field is incorrect")
        if not str(tic_tac_toe_field.field[0][0]).lower() == "fieldstate.x":
            return CheckResult.wrong("The X was placed to a wrong position." +
                                     "The X symbol was not found (" +
                                     state2char(tic_tac_toe_field.field[0][0]) + " instead of it).")
        return "1 1"

    def manual_test_2_2(self, output):
        if len(output.split("\n")) > 3:
            return CheckResult.wrong("We placed a symbol to an occupied cell, but your program didn't warned about it.")
        return "1 2"

    def manual_test_2_3(self, output):
        tic_tac_toe_field: TicTacToeField = TicTacToeField.parse(output)
        if tic_tac_toe_field is None:
            return CheckResult.wrong("The game field is incorrect")
        if not state2char(tic_tac_toe_field.field[0][0]) == "X":
            return CheckResult.wrong("The \"O\" symbol overlapped the \"X\" one.")
        return CheckResult.correct()

    # manual testing of the game #############################################
    def manual_test_1(self, output):
        if self.manual_test_turns[self.turn] is None:
            self.turn += 1
            temp = self.manual_test_turns[self.turn]
            return str(temp[0] + 1) + " " + str(temp[1] + 1)

        fields: List[TicTacToeField] = TicTacToeField.parse_all(output)

        if len(fields) != 1:
            raise WrongAnswer("Cannot parse output. "
                              f"Expected 1 grid to be printed, found {len(fields)}")

        field = fields[0]

        a, b = self.manual_test_turns[self.turn]
        if self.turn % 2 == 1:
            mode = "x"
        else:
            mode = "o"

        if field is None:
            return CheckResult.wrong("The game field is incorrect")

        if not str(field.field[a][b]).lower() == "fieldstate." + mode:
            return CheckResult.wrong("The " + mode.upper() + " was placed to a wrong position." +
                                     "The " + mode.upper() + " symbol was not found (" +
                                     state2char(field.field[a][b]) + " instead of it).")

        self.turn += 1
        temp = self.manual_test_turns[self.turn]
        return str(temp[0] + 1) + " " + str(temp[1] + 1)

    def manual_test_1_check(self, output: str):
        if not "wins" in output.lower() or not "x" in output.lower():
            return CheckResult.wrong("A win message was expected, but the game didn't stop.")
        return CheckResult.correct()

    def check(self, reply, attach):
        return CheckResult.wrong('You finished the program too early, input request was expected')

    ##########################################################################

    # input util the finish
    def test(self, output):
        index = random.randint(0, len(inputs) - 1)
        return inputs[index]

    # winnings counters
    # easy
    def check_1(self, reply: str, attach):
        if "x wins" in reply.lower():
            self.win += 1
        elif "draw" in reply.lower():
            self.draw += 1
        return CheckResult.correct()

    # check the percentage of winnings
    def final_check_easy(self, reply, attach):
        if self.win > 13:
            self.win = 0
            self.draw = 0
            self.turn = 0
            return CheckResult.correct()
        else:
            return CheckResult.wrong("The difficulty of your easy AI is too high. " +
                                     "Make it easier.\n"
                                     "If you are sure the AI difficulty is fine, try to rerun the test.")

    def final_check_medium(self, reply, attach):
        if self.win > 10:
            self.win = 0
            self.draw = 0
            self.turn = 0
            return CheckResult.correct()
        else:
            return CheckResult.wrong("The difficulty of your medium AI is too high. " +
                                     "Make it easier.\n"
                                     "If you are sure the AI difficulty is fine, try to rerun the test.")

    def final_check_hard(self, reply, attach):
        if self.draw > 40:
            self.win = 0
            self.draw = 0
            self.turn = 0
            return CheckResult.correct()
        else:
            return CheckResult.wrong("The difficulty of your hard AI is too high." +
                                     "Make it easier.")

    def final_check_hard_vs_medium(self, reply, attach):
        if self.win > 12:
            self.win = 0
            self.draw = 0
            self.turn = 0
            return CheckResult.correct()
        else:
            return CheckResult.wrong("The difficulty of your hard AI is too low.")

    # checking if the game works correctly in ai vs ai mode
    def auto_test_check(self, reply: str, attach):
        if "wins" not in reply.lower() and "draw" not in reply.lower():
            return CheckResult.wrong("The game was not finished (your program did not print the result of the game).")

        fields = TicTacToeField.parse_all(reply)

        if len(fields) == 0:
            return CheckResult.wrong("No fields found")

        for i in range(1, len(fields)):
            curr: TicTacToeField = fields[i - 1]
            next: TicTacToeField = fields[i]

            if not (curr.equal_to(next) or curr.has_next_as(next)):
                return CheckResult.wrong("For two fields following each " +
                                         "other one is not a continuation " +
                                         "of the other (they differ more than in two places).")

        return CheckResult.correct()


if __name__ == '__main__':
    TicTacToeTest('tictactoe.tictactoe').run_tests()
