import numpy as np
import graphics
from graphics import *
import time

class BasePlayer:

    def __init__(self):
        self.reset_metrics()

    def set_n(self,n):
        self.n = n

    def set_env(self, env):
        self.env = env

    def reset_metrics(self):
        self.wins = 0
        self.losses = 0
        self.ties = 0

    def record_outcome(self, game, outcome):
        if outcome == self.n:
            self.wins += 1
        elif outcome == -self.n:
            self.losses += 1
        else:
            self.ties += 1

    def reset(self):
        pass

    def update(self, game, state, reward, done):
        pass

    def __str__(self):
        return self.__class__.__name__ + ' w/l/t=' + str(self.wins) + '/' + str(self.losses) + '/' + str(self.ties)

class EmptyPlayer(BasePlayer):

    def __init__(self):
        super().__init__()

    def move(self, game, state):
        pass


class RandomPlayer(BasePlayer):

    def __init__(self):
        super().__init__()

    def move(self, game, state):
        return game.sample(legal=True)


class HumanPlayer(BasePlayer):

    def __init__(self):
        super().__init__()

    def move(self, game, state):
        print(game)
        return int(input())

    def record_outcome(self, game, outcome):
        print(game)
        if outcome == self.n:
            print('...YOU WIN!')
        elif outcome == -self.n:
            print('...YOU LOSE...')
        else:
            print('...TIE GAME...')

class PrettyGoodPlayer(BasePlayer):

    def __init__(self):
        super().__init__()

    def move(self, game, state):
        move = self.winning_move(game)
        if move != -1:
            return move
        move = self.block_opponent(game)
        if move != -1:
            return move
        return game.sample(legal=True)

    def winning_move(self, game):
        for row in range(3):
            for col in range(3):
                if game.board[row][col] == 0:
                    game.board[row][col] = self.n
                    max_min = game.max_min()
                    game.board[row][col] = 0
                    if max_min[0] == self.n * 3 or max_min[1] == self.n * 3:
                        return row * 3 + col
        return -1

    def block_opponent(self, game):
        for row in range(3):
            for col in range(3):
                if game.board[row][col] == 0:
                    game.board[row][col] = -self.n
                    max_min = game.max_min()
                    game.board[row][col] = 0
                    if max_min[0] == -self.n * 3 or max_min[1] == -self.n * 3:
                        return row * 3 + col
        return -1

class VeryGoodPlayer(PrettyGoodPlayer):
    def __init__(self):
        super().__init__()

    def move(self, game, state):
        move = self.winning_move(game)
        if move != -1:
            return move
        move = self.block_opponent(game)
        if move != -1:
            return move
        move = self.double_winner(game.board,self.n)
        if move != -1:
            return move
        move = self.double_winner(game.board,-self.n)
        if move != -1:
            return move
        return game.sample(legal=True)

    def double_winner(self, board, n):
        for row in range(3):
            for col in range(3):
                if board[row][col] == 0:
                    board[row][col] = n
                    w_col = [1 for x in np.sum(board,0) if x == n*2]
                    w_row = [1 for x in np.sum(board,1) if x == n*2]
                    winners = int(np.sum(w_col) + np.sum(w_row))
                    winners += (1 if board.trace(0) == n*2 else 0)
                    winners += 1 if np.flip(board,0).trace(0) == n*2 else 0
                    board[row][col] = 0
                    if winners > 1:
                        return row * 3 + col
        return -1

class MinimaxPlayer(BasePlayer):

    # return a valid move (0..9, equal to [row * 3 + col] )
    def move(self, game, state):
        best_row = -1
        best_col = -1
        best_score = -100
        for row in range(3):
            for col in range(3):
                if game.board[row][col] == 0:
                    game.board[row][col] = self.n
                    score = self.minimax(game,False)
                    game.board[row][col] = 0
                    if score > best_score:
                        best_score = score
                        best_row = row
                        best_col = col
        return best_row * 3 + best_col

    # check if the board is full (implying that the game is over)
    def board_is_full(self, board):
        for row in range(3):
            for col in range(3):
                if board[row][col] == 0:
                    return False
        return True

    # do the work first described by Jon Von Neumann in 1928
    def minimax(self, game, isMe):

        # first, check for terminal conditions...
        scores = game.max_min()
        if scores[0] == 3:
            return scores[0] * self.n       # 'x' wins...
        elif scores[1] == -3:
            return scores[1] * self.n       # 'o' wins...
        if self.board_is_full(game.board):
            return 0                        # ...and a tie is also a terminal condition.

        if isMe:
            best = -4
            for row in range(3):
                for col in range(3):
                    if game.board[row][col] == 0:
                        game.board[row][col] = self.n
                        best = max(best, self.minimax(game, not isMe))
                        game.board[row][col] = 0
        else:
            best = 4
            for row in range(3):
                for col in range(3):
                    if game.board[row][col] == 0:
                        game.board[row][col] = -self.n
                        best = min(best, self.minimax(game, not isMe))
                        game.board[row][col] = 0
        return best

