import tensorflow as tf
import tensorflow_lattice as tfl
import numpy as np
from tensorflow.keras import Model
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten
from tensorflow.keras.activations import relu

import sys
sys.path.append('../ChessEngine/')
from Game import Game

board_width = 8
board_height = 8
num_channels = 12 # will be increased later to 19

# normalize on axis -1 because the data format is channels last
# not entirely sure what a linear layer is, but I use combination of a Dense one and Flatten instead
# need to make BatchNormalization layers for every time they are used because they can't be created every time the model is called!

class AlphaModel(Model):
    def __init__(self):
        super(AlphaModel, self).__init__()

        # sparse categorical cross entropy is the loss function for the policy
        # mean squared error is the loss function for the value
        self.loss_objects = [tf.keras.losses.SparseCategoricalCrossentropy(from_logits = False), tf.keras.losses.MeanSquaredError()]

        # input layer
        self.input_layer = Conv2D(input_shape = (board_height, board_width, num_channels), filters = 256, kernel_size=(3, 3), strides = 1, padding = 'same', data_format = 'channels_last', use_bias = False)

        # Residual tower
        # block one
        self.res_a_one = self.gen_conv2d()
        self.res_a_two = self.gen_conv2d()
        # block two
        self.res_b_one = self.gen_conv2d()
        self.res_b_two = self.gen_conv2d()
        # block three
        self.res_c_one = self.gen_conv2d()
        self.res_c_two = self.gen_conv2d()
        # block four
        self.res_d_one = self.gen_conv2d()
        self.res_d_two = self.gen_conv2d()
        # block five
        self.res_e_one = self.gen_conv2d()
        self.res_e_two = self.gen_conv2d()
        # block six
        self.res_f_one = self.gen_conv2d()
        self.res_f_two = self.gen_conv2d()
        # block seven
        self.res_g_one = self.gen_conv2d()
        self.res_g_two = self.gen_conv2d()
        # block eight
        self.res_h_one = self.gen_conv2d()
        self.res_h_two = self.gen_conv2d()
        # block nine
        self.res_i_one = self.gen_conv2d()
        self.res_i_two = self.gen_conv2d()
        # block ten
        self.res_j_one = self.gen_conv2d()
        self.res_j_two = self.gen_conv2d()
        # block eleven
        self.res_k_one = self.gen_conv2d()
        self.res_k_two = self.gen_conv2d()
        # block twelve
        self.res_l_one = self.gen_conv2d()
        self.res_l_two = self.gen_conv2d()
        # block thirteen
        self.res_m_one = self.gen_conv2d()
        self.res_m_two = self.gen_conv2d()
        # block fourteen
        self.res_n_one = self.gen_conv2d()
        self.res_n_two = self.gen_conv2d()
        # block fifteen
        self.res_o_one = self.gen_conv2d()
        self.res_o_two = self.gen_conv2d()
        # block sixteen
        self.res_p_one = self.gen_conv2d()
        self.res_p_two = self.gen_conv2d()
        # block seventeen
        self.res_q_one = self.gen_conv2d()
        self.res_q_two = self.gen_conv2d()
        # block eighteen
        self.res_r_one = self.gen_conv2d()
        self.res_r_two = self.gen_conv2d()
        # block nineteen
        self.res_s_one = self.gen_conv2d()
        self.res_s_two = self.gen_conv2d()
        # end residual tower

        # policy head
        self.policy_one = self.gen_conv2d()
        self.policy_two = Conv2D(filters = 73, kernel_size = (3, 3), strides = 1, padding = 'same', data_format = 'channels_last', use_bias = False) # not sure about kernel size, stride, bias, or batch normalization for this one
        self.policy_three = Flatten(data_format = 'channels_last')

        # value head
        self.value_one = Conv2D(filters = 1, kernel_size=(1, 1), strides = 1, data_format = 'channels_last', use_bias = False)
        self.value_two = Dense(units = 256, activation = 'relu', use_bias = False)
        self.value_three = Flatten(data_format = 'channels_last')
        self.value_four = Dense(units = 1, activation = 'tanh', use_bias = False)

    def gen_conv2d(self):
        return Conv2D(filters = 256, kernel_size=(3, 3), strides = 1, padding = 'same', data_format = 'channels_last', use_bias = False)

    def rect_norm(self, val):
        return relu(BatchNormalization(axis = -1)(val))

    def call(self, x):
        x = self.input_layer(x)
        x = self.rect_norm(x)

        # block 1
        x_skip = x
        x = self.res_a_one(x)
        x = self.rect_norm(x)
        x = self.res_a_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_a_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x) 
        # block 2
        x_skip = x
        x = self.res_b_one(x)
        x = self.rect_norm(x)
        x = self.res_b_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_b_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)
        # block 3
        x_skip = x
        x = self.res_c_one(x)
        x = self.rect_norm(x)
        x = self.res_c_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_c_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)
        # block 4
        x_skip = x
        x = self.res_d_one(x)
        x = self.rect_norm(x)
        x = self.res_d_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_d_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)
        # block 5
        x_skip = x
        x = self.res_e_one(x)
        x = self.rect_norm(x)
        x = self.res_e_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_e_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)
        # block 6
        x_skip = x
        x = self.res_f_one(x)
        x = self.rect_norm(x)
        x = self.res_f_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_f_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)
        # block 7
        x_skip = x
        x = self.res_g_one(x)
        x = self.rect_norm(x)
        x = self.res_g_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_g_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)
        # block 8
        x_skip = x
        x = self.res_h_one(x)
        x = self.rect_norm(x)
        x = self.res_h_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_h_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)
        # block 9
        x_skip = x
        x = self.res_i_one(x)
        x = self.rect_norm(x)
        x = self.res_i_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_i_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)
        # block 10
        x_skip = x
        x = self.res_j_one(x)
        x = self.rect_norm(x)
        x = self.res_j_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_j_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)
        # block 11
        x_skip = x
        x = self.res_k_one(x)
        x = self.rect_norm(x)
        x = self.res_k_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_k_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)
        # block 12
        x_skip = x
        x = self.res_l_one(x)
        x = self.rect_norm(x)
        x = self.res_l_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_l_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)
        # block 13
        x_skip = x
        x = self.res_m_one(x)
        x = self.rect_norm(x)
        x = self.res_m_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_m_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)
        # block 14
        x_skip = x
        x = self.res_n_one(x)
        x = self.rect_norm(x)
        x = self.res_n_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_n_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)
        # block 15
        x_skip = x
        x = self.res_o_one(x)
        x = self.rect_norm(x)
        x = self.res_o_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_o_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)
        # block 16
        x_skip = x
        x = self.res_p_one(x)
        x = self.rect_norm(x)
        x = self.res_p_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_p_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)
        # block 17
        x_skip = x
        x = self.res_q_one(x)
        x = self.rect_norm(x)
        x = self.res_q_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_q_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)
        # block 18
        x_skip = x
        x = self.res_r_one(x)
        x = self.rect_norm(x)
        x = self.res_r_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_r_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)
        # block 19
        x_skip = x
        x = self.res_s_one(x)
        x = self.rect_norm(x)
        x = self.res_s_two(x)
        x = BatchNormalization(axis = -1)(x)
        x_skip = self.res_s_two(x_skip)
        x_skip = BatchNormalization(axis = -1)(x_skip)
        x = (x + x_skip)
        x = self.rect_norm(x)

        # output 1
        policy = self.policy_one(x)
        policy = self.rect_norm(policy)
        policy = self.policy_two(policy)
        policy = self.policy_three(policy)

        # output 2
        value = self.value_one(x)
        value = self.rect_norm(value)
        value = self.value_two(value)
        value = self.value_three(value)
        value = self.value_four(value)
        
        return policy, value

