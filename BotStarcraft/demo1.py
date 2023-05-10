from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
# from bots.supermente_drone import Supermente
from bots.supermente_zerling import Supermente

run_game(maps.get("AcropolisLE"), [
    Bot(Race.Zerg, Supermente()),
    Computer(Race.Terran, Difficulty.Hard)
], realtime=False)

