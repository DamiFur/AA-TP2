import random
import matplotlib.pyplot as plt

# I need a board representation that is:
# - hashable
# - compact under sparsity
# - unique representation of every board (else Q as dictionary wont work)
# - remark: the representation must ONLY be efficient to hash on Players,
#   not for the overall game

class FourInALine:

    def __init__(self, playerX, playerO, board_width=7, board_height=7, win_reward=1, lose_reward=-1, tie_reward=0.25):
        self.playerX, self.playerO = playerX, playerO
        # self.playerX_turn = random.choice([True, False])
        self.playerX_turn = True
        self.turns_played = 0;
        self.width  = board_width
        self.height = board_height
        self.board = [ [' ' for _ in xrange(self.width)] for _ in xrange(self.height)]

        self.win_reward  = win_reward
        self.lose_reward = lose_reward
        self.tie_reward  = tie_reward

    def play_game(self):

        self.playerX.start_game('X', self.board)
        self.playerO.start_game('O', self.board)

        while True:

            # give turn to player
            if self.playerX_turn:
                player, char, other_player = self.playerX, 'X', self.playerO
            else:
                player, char, other_player = self.playerO, 'O', self.playerX
            if player.breed == "Human":
                self.display_board()

            # before selecting a move, check if the board is full
            if self.board_full():
                player.reward(self.tie_reward, self.board)
                other_player.reward(self.tie_reward, self.board)
                if self.playerX.breed == "Human" or self.playerO.breed == "Human":
                    self.display_board()
                    print "It's a tie! %d" % self.turns_played
                return "tie"

            # current player selects action (a column)
            selected_column = player.move(self.board)

            # check game status and give rewards to players
            # game ends if a player wins or the board is full

            # find move row (we only have the column)
            move_row = -1
            for row in xrange(self.height):
                if self.board[row][selected_column] == ' ':
                    move_row = row
                    break

            # check if action is illegal (forced legal tho, for testing purposes)
            if move_row == -1:
                print 'Illegal move!'
                player.reward(-99, self.board)
                break

            self.board[move_row][selected_column] = char
            if self.player_wins(char, (move_row, selected_column)):
                player.reward(self.win_reward, self.board)
                other_player.reward(self.lose_reward, self.board)

                if self.playerX.breed == "Human" or self.playerO.breed == "Human":
                    self.display_board()
                    print "%s wins!" % player.breed

                return char
            
            # update the Q function of the other player
            other_player.reward(0, self.board)

            # now its the turn of the other player
            self.playerX_turn = not self.playerX_turn

            self.turns_played = self.turns_played + 1;


    def player_wins(self, char, last_move):

        row, col = last_move

        # check for a row win
        count_char = 1
        i = col - 1
        while i >= 0 and self.board[row][i] == char and count_char < 4:
            count_char = count_char + 1
            i = i - 1

        i = col + 1
        while i < self.width and self.board[row][i] == char and count_char < 4:
            count_char = count_char + 1
            i = i + 1

        if count_char == 4:
            # print 'row win'
            return True;

        # check for col win
        count_char = 1
        i = row - 1
        while i >= 0 and self.board[i][col] == char and count_char < 4:
            count_char = count_char + 1
            i = i - 1

        i = row + 1
        while i < self.height and self.board[i][col] == char and count_char < 4:
            count_char = count_char + 1
            i = i + 1

        if count_char == 4: 
            # print 'col win'
            return True

        # check for a ascending diagonal win
        count_char = 1;
        i = row-1;
        j = col-1;

        while i >= 0 and j >= 0 and self.board[i][j] == char and count_char < 4:
            count_char = count_char + 1
            i = i - 1
            j = j - 1

        i = row+1;
        j = col+1;

        while i < self.height and j < self.width and self.board[i][j] == char and count_char < 4:
            count_char = count_char + 1
            i = i + 1
            j = j + 1

        if count_char == 4:
            # print 'asc diag win'
            return True

        # check for an descending diagonal win
        count_char = 1;
        i = row+1;
        j = col-1;

        while i < self.height and j >= 0 and self.board[i][j] == char and count_char < 4:
            count_char = count_char + 1
            i = i + 1
            j = j - 1

        i = row-1;
        j = col+1;

        while i >= 0 and j < self.width and self.board[i][j] == char and count_char < 4:
            count_char = count_char + 1
            i = i - 1
            j = j + 1

        # if count_char == 4:
            # print 'desc diag win'

        return count_char == 4

    def board_full(self):
        return self.turns_played == self.width * self.height

    def display_board(self):
        for row in reversed(xrange(self.height)):
            print self.board[row]
        print '----'*self.width
        print map(str,xrange(self.width))

