import random
from typing import Union
from copy import deepcopy

PLAYER_O = 'O'
PLAYER_X = 'X'
EMPTY_FIELD = '_'


class Coordinates:
    def __init__(self, row: int, column: int):
        self.row = row
        self.column = column

    def __str__(self):
        return f'({self.row},{self.column})'

    @staticmethod
    def create_from_string(string: str) -> 'Coordinates':
        def valid_raw_coordinates(raw_coordinates: str) -> None:
            try:
                words = list(map(int, raw_coordinates.split()))
            except ValueError:
                print("You should enter numbers!")
                raise NonInteger

            for word in words:
                number = int(word)
                if not 1 <= number <= 3:
                    print("Coordinates should be from 1 to 3!")
                    raise OutOfRange

        def transform_coordinates(raw_coordinates: str) -> list:
            column, row = list(map(int, raw_coordinates.split()))
            return [3 - row, column - 1]

        valid_raw_coordinates(string)

        return Coordinates(*transform_coordinates(string))


class Board:
    def __init__(self, string: str) -> None:
        self.matrix = [
            list(string[0:3]),
            list(string[3:6]),
            list(string[6:9])
        ]

    def __str__(self) -> str:
        def generate_row(row):
            return " ".join(row)

        line1 = generate_row(self.matrix[0])
        line2 = generate_row(self.matrix[1])
        line3 = generate_row(self.matrix[2])

        if not self.win(PLAYER_O) and not self.win(PLAYER_X):
            line1 = line1.replace(EMPTY_FIELD, ' ')
            line2 = line2.replace(EMPTY_FIELD, ' ')
            line3 = line3.replace(EMPTY_FIELD, ' ')

        return """
        ---------
        | {0} |
        | {1} |
        | {2} |
        ---------
        """.format(line1, line2, line3)

    def win(self, player) -> bool:
        return self.is_horizontal_line(player) or \
               self.is_vertical_line(player) or \
               self.is_diagonal_line(player)

    def is_horizontal_line(self, player) -> bool:
        for row in self.matrix:
            if self.is_three_in_line(row, player):
                return True
        return False

    def is_vertical_line(self, player) -> bool:
        for column in range(3):
            column = [self.matrix[0][column], self.matrix[1][column], self.matrix[2][column]]
            if self.is_three_in_line(column, player):
                return True
        return False

    def is_diagonal_line(self, player) -> bool:
        length = len(self.matrix)
        diagonal_left_to_right = []
        diagonal_right_to_left = []

        for value in range(length):
            diagonal_left_to_right.append(self.matrix[value][value])
            diagonal_right_to_left.append(self.matrix[value][2 - value])

        return self.is_three_in_line(diagonal_left_to_right, player) or \
            self.is_three_in_line(diagonal_right_to_left, player)

    @staticmethod
    def is_three_in_line(group, player) -> bool:
        unique_elements = set(group)
        return len(unique_elements) == 1 and player in unique_elements

    def has_moves(self) -> bool:
        elements = set([value for group in self.matrix for value in group])
        return EMPTY_FIELD in elements

    def count_player_moves(self, element) -> int:
        return len([value for group in self.matrix for value in group if value == element])

    def play_move(self, coordinates: Coordinates, player: str) -> None:
        if self.is_occupied(coordinates):
            print("This cell is occupied! Choose another one!")
            raise OccupiedField

        self.set_value(coordinates, player)

    def is_occupied(self, coordinates: Coordinates) -> bool:
        return self.get_value(coordinates) != EMPTY_FIELD

    def get_value(self, coordinates: Coordinates) -> str:
        return self.matrix[coordinates.row][coordinates.column]

    def set_value(self, coordinates: Coordinates, player: str) -> None:
        self.matrix[coordinates.row][coordinates.column] = player


class AI:
    def __init__(self, level: str, player: str) -> None:
        self.level = level
        self.player = player

    def get_coordinates(self, board: Board) -> Coordinates:
        pass

    def message_calculating_move(self) -> None:
        print(f'Making move level "{self.level}"')

    def random_move(self, board: Board) -> Coordinates:
        options = self.available_moves(board)
        return random.choice(options)

    @staticmethod
    def available_moves(board: Board) -> list:
        options = []
        for row in range(3):
            for column in range(3):
                coordinates = Coordinates(row, column)
                if not board.is_occupied(coordinates):
                    options.append(coordinates)

        return options

    @staticmethod
    def opposite_player(player: str) -> str:
        if player == PLAYER_O:
            return PLAYER_X
        else:
            return PLAYER_O

    @staticmethod
    def find_two_in_row(matrix: list, player: str) -> Union[Coordinates, None]:
        for pos_row in range(3):
            row = matrix[pos_row]
            if row.count(player) == 2 and row.count(EMPTY_FIELD) == 1:
                return Coordinates(pos_row, row.index(EMPTY_FIELD))

        for pos_column in range(3):
            column = [matrix[0][pos_column], matrix[1][pos_column], matrix[2][pos_column]]
            if column.count(player) == 2 and column.count(EMPTY_FIELD) == 1:
                return Coordinates(column.index(EMPTY_FIELD), pos_column)

        first_diagonal = [matrix[0][0], matrix[1][1], matrix[2][2]]
        if first_diagonal.count(player) == 2 and first_diagonal.count(EMPTY_FIELD) == 1:
            position = first_diagonal.index(EMPTY_FIELD)
            return Coordinates(position, position)

        second_diagonal = [matrix[0][2], matrix[1][1], matrix[2][0]]
        if second_diagonal.count(player) == 2 and second_diagonal.count(EMPTY_FIELD) == 1:
            pos_row = second_diagonal.index(EMPTY_FIELD)
            pos_column = 2 - pos_row
            return Coordinates(pos_row, pos_column)

        return None


