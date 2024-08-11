import random
import sys

from bot.main import MassReaper
from ladder import run_ladder_game
from sc2 import maps
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import AIBuild, Bot, Computer

bot1 = Bot(Race.Terran, MassReaper())


def main():
    # Ladder game started by LadderManager
    print("Starting ladder game...")
    result, opponentid = run_ladder_game(bot1)
    print(result, " against opponent ", opponentid)


# Start game
if __name__ == "__main__":
    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        result, opponentid = run_ladder_game(bot1)
        print(result, " against opponent ", opponentid)
    else:
        # Local game
        random_map = random.choice(
            [
                "Equilibrium513AIE",
                "Gresvan513AIE",
                "GoldenAura513AIE",
                "HardLead513AIE",
                "Oceanborn513AIE",
                "SiteDelta513AIE",
            ]
        )
        random_race = random.choice(
            [
                Race.Zerg,
                Race.Terran,
                Race.Protoss,
            ]
        )
        print("Starting local game...")

        run_game(
            maps.get(random_map),
            [
                bot1,
                Computer(random_race, Difficulty.CheatVision, ai_build=AIBuild.Macro),
            ],
            realtime=False,
        )