class Player(object):
    def __init__(self):
        self.breed = "Human"

    def start_game(self, char, board):
        print "\nNew game!"

    def move(self, board):
        column = -1
        while not 0 <= column < len(board[0]):
            column = int(raw_input("Your move? "))

        return column

    def reward(self, value, board):
        pass
        # print "{} rewarded: {}".format(self.breed, value)

    def available_moves(self, board):
        moves = []
        for col in xrange(len(board[0])):
            for row in xrange(len(board)):
                if board[row][col] == ' ':
                    moves.append(col)
                    break
        return moves

class RandomPlayer(Player):
    def __init__(self):
        self.breed = "Random"

    def reward(self, value, board):
        pass

    def start_game(self, char, board):
        pass

    def move(self, board):
        return random.choice(self.available_moves(board))


class QLearningPlayer(Player):
    def __init__(self, epsilon=0.2, alpha=0.3, gamma=0.9):
        self.breed = "Qlearner"
        self.q = {} # (state, action) keys: Q values
        self.epsilon = epsilon # e-greedy chance of random exploration
        self.alpha = alpha # learning rate
        self.gamma = gamma # discount factor for future rewards


    def start_game(self, char, board):
        self.last_board = self.copy_board(board)
        self.last_move = None

    def getQ(self, state, action):
        # encourage exploration; "optimistic" 1.0 initial values
        if self.q.get((self.encode_board(state), action)) is None:
            self.q[(self.encode_board(state), action)] = 1.0
        return self.q.get((self.encode_board(state), action))

    # TODO: find an efficient encoding! careful with excecution time as well!
    def encode_board(self, board):
        # encoding = ""
        # for row in xrange(len(board)):
        #     for col in xrange(len(board[0])):
        #         encoding = encoding + board[row][col]

        # return encoding

        return str(board)

    def copy_board(self, board):
        return [ [board[row][col] for col in xrange(len(board[0]))] for row in xrange(len(board))];

    def move(self, board):

        self.last_board = self.copy_board(board) # copy is needed, else board changes, we need to store the prev board.
        actions = self.available_moves(board)

        if random.random() < self.epsilon: # explore!
            self.last_move = random.choice(actions)
            return self.last_move

        qs = [self.getQ(self.last_board, a) for a in actions]
        maxQ = max(qs)

        if qs.count(maxQ) > 1:
            # more than 1 best option; choose among them randomly
            best_options = [i for i in xrange(len(actions)) if qs[i] == maxQ]
            i = random.choice(best_options)
        else:
            i = qs.index(maxQ)

        self.last_move = actions[i]
        return actions[i]

    def reward(self, value, board):
        if self.last_move:
            self.learn(self.last_board, self.last_move, value, self.copy_board(board))

    def learn(self, state, action, reward, result_state):
        prevQ = self.getQ(state, action)
        maxqnew = max([self.getQ(result_state, a) for a in self.available_moves(state)])
        self.q[(self.encode_board(state), action)] = prevQ + self.alpha * ((reward + self.gamma*maxqnew) - prevQ)