class EasyAI(AI):
    def __init__(self, player: str) -> None:
        super().__init__('easy', player)

    def get_coordinates(self, board) -> Coordinates:
        self.message_calculating_move()
        return self.random_move(board)


class MediumAI(AI):
    def __init__(self, player: str) -> None:
        super().__init__('medium', player)

    def get_coordinates(self, board) -> Coordinates:
        self.message_calculating_move()

        coordinates = self.find_two_in_row(board.matrix, self.player)
        if coordinates is not None:
            return coordinates

        opposite = self.opposite_player(self.player)
        coordinates = self.find_two_in_row(board.matrix, opposite)
        if coordinates is not None:
            return coordinates

        return self.random_move(board)


class HardAI(AI):
    def __init__(self, player: str) -> None:
        super().__init__('hard', player)

    def get_coordinates(self, board) -> Coordinates:
        self.message_calculating_move()

        coordinates = self.find_two_in_row(board.matrix, self.player)
        if coordinates is not None:
            return coordinates

        opposite = self.opposite_player(self.player)
        coordinates = self.find_two_in_row(board.matrix, opposite)
        if coordinates is not None:
            return coordinates

        moves = self.available_moves(board)
        if len(moves) == 9:
            return self.random_move(board)

        final_score, final_index = self.minimax(board, self.player, self.player, self.opposite_player(self.player))
        return moves[final_index]

    def minimax(self, cloned_board: Board, player: str, me: str, opposite: str) -> tuple:
        if not cloned_board.has_moves():
            if cloned_board.win(me):
                return 10, -1
            elif cloned_board.win(opposite):
                return -10, -1
            else:
                return 0, -1

        options = {}
        next_opponent = self.opposite_player(player)
        next_moves = self.available_moves(cloned_board)
        for index in range(len(next_moves)):
            another_board = deepcopy(cloned_board)
            another_board.play_move(next_moves[index], player)
            score, _ = self.minimax(another_board, next_opponent, me, opposite)
            options[score] = index

        if player == me:
            score = max(options.keys())
            index = options[score]
        else:
            score = min(options.keys())
            index = options[score]

        return score, index


class User(AI):
    def __init__(self, player: str) -> None:
        super().__init__('Human', player)

    def get_coordinates(self, board) -> Coordinates:
        raw_coordinates = input("Enter the coordinates: ")
        return Coordinates.create_from_string(raw_coordinates)


class Match:
    def __init__(self, player_x: AI, player_o: AI) -> None:
        self.player_x = player_x
        self.player_o = player_o

    def play(self) -> None:
        board = Board('_________')
        print(board)

        while not self.is_finished(board):

            self.play_move(board, self.player_x)

            print(board)

            if self.is_finished(board):
                break

            self.play_move(board, self.player_o)

            print(board)

        print(self.game_status(board))

    @staticmethod
    def play_move(board: Board, ai: AI) -> None:
        while True:
            try:
                coordinates = ai.get_coordinates(board)
                board.play_move(coordinates, ai.player)
            except MoveException:
                if isinstance(ai, User):
                    continue
                else:
                    raise RuntimeError
            else:
                break

    def game_status(self, board: Board) -> str:
        if not self.valid_game_state(board):
            return 'Impossible'
        elif board.win(PLAYER_O):
            return 'O wins'
        elif board.win(PLAYER_X):
            return 'X wins'
        elif not board.has_moves():
            return 'Draw'
        else:
            return 'Game not finished'

    def is_finished(self, board: Board) -> bool:
        return not self.valid_game_state(board) or \
               board.win(PLAYER_O) or \
               board.win(PLAYER_X) or \
               not board.has_moves()

    @staticmethod
    def valid_game_state(board: Board) -> bool:
        if board.win(PLAYER_O) and board.win(PLAYER_X):
            return False

        total_o = board.count_player_moves(PLAYER_O)
        total_x = board.count_player_moves(PLAYER_X)
        diff = abs(total_x - total_o)

        return total_o == total_x or diff == 1


class Command:
    def run(self) -> None:
        pass

    @staticmethod
    def create_from_string(option: str) -> 'Command':
        if option == 'exit':
            return Exit()

        if option.startswith('start'):
            return Start(option)

        raise UnknownCommand


class Start(Command):
    def __init__(self, option: str) -> None:
        def generate_ai(name: str, player: str) -> AI:
            if name == 'user':
                return User(player)

            if name == 'easy':
                return EasyAI(player)

            if name == 'medium':
                return MediumAI(player)

            if name == 'hard':
                return HardAI(player)

            raise UnknownAI

        option = option.split()
        self.player_x = generate_ai(option[1], PLAYER_X)
        self.player_o = generate_ai(option[2], PLAYER_O)

    def run(self) -> None:
        match = Match(self.player_x, self.player_o)
        match.play()


class Exit(Command):
    def run(self) -> None:
        raise Terminate


class Terminate(Exception):
    pass


class UnknownCommand(Exception):
    pass


class UnknownAI(Exception):
    pass


class MoveException(Exception):
    pass


class OccupiedField(MoveException):
    pass


class NonInteger(MoveException):
    pass


class OutOfRange(MoveException):
    pass


class Game:
    def run(self) -> None:
        while True:
            try:
                command = self.ask_command()
                command.run()
            except Terminate:
                break
            except (UnknownCommand, UnknownAI):
                print('Bad parameters!')

    @staticmethod
    def ask_command() -> Command:
        option = input('Input command: ')
        return Command.create_from_string(option)


game = Game()
game.run()
