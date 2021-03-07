import os
import sys
import time

import numpy as np
from tqdm import tqdm

# From https://github.com/suragnair/alpha-zero-general/blob/master/othello/tensorflow/NNet.py

import tensorflow as tf
from ChessNNet import ChessNNet as cnnet

board_size = (8, 8)
action_size = 4672

class dotdict(dict):
    def __getattr__(self, name):
        return self[name]

args = dotdict({
    'lr': 0.001,
    'dropout': 0.3,
    'epochs': 10,
    'batch_size': 4, # 64
    'num_channels': 512,
})


class AverageMeter(object):
    # From https://github.com/pytorch/examples/blob/master/imagenet/main.py

    def __init__(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def __repr__(self):
        return f'{self.avg:.2e}'

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count

class NNetWrapper:
    def __init__(self):
        self.nnet = cnnet(args)
        self.board_x, self.board_y = board_size
        self.action_size = action_size

        self.sess = tf.compat.v1.Session(graph=self.nnet.graph)
        self.saver = None
        with tf.compat.v1.Session() as temp_sess:
            temp_sess.run(tf.compat.v1.global_variables_initializer())
        self.sess.run(tf.compat.v1.variables_initializer(self.nnet.graph.get_collection('variables')))

    def train(self, examples):
        """
        examples: list of examples, each example is of form (board, pi, v)
        """

        for epoch in range(args.epochs):
            print('EPOCH ::: ' + str(epoch + 1))
            pi_losses = AverageMeter()
            v_losses = AverageMeter()
            batch_count = int(len(examples) / args.batch_size)

            # self.sess.run(tf.local_variables_initializer())
            t = tqdm(range(batch_count), desc='Training Net')
            for _ in t:
                sample_ids = np.random.randint(len(examples), size=args.batch_size)
##                boards = []
##                pis = []
##                vs = []
##                for i in sample_ids:
##                    example = examples[i]
##                    for component in example: # each component is a move in the example
##                        boards.append(component[0])
##                        pis.append(component[1])
##                        vs.append(component[2])
                
                boards, pis, vs = list(zip(*[examples[i] for i in sample_ids])) # what they had: 

                # predict and compute gradient and do SGD step
                input_dict = {self.nnet.input_boards: boards, self.nnet.target_pis: pis, self.nnet.target_vs: vs,
                              self.nnet.isTraining: True}
                #input_dict = {self.nnet.input_boards: boards, self.nnet.target_pis: pis, self.nnet.target_vs: vs,
                              #self.nnet.dropout: args.dropout, self.nnet.isTraining: True}

                print(np.array(boards).shape)
                print(np.array(pis).shape)
                print(np.array(vs).shape)

                # record loss
                print('made it to a')
                self.sess.run(self.nnet.train_step, feed_dict=input_dict)
                print('made it to b')
                pi_loss, v_loss = self.sess.run([self.nnet.loss_pi, self.nnet.loss_v], feed_dict=input_dict)
                pi_losses.update(pi_loss, len(boards))
                v_losses.update(v_loss, len(boards))
                t.set_postfix(Loss_pi=pi_losses, Loss_v=v_losses)

    def predict(self, board):
        """
        board: np array with board
        """
        # timing
        start = time.time()

        # preparing input
        #print(board)
        #board = board[np.newaxis, :, :]

        # run
        prob, v = self.sess.run([self.nnet.prob, self.nnet.v],
                                feed_dict={self.nnet.input_boards: board, self.nnet.dropout: 0,
                                           self.nnet.isTraining: False})

        # print('PREDICTION TIME TAKEN : {0:03f}'.format(time.time()-start))
        return prob[0], v[0]

    def save_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print("Checkpoint Directory does not exist! Making directory {}".format(folder))
            os.mkdir(folder)
        else:
            print("Checkpoint Directory exists! ")
        if self.saver == None:
            self.saver = tf.train.Saver(self.nnet.graph.get_collection('variables'))
        with self.nnet.graph.as_default():
            self.saver.save(self.sess, filepath)

    def load_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath + '.meta'):
            raise ("No model in path {}".format(filepath))
        with self.nnet.graph.as_default():
            self.saver = tf.train.Saver()
            self.saver.restore(self.sess, filepath)