##    def train_step(self, data):
##        # Unpack the data. Its structure depends on your model and
##        # on what you pass to `fit()`.
##        x, y = data
##
##        with tf.GradientTape() as tape:
##            y_pred = self(x, training=True)  # Forward pass
##            # Compute the loss value
##            # (the loss function is configured in `compile()`)
##            loss = self.compiled_loss(y, y_pred, regularization_losses=self.losses)
##
##        # Compute gradients
##        trainable_vars = self.trainable_variables
##        gradients = tape.gradient(loss, trainable_vars)
##        # Update weights
##        self.optimizer.apply_gradients(zip(gradients, trainable_vars))
##        # Update metrics (includes the metric that tracks the loss)
##        self.compiled_metrics.update_state(y, y_pred)
##        # Return a dict mapping metric names to current value
##        return {m.name: m.result() for m in self.metrics}

    def train_step(self, data):
        print('hola!')
        inputs, targets = data

        with tf.GradientTape() as tape:
            outputs = self(inputs, training = True)
            losses = [l(t, o) for l, o, t in zip(self.loss_objects, outputs, targets)]

        gradients = tape.gradient(losses, self.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))
        self.compiled_metrics.update_state(outputs, targets)
        return {m.name: m.result() for m in self.metrics}


    # https://stackoverflow.com/questions/59690188/how-do-i-make-a-multi-output-tensorflow-2-neural-network-for-both-regression-and
    # ^^^ this is a thing worth looking at some point


am = AlphaModel()
opt = tf.keras.optimizers.Adam(learning_rate = 0.02)
am.compile(optimizer = opt, metrics = ['accuracy'])
g = Game()
inputs = g.get_nnet_inputs()
new_inputs = np.array(inputs)
#print(new_inputs)
new_inputs = new_inputs.reshape(1, board_height, board_width, num_channels)
#print(new_inputs.shape)
#print(new_inputs)
p, v = am(new_inputs)
#print(p.shape)
#print(v.shape)
#am.summary()
#print(am.optimizer)
#print(am.compiled_metrics)
am.fit(x = new_inputs, y = (p, v))