class Game:
    def __init__(self, x_player=EmptyPlayer(), o_player=MinimaxPlayer(), animation=False):
        self.x_player = x_player
        self.o_player = o_player
        self.x_player.set_n(1)
        self.o_player.set_n(-1)
        self.x_player.set_env(self)
        self.o_player.set_env(self)
        self.i = 0
        self.animation = GameBoard() if animation else None
        self.reset()

    def reset(self, mode='reinforcement_learning'):
        self.board = np.zeros((3,3))
        self.x_turn = True
        self.x_player.reset()
        self.o_player.reset()
        self.moves = []
        self.states = []
        self.available = [0,1,2,3,4,5,6,7,8]
        if self.animation is not None:
            self.animation.clear()
        if mode == 'reinforcement_learning':
            return self.state(self.x_player, self.board)

    # used for reinforcement learning only... for normal game play, use move()
    def step(self, action):
        try:
            self.move(action, self.x_player)
            if self.x_wins():
                return self.state(self.x_player, self.board), 1, True
            elif len(self.available) > 0:
                action = self.o_player.move(self, self.state(self.o_player, self.board))
                outcome = self.move(action, self.o_player)
                if self.o_wins():
                    return self.state(self.x_player, self.board), -1, True
                else:
                    return self.state(self.x_player, self.board), 0, len(self.available) == 0
            else:
                return self.state(self.x_player, self.board), 0, True
        except ValueError:
            return self.state(self.x_player, self.board), -1, True

    def state_space():
        return 3**9

    def action_space():
        return 9

    def x_wins(self):
        return max(self.max_min()) == 3

    def o_wins(self):
        return min(self.max_min()) == -3

    # returns the max and min of sum of each axis + each diagonal
    def max_min(self):
        col_sum = np.sum(self.board,0)
        row_sum = np.sum(self.board,1)
        maxs = np.maximum(col_sum,row_sum)
        mins = np.minimum(col_sum,row_sum)
        diag0 = self.board.trace(0)
        diag1 = np.flip(self.board,0).trace(0)
        return max(max(maxs), diag0, diag1), min(min(mins), diag0, diag1)

    def move(self, action, player):
        n_player = 1 if player is self.x_player else -1
        row = action // 3
        col = action % 3
        if self.board[row][col] == 0:
            self.board[row][col] = n_player
            self.available.remove(action)
            self.moves.append((n_player,row,col))
            self.states.append(self.state(self.x_player, self.board)) # supports instant replay
            if self.animation is not None:
                if n_player == 1:
                    self.animation.x(row,col)
                    time.sleep(0.1)
                else:
                    self.animation.o(row,col)
                    time.sleep(0.1)
        else:
            raise ValueError("illegal move")
        x,o = self.max_min()
        return x == 3 or o == -3

    # return a random legal move (do not call if all 9 squares are taken!)
    def sample(self, legal=False):
        if legal:
            if len(self.available) == 0:
                raise ValueError('cannot sample randomly; board is full')
            else:
                return self.available[np.random.randint(len(self.available))]
        else:
            return np.random.randint(9)

    def sequential(self):
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == 0:
                    return row * 3 + col
        raise ValueError('cannot sample sequentially; board is full')

    def state(self, player, board):
        i = 0
        n = 1 if player is self.x_player else -1
        for row in range(3):
            for col in range(3):
                i += (n * board[row][col] + 1) * (3 ** (row*3+col))
        return int(i)

    def construct_board(state):
        board = np.zeros((3,3))
        for row in range(2,-1,-1):
            for col in range(2,-1,-1):
                exp = 3 ** (row*3+col)
                board[row][col] = state // exp - 1
                state = state % exp
        return board

    def play(self):
        self.reset()
        self.i+=1
        while len(self.available) > 0:
            player = self.x_player if self.x_turn else self.o_player
            opponent = self.x_player if not self.x_turn else self.o_player
            state = self.state(player, self.board)
            p_row_col = player.move(self,state)
            try:
                player_wins = self.move(p_row_col,player)
            except ValueError:
                player.update(self,state,-100, True)
                break
            if player_wins:
                player.update(self,state,1, True)
                opponent.update(self,state,-1, True)
                break
            else:
                opponent.update(self,state,0, False)
            self.x_turn = not self.x_turn
        if player_wins:
            self.x_player.record_outcome(self, player.n)
            self.o_player.record_outcome(self, player.n)
        else:
            self.x_player.record_outcome(self, 0)
            self.o_player.record_outcome(self, 0)

    def game_over(self):
        return np.max(np.absolute(self.max_min())) == 3 or self.i >= 9

    def replay(self):
        print('=== REPLAY =================================')
        print(self.states)
        i = 0
        for state in self.states:
            i += 1
            print('===( ' + str(i) + ' [ state=' + str(state) + ' ] )=====================\n')
            self.board = Game.construct_board(state)
            print(Game.draw(self.board))
            if (self.x_wins()):
                print('X wins!')
            if (self.o_wins()):
                print('O wins!')
        print('\n')

    def draw(board):
        s = ''
        for i in range(3):
            for line in range(3):
                for j in range(3):
                    if board[i][j] == 1:
                        if line == 0:
                            s += '\\ /'
                        elif line == 1:
                            s += ' X '
                        else:
                            s += '/ \\'
                    elif board[i][j] == -1:
                        if line == 0:
                            s += 'OOO'
                        elif line == 1:
                            s += 'O O'
                        else:
                            s += 'OOO'
                    else:
                        if line == 1:
                            s += ' ' + str(int(i*3+j)) + ' '
                        else:
                            s += '   '
                    s += '   '
                s += '\n'
            s += '\n'
        return s

    def __str__(self):
        s = '\n---( '
        s += str(9-len(self.available))
        s += ' )--------------------------\n\n'
        s += Game.draw(self.board)
        s += 'x state = '
        s += str(self.state(self.x_player, self.board))
        s += ', o state = '
        s += str(self.state(self.o_player, self.board))
        s += ' available: ' + str(self.available)
        return s