def training_performance_experiment(p1, p2, width, height, filename, training_cycles):

    # when testing performance, do not train on
    # experiments + follow Q function
    # p1 is Q learner

    if p1.breed == "Qlearner":
        p1_epsilon_save = p1.epsilon
        p1_alpha_save   = p1.alpha

    if p2.breed == "Qlearner":
        p2_epsilon_save = p2.epsilon
        p2_alpha_save   = p2.alpha

    epochs  = []
    p1_wins = []
    p2_wins = []
    draws   = []

    training_jump = 500;

    for i in range(0,training_cycles,training_jump):

        p1_count = 0
        p2_count = 0

        # make sure players do not learn while range testing
        if p1.breed == "Qlearner":
            p1.epsilon = 0;
            p1.alpha   = 0;

        if p2.breed == "Qlearner":
            p1.epsilon = 0;
            p1.alpha   = 0;

        for _ in range(500):

            t = FourInALine(p1, p2, width, height)
            res = t.play_game()
            
            if res == 'X':
                p1_count = p1_count + 1
            elif res == 'O':
                p2_count = p2_count + 1

        epochs.append(i)
        p1_wins.append(float(p1_count)/500)
        p2_wins.append(float(p2_count)/500)
        draws.append(1-(float(p1_count)+float(p2_count))/500)

        # restore learning parameters
        if p1.breed == "Qlearner":
            p1.epsilon = p1_epsilon_save
            p1.alpha   = p1_alpha_save

        if p2.breed == "Qlearner":
            p2.epsilon = p2_epsilon_save
            p2.alpha   = p2_alpha_save

        # keep training
        for _ in range(training_jump):
            t = FourInALine(p1, p2, width, height)
            t.play_game()

        if i % 50000 == 0 and i != 0:

            plt.figure()
            plt.title('Tasa de aciertos en funcion a numero de \n entrenamiento (promedio en ventanas 500 trials)')
            plt.xlabel('Numero de entrenamiento')
            plt.ylabel('Tasa Victorias')
            plt.ylim([0,1])
            plt.plot(epochs, p1_wins)
            plt.plot(epochs, p2_wins)
            plt.plot(epochs, draws)           
            plt.savefig(filename + ' ' + str(i) + '.png')
            plt.show()

    plt.figure()
    plt.title('Tasa de aciertos en funcion a numero de \n entrenamiento (promedio en ventanas 500 trials)')
    plt.xlabel('Numero de entrenamiento')
    plt.ylabel('Tasa Victorias')
    plt.ylim([0,1])
    plt.plot(epochs, p1_wins)
    plt.plot(epochs, p2_wins)
    plt.plot(epochs, draws) 

    plt.savefig(filename + '.png')
    plt.show()

    return {'epochs': epochs, 'p1': p1_wins, 'p2': p2_wins, 'draws': draws}
    # return (p1_wins, p2_wins, draws)

# Cuidado, ponerle un nombre de experimento diferente a cada experimento para que no se sobreescriban los graficos

tests = [
# {'exp_name': 'Qlearner_vs_Random', 'training_cycles': 100000, 'p1_type': 'Qlearner', 'p2_type': 'Random', 'p1_epsilon': 0.2, 'p1_alpha': 0.8, 'p1_gamma': 0.9, 'p2_epsilon': 0.2, 'p2_alpha': 0.8, 'p2_gamma': 0.9, 'game_width': 5, 'game_height': 5, 'win_reward': 1, 'lose_reward': -1, 'tie_reward': 0.5},

# Qlearner vs Qlearner
# {'exp_name': 'Random_vs_Random', 'training_cycles': 500000, 'p1_type': 'Random', 'p2_type': 'Random', 'game_width': 6, 'game_height': 6, 'win_reward': 1, 'lose_reward': -1, 'tie_reward': 0.5},
{'exp_name': 'Qlearner vs Qlearner', 'training_cycles': 500000, 'p1_type': 'Qlearner', 'p2_type': 'Qlearner', 'p1_epsilon': 0.2, 'p1_alpha': 0.8, 'p1_gamma': 0.9, 'p2_epsilon': 0.2, 'p2_alpha': 0.8, 'p2_gamma': 0.9, 'game_width': 5, 'game_height': 5, 'win_reward': 1, 'lose_reward': -100, 'tie_reward': 0.5}

# # Qlearner vs Random
# {'exp_name': 'Qlearner vs Random (epsilon=0.1)', 'training_cycles': 100000, 'p1_type': 'Qlearner', 'p2_type': 'Random', 'p1_epsilon': 0.2, 'p1_alpha': 0.8, 'p1_gamma': 0.9, 'p2_epsilon': 0.2, 'p2_alpha': 0.8, 'p2_gamma': 0.9, 'game_width': 6, 'game_height': 6, 'win_reward': 1, 'lose_reward': -1, 'tie_reward': 0.5},
# {'exp_name': 'Qlearner vs Random (epsilon=0.3)' , 'training_cycles': 100000, 'p1_type': 'Qlearner', 'p2_type': 'Random', 'p1_epsilon': 0.2, 'p1_alpha': 0.8, 'p1_gamma': 0.9, 'p2_epsilon': 0.2, 'p2_alpha': 0.8, 'p2_gamma': 0.9, 'game_width': 6, 'game_height': 6, 'win_reward': 1, 'lose_reward': -1, 'tie_reward': 0.5},

# # Random vs Random
# {'exp_name': 'Random vs Random', 'training_cycles': 500000, 'p1_type': 'Random', 'p2_type': 'Random', 'p1_epsilon': 0.2, 'p1_alpha': 0.8, 'p1_gamma': 0.9, 'p2_epsilon': 0.2, 'p2_alpha': 0.8, 'p2_gamma': 0.9, 'game_width': 6, 'game_height': 6, 'win_reward': 1, 'lose_reward': -1, 'tie_reward': 0.5}
]

