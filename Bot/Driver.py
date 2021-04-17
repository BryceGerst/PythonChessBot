import sys
sys.path.append('../GUI/')
from BotDisplay import Display
import Bot

disp = Display()

nnet = Bot.do_self_play(2,1,disp)
