# Piotr Gdowski
# Reversi player alpha-beta vs mcts 

# coding=utf-8
import sys
import time
from random import choice, seed

ALPHA_BETA_DEEP = 1
MCTS_TIMEOUT = 1 # seconds
M = 8
rounds = 0
coef = (20, -3, 11, 8, 8, 11, -3, 20,
        -3, -7, -4, 1, 1, -4, -7, -3,
        11, -4, 2, 2, 2, 2, -4, 11,
        8, 1, 2, -3, -3, 2, 1, 8,
        8, 1, 2, -3, -3, 2, 1, 8,
        11, -4, 2, 2, 2, 2, -4, 11,
        -3, -7, -4, 1, 1, -4, -7, -3,
        20, -3, 11, 8, 8, 11, -3, 20)

def initial_board():
    B = [ None for i in range(M*M)]
    B[3*M+3] = 1
    B[4*M+4] = 1
    B[3*M+4] = 0
    B[4*M+3] = 0
    return B

dirs  = [ (0,1), (1,0), (-1,0), (0,-1), (1,1), (-1,-1), (1,-1), (-1,1) ]
    
inf = 1000000
def pick_move(grid, level, player=1, a=-inf, b=inf): # returns potential score and last move
    if level == 0 or terminal(grid):
        if terminal(grid):
            if resultat(grid) >= 0: return 100000, None
            return -100000, None
        return judge(grid, player), None # just say something
    best_move = None
    best_score = -inf
    for move in moves(grid, player):
        tmp = list(grid)
        do_move(tmp, move, player)
        result = pick_move(tmp, level - 1, 1-player, -b, -a)
        if -result[0] > best_score:
            best_move = move
            best_score = -result[0]
            if best_score > a:
                a = best_score
                if a >= b:
                    break
    return best_score, best_move
def draw(grid):
    for i in range(M):
        res = []
        for j in range(M):
            b = grid[j*M+i] 
            if b == None:
                res.append('.')
            elif b == 1:
                res.append('X')
            else:
                res.append('O')
        print (''.join(res))
    print()       

def get(grid, x, y):
    if 0 <= x < M and 0 <= y < M:
        return grid[y*M+x]
    return None
    
def judge(grid, player): 
    result = 0 
    
    d = 0
    my, opp = 0,0
    for i in range(M*M):
        if grid[i] == 1: 
            d += coef[i]
            my += 1
        elif grid[i] == 0: 
            d -= coef[i]
            opp += 1
                  
    p = 0
    if my > opp: p = my / (opp + my)
    elif opp > my:  p = -my/(opp + my)

    my, opp = 0,0
    for i in [grid[0], grid[7], grid[56], grid[63]]:
        if i == 1: my += 1
        elif i == 0: opp += 1
    c = (my - opp)

    my, opp = 0,0
    not_none = 0
    if grid[0] is None:
        for i in [grid[1], grid[8], grid[9]]:
            if i == 1: my += 1
            if i == 0: opp += 1
    if grid[7] is None:
        for i in [grid[6], grid[14], grid[15]]:
            if i == 1: my += 1
            if i == 0: opp += 1
    if grid[56] is None:
        for i in [grid[57], grid[48], grid[49]]:
            if i == 1: my += 1
            if i == 0: opp += 1
    if grid[63] is None:
        for i in [grid[62], grid[55], grid[54]]:
            if i == 1: my += 1
            if i == 0: opp += 1
    l = (my - opp)

    my, opp = 0,0
    my = len(list(moves(grid, 1)))
    opp = len(list(moves(grid,0)))
    m = 0
    if my > opp: m = my / (my + opp)
    elif my < opp: m = -opp / (my + opp)
    if player == 0: player -= 1
    return player*(1000 * p + 20000 * c - 3750 * l + 20000 * m + 10 * d) 
    
def choose_move(grid, player):
    ms = list(moves(grid, player))
    if len(ms) > 0:
        #move = pick_move(grid, ALPHA_BETA_DEEP, player)[1]
        #if move is None: 
        #    return choice(ms)
        #return move
        
        return choice(ms) # random player
        
    return None

def terminal(grid):
    return len(list(moves(grid, 0))) == 0 and len(list(moves(grid,1))) == 0 # noone can move