class GameBoard():
    def __init__(self):
        self.size = 90
        self.stroke = 5
        self.w = self.size * 5
        self.h = self.size * 5
        self.win = GraphWin("/rl/tic-tac-toe", self.w, self.h)
        self.clear()

    def line(self,xyxy):
        rect = Rectangle(Point(xyxy[0], xyxy[1]), Point(xyxy[2],xyxy[3]))
        rect.setFill('black')
        rect.draw(self.win)

    def clear(self):
        rect = Rectangle(Point(0,0), Point(self.w, self.h))
        rect.setFill('white')
        rect.draw(self.win)
        self.line([self.size * 2, self.size, self.size * 2 + self.stroke, self.size * 4])
        self.line([self.size * 3, self.size, self.size * 3 + self.stroke, self.size * 4])
        self.line([self.size, self.size * 2, self.size * 4, self.size * 2 + self.stroke])
        self.line([self.size, self.size * 3, self.size * 4, self.size * 3 + self.stroke])
        time.sleep(0.2)

    def x(self,row,col):
        a = Point((row+1)*self.size + self.stroke*3,(col+1)*self.size + self.stroke*2)
        b = Point(a.getX()-self.stroke,a.getY()+self.stroke)
        c = Point(a.getX()+self.size-self.stroke*4,a.getY()+self.size-self.stroke*4)
        d = Point(c.getX()-self.stroke,c.getY()+self.stroke)
        poly = Polygon([a,b,d,c])
        poly.setFill('red')
        poly.draw(self.win)
        e = Point(c.getX(),b.getY())
        f = Point(d.getX(),a.getY())
        g = Point(b.getX(),c.getY())
        h = Point(a.getX(),d.getY())
        poly = Polygon([e,f,g,h])
        poly.setFill('red')
        poly.draw(self.win)

    def o(self,row,col):
        center = Point((row+1)*self.size + self.size * 0.5 + self.stroke//2,(col+1)*self.size + self.size * 0.5 + self.stroke//2)
        outer = Circle(center, self.size//3)
        outer.setFill('blue')
        outer.draw(self.win)
        inner = Circle(center, self.size//4.5)
        inner.setFill('white')
        inner.draw(self.win)
