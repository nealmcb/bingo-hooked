"""Simulate Bingo, tracking number of numbers until a win.
Draw a plot of the denisty function.

With default of 100 repeats, 1000 trials, takes perhaps 100 seconds on a modern CPU.

Based on @Hooked answer at https://math.stackexchange.com/a/281661/5307

TODO:
collect results incrementally with map_async, print out early if requested.
 http://blog.shenwei.me/python-multiprocessing-pool-difference-between-map-apply-map_async-apply_async/
"""

from numpy import *
from collections import Counter
from multiprocessing import *
import matplotlib.pyplot as plt
import argparse
import logging

parser = argparse.ArgumentParser(description='Template file python best practices.')

parser.add_argument("--test",  action="store_true", default=False,
  help="Run tests")

parser.add_argument("-d", "--debuglevel", type=int, default=logging.WARNING,
  help="Set logging level to debuglevel, expressed as an integer: "
  "DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50. "
  "The default is %(default)s" )

parser.add_argument('-t', "--trials", type=int, default=1000,
                    help='Number of games per trial')

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
    args = parser.parse_args()

    # Distribute computation via Python multiprocessing package.
    # "repeats" specifies the number of tasks to be farmed out via the Pool
    # "trials" specifies the number of game simulations to run per task
    # The Counters returned by each task are summed together at the end.
    repeats = 100
    trials = args.trials
    P = Pool()
    sol = sum(P.map(simulation, [trials] * repeats))
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
    [print(f'{x:d}, {cum:0.8f}') for x, cum in cdfdata]

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
