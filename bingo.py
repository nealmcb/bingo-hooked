"""Simulate Bingo, tracking number of numbers until a win.
Draw a plot of the denisty function.

With default of 10**2 repeates, 10**3 trials, takes about 100 seconds.

Based on @Hooked answer at https://math.stackexchange.com/a/281661/5307
"""

from numpy import *
from collections import Counter
from multiprocessing import *
import pylab as plt

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
    for _ in range(trials):
        C[game_length(b, new_game())] += 1
    return C


def main():
    # Distribute computation via Python multiprocessing package.
    # "repeats" specifies the number of tasks to be farmed out via the Pool
    # "trials" specifies the number of simulations to run per task
    # The Counters returned by each task are summed together at the end.
    repeats = 10 ** 2
    trials = 10 ** 3
    P = Pool()
    sol = sum(P.map(simulation, [trials, ] * repeats))
    P.close()
    P.join()

    X = array(sorted(sol.keys()))
    Y = array([float(sol[x]) for x in X])
    Y /= repeats * trials
    EX = array(list(sol.elements()))
    print("Mean and stddev", EX.mean(), EX.std())

    cdfdata = list(zip(X, cumsum(Y)))

    print("\nObserved cumulative probability distribution\n")
    print("calls,cumprobability")
    [print(f'{x:d}, {cum:0.4f}') for x, cum in cdfdata]

    plt.fill_between(X, Y, lw=2, alpha=.8)
    plt.plot([EX.mean(), EX.mean()], [0, 1.2 * max(Y)], 'r--', lw=2)
    plt.ylim(ymax=1.2 * max(Y))
    plt.xlabel("Expected game length")
    plt.ylabel("Probability")
    # For interactive use
    # plt.show()
    plt.savefig('bingo-pdf.png')


if __name__ == "__main__":
    main()