def resultat(grid):
    res = 0
    for i in range(M*M):
        b = grid[i]
        if b == 0: # it's O
            res -= 1
        elif b == 1: # it's X
            res += 1
    return res

def moves(grid, player):
    for y in range(M):
        for x in range(M):
            if grid[y*M+x] == None:
                if any(can_beat(grid, x, y, direction, player) for direction in dirs):
                    yield (x,y) 
    
def can_beat(grid, x, y, d, player):
    dx,dy = d
    x += dx
    y += dy
    cnt = 0
    while get(grid, x, y) == 1-player:
        x += dx
        y += dy
        cnt += 1
    return cnt > 0 and get(grid, x, y) == player

def do_move(grid, move, player):
    if move == None:
        return 
    x,y = move
    x0,y0 = move
    grid[y*M+x] = player
    for dx,dy in dirs:
        x,y = x0,y0
        to_beat = []
        x += dx
        y += dy
        while get(grid, x,y) == 1-player:
            to_beat.append( (x,y) )
            x += dx
            y += dy
        if get(grid, x,y) == player:              
            for (nx,ny) in to_beat:
                grid[ny*M+nx] = player

from math import log, sqrt
def score(N, pair):
    wi, ni = pair 
    if ni == 0:
        return 2
    return wi/ni + sqrt(2 * log(N) / ni)

mcts_tree = {}
def go_random(grid, player):
    if terminal(grid):
        return resultat(grid) > 0 # we won
    ms = list(moves(grid, player))
    if len(ms) > 0:
        do_move(grid, choice(ms), player)
    res = go_random(grid, 1 - player)
    t_g = tuple(grid)
    if t_g not in mcts_tree:
        mcts_tree[t_g] = (res, 1)
    else:
        w, t = mcts_tree[t_g]
        mcts_tree[t_g] = (w + res, t + 1)
    return res

def mcts_move(grid, player):
    all_moves = list(moves(grid, player))
    if len(all_moves) == 0:
        return None
    if tuple(grid) not in mcts_tree:
        mcts_tree[tuple(grid)] = (0, 0) # wins, total 
    tries = 0
    kids = []
    for m in all_moves:
        g = list(grid)
        do_move(g, m, player)
        kids.append((g, m))
        if tuple(g) not in mcts_tree:
            mcts_tree[tuple(g)] = (0, 0)
    best = []        
    end = time.time() + MCTS_TIMEOUT
    while time.time() < end:
        tries += 1
        best_score = -1
        best_kid = None
        for game, mv in kids:
            value = score(tries, mcts_tree[tuple(game)])
            if best_score < value:
                best_score = value
                best_kid = game
                best = [game]
            if best_score == value:
                best.append(game)
        game = choice(best)
        res  = go_random(list(game), 1 - player)
        w, t = mcts_tree[tuple(game)]
        mcts_tree[tuple(game)] = (w + res, t + 1)
    print("#playouts: %d" % (tries))
    return max((mcts_tree[tuple(g)][1],m) for g, m in kids)[1]

games = 200
wins = 0
draws = 0
my_move = None
time_spent_min = 0
time_spent_mcts = 0 
moves_done_min = 0
moves_done_mcts = 0

seed(105) # to make results repeatable
for i in range(games):
    grid = initial_board()
    player = 0 
    mcts_tree = {}
    while not terminal(grid):
        if player == 0:
            t = time.time()
            my_move = choose_move(grid, player)
            time_spent_min += (time.time() - t)
            moves_done_min += 1
        else:
            t = time.time()
            my_move = mcts_move(grid, player)
            time_spent_mcts += (time.time() - t)
            moves_done_mcts += 1
        do_move(grid, my_move, player)
        player = 1 - player
        #draw(grid)
    if resultat(grid) < 0: # more O's om the board
        print("Game no. %d, minmax won" % (i))
        wins += 1
    elif resultat(grid) == 0:
        draws += 1
        print("Game no. %d, draw" % (i))
    else:
        print("Game no. %d, mcts won" % (i))
    

print("Results:\tO's %d : %d : %d X's" % (wins, draws, games-wins-draws))
print("Avg time spent on move for minmax (O's):\t %f" % (time_spent_min / moves_done_min))
print("Avg time spent on move for mcts   (X's):\t %f" % (time_spent_mcts / moves_done_mcts))