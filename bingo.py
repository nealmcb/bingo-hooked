from numpy import *
from collections import Counter

def new_board():
    cols = arange(1,76).reshape(5,15)
    return array([random.permutation(c)[:5] for c in cols])

def new_game():
    for token in random.permutation(arange(1,76)):
        yield token

def winning(B):
    if (B.sum(axis=0)==5).any(): return True
    if (B.sum(axis=1)==5).any(): return True
    if trace(B)==5 or trace(B.T)==5: return True
    return False

def game_length(board, game):
    B = zeros((5,5),dtype=bool)
    B[2,2] = True
    for n,idx in enumerate(game):
        if winning(B): return n
        B[board==idx] = True

def simulation(trials):
    C = Counter()
    b = new_board()
    for _ in xrange(trials):
        C[game_length(b, new_game())] += 1
    return C

repeats = 10**2
trials  = 10**3

from multiprocessing import *
P = Pool()
sol = sum(P.map(simulation,[trials,]*repeats))
P.close()
P.join()

X = array(sorted(sol.keys()))
Y = array([float(sol[x]) for x in X])
Y/= repeats*trials

EX = array(list(sol.elements()))
print "Mean and stddev", EX.mean(), EX.std()

import pylab as plt
plt.fill_between(X, Y, lw=2, alpha=.8)

plt.plot([EX.mean(),EX.mean()], [0,1.2*max(Y)], 'r--',lw=2)
plt.ylim(ymax = 1.2*max(Y))
plt.xlabel("Expected game length")

plt.show()
