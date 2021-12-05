import sys
import importlib
import argparse
import time
import os

from game import Game
from players.guesser import *
from players.codemaster import *

TWO_PLAYER = True

class GameRun:
    """Class that builds and runs a Game based on command line arguments"""

    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Run the Codenames AI competition game.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument("--seed", help="Random seed value for board state -- integer or 'time'", default='time')
        parser.add_argument("--w2v", help="Path to w2v file or None", default=None)
        parser.add_argument("--glove", help="Path to glove file or None", default=None)
        parser.add_argument("--wordnet", help="Name of wordnet file or None, most like ic-brown.dat", default=None)
        parser.add_argument("--glove_cm", help="Path to glove file or None", default=None)
        parser.add_argument("--glove_guesser", help="Path to glove file or None", default=None)
        parser.add_argument("--no_log", help="Supress logging", action='store_true', default=False)
        parser.add_argument("--no_print", help="Supress printing", action='store_true', default=False)
        parser.add_argument("--game_name", help="Name of game in log", default="default")

        args = parser.parse_args()

        self.do_log = not args.no_log
        self.do_print = not args.no_print
        if not self.do_print:
            self._save_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
        self.game_name = args.game_name

        self.g_kwargs = {}
        self.cm_kwargs = {}

        # if the game is going to have an ai, load up word vectors
        if sys.argv[1] != "human" or sys.argv[2] != "human":
            if args.wordnet is not None:
                brown_ic = Game.load_wordnet(args.wordnet)
                self.g_kwargs["brown_ic"] = brown_ic
                self.cm_kwargs["brown_ic"] = brown_ic
                print('loaded wordnet')

            if args.glove is not None:
                glove_vectors = Game.load_glove_vecs(args.glove)
                self.g_kwargs["glove_vecs"] = glove_vectors
                self.cm_kwargs["glove_vecs"] = glove_vectors
                print('loaded glove vectors')

            if args.w2v is not None:
                w2v_vectors = Game.load_w2v(args.w2v)
                self.g_kwargs["word_vectors"] = w2v_vectors
                self.cm_kwargs["word_vectors"] = w2v_vectors
                print('loaded word vectors')

            if args.glove_cm is not None:
                glove_vectors = Game.load_glove_vecs(args.glove_cm)
                self.cm_kwargs["glove_vecs"] = glove_vectors
                print('loaded glove vectors')

            if args.glove_guesser is not None:
                glove_vectors = Game.load_glove_vecs(args.glove_guesser)
                self.g_kwargs["glove_vecs"] = glove_vectors
                print('loaded glove vectors')

        # set seed so that board/keygrid can be reloaded later
        if args.seed == 'time':
            self.seed = time.time()
        else:
            self.seed = int(args.seed)

    def __del__(self):
        """reset stdout if using the do_print==False option"""
        if not self.do_print:
            sys.stdout.close()
            sys.stdout = self._save_stdout

    def import_string_to_class(self, import_string):
        """Parse an import string and return the class"""
        parts = import_string.split('.')
        module_name = '.'.join(parts[:len(parts) - 1])
        class_name = parts[-1]

        module = importlib.import_module(module_name)
        my_class = getattr(module, class_name)

        return my_class

def generateAllMatchups():
    matchups = []
    codemasters = ["codemaster_glove_03","codemaster_glove_05","codemaster_glove_07",\
               "codemaster_w2v_03","codemaster_w2v_05","codemaster_w2v_07"]
    cm_guessers = {"codemaster_glove_03":"guesser_glove","codemaster_glove_05":"guesser_glove",\
               "codemaster_glove_07":"guesser_glove","codemaster_w2v_03":"guesser_w2v",\
               "codemaster_w2v_05":"guesser_w2v","codemaster_w2v_07":"guesser_w2v"}
    for cm1 in codemasters:
        g1 = cm_guessers[cm1]
        for cm2 in codemasters:
            if cm1 != cm2 and g1 != "guesser_glove":
                g2 = cm_guessers[cm2]
                matchups.append([(cm1, g1),(cm2, g2)])
    return matchups

def runAllSimulatedGames():
    reps = input("Enter how many times you want to simulate all matchups: ")
    print("Simulating all matchups " + reps + " times")

    matchups = generateAllMatchups()
    game_setup = GameRun()

    for rep in range(int(reps)):
        for matchup in matchups:
            red = matchup[0]
            blue = matchup[1]
            cm1 = red[0]
            g1 = red[1]
            cm2 = blue[0]
            g2 = blue[1]
            print(f'Red CM: {cm1} BLUE CM: {cm2}')
            print(f'RED G: {g1} BLUE G {g2}')
            game = Game(game_setup.import_string_to_class(f"players.{cm1}.AICodemaster"),
                    game_setup.import_string_to_class(f"players.{g1}.AIGuesser"),
                    game_setup.import_string_to_class(f"players.{cm2}.AICodemaster"),
                    game_setup.import_string_to_class(f"players.{g2}.AIGuesser"),
                    seed=game_setup.seed,
                    do_print=game_setup.do_print,
                    do_log=game_setup.do_log,
                    game_name=game_setup.game_name,
                    cm_kwargs=game_setup.cm_kwargs,
                    g_kwargs=game_setup.g_kwargs)
            game.run()

if __name__ == "__main__":
    runAllSimulatedGames()