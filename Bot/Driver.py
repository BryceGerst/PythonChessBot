import sys
sys.path.append('../ChessEngine/')
from Game import Game
from NNet import NNet
import Bot
import tensorflow as tf
# suppresses the unhelpful warnings tensorflow gives
#tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

start = Game()


nnet = Bot.train_nnet(1,1)