for test in tests:

    # Player parameters
    if test['p1_type'] == "Qlearner":
        epsilon = test['p1_epsilon']
        alpha   = test['p1_alpha']
        gamma   = test['p1_gamma']
        p1 = QLearningPlayer(epsilon, alpha, gamma)
    else:
        p1 = RandomPlayer()

    if test['p2_type'] == "Qlearner":
        epsilon = test['p2_epsilon']
        alpha   = test['p2_alpha']
        gamma   = test['p2_gamma']
        p2 = QLearningPlayer(epsilon, alpha, gamma)
    else:
        p2 = RandomPlayer()

    # Board parameters
    width = test['game_width']
    height = test['game_height']
    win_reward  = test['win_reward']
    lose_reward = test['lose_reward']
    tie_reward  = test['tie_reward']

    training_performance_experiment(p1, p2, width, height, test['exp_name'], test['training_cycles'])


test = tests[1]

# Player parameters
if test['p1_type'] == "Qlearner":
    epsilon = test['p1_epsilon']
    alpha   = test['p1_alpha']
    gamma   = test['p1_gamma']
    p1 = QLearningPlayer(epsilon, alpha, gamma)
else:
    p1 = RandomPlayer()

if test['p2_type'] == "Qlearner":
    epsilon = test['p2_epsilon']
    alpha   = test['p2_alpha']
    gamma   = test['p2_gamma']
    p2 = QLearningPlayer(epsilon, alpha, gamma)
else:
    p2 = RandomPlayer()

# Board parameters
width = test['game_width']
height = test['game_height']
win_reward  = test['win_reward']
lose_reward = test['lose_reward']
tie_reward  = test['tie_reward']

epsilon_low = training_performance_experiment(p1, p2, width, height, test['exp_name'], test['training_cycles'])

test = tests[2]

# Player parameters
if test['p1_type'] == "Qlearner":
    epsilon = test['p1_epsilon']
    alpha   = test['p1_alpha']
    gamma   = test['p1_gamma']
    p1 = QLearningPlayer(epsilon, alpha, gamma)
else:
    p1 = RandomPlayer()

if test['p2_type'] == "Qlearner":
    epsilon = test['p2_epsilon']
    alpha   = test['p2_alpha']
    gamma   = test['p2_gamma']
    p2 = QLearningPlayer(epsilon, alpha, gamma)
else:
    p2 = RandomPlayer()

# Board parameters
width = test['game_width']
height = test['game_height']
win_reward  = test['win_reward']
lose_reward = test['lose_reward']
tie_reward  = test['tie_reward']

epsilon_high = training_performance_experiment(p1, p2, width, height, test['exp_name'], test['training_cycles'])

def comparing_epsilons(epsilon_low, epsilon_high):
    plt.figure()
    plt.title('Tasa de aciertos en funcion a numero de \n entrenamiento (promedio en ventanas 500 trials)')
    plt.xlabel('Numero de entrenamiento')
    plt.ylabel('Tasa Victorias')
    plt.ylim([0,1])
    plt.plot(epochs, epsilon_low['p1'])
    plt.plot(epochs, epsilon_low['p2'])
    plt.plot(epochs, epsilon_high['p1'])
    plt.plot(epochs, epsilon_high['p2'])

    plt.savefig(filename + '.png')
    plt.show()

# # board parameters
# width = 6;
# height = 6;
# win_reward  = 100
# lose_reward = -1
# tie_reward  = 0.5

# epsilon = 0.2
# alpha   = 0.8
# gamma   = 1
# p1 = QLearningPlayer(epsilon, alpha, gamma)

# p2 = RandomPlayer()
# epsilon = 0.2
# alpha   = 1
# gamma   = 0.9
# p2 = QLearningPlayer(epsilon, alpha, gamma)

# for i in xrange(500000):
#     t = FourInALine(p1, p2, width, height, win_reward, lose_reward, tie_reward)
#     t.play_game()

# # human against the machine!
# p2 = Player()
# p1.epsilon = 0 # no deviating
# p1.alpha = 1 # no learning

# # print p2.q

# while True:
#     t = FourInALine(p1, p2, width, height, win_reward, lose_reward, tie_reward)
#     t.play_game()