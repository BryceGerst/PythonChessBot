import tensorflow as tf
from tensorflow.keras.layers import Conv2D, BatchNormalization, Dense, Flatten, Input, Add
from tensorflow.keras import Model
from tensorflow.keras.activations import relu
import numpy as np
import sys
sys.path.append('../ChessEngine/')
from Game import Game

board_width = 8
board_height = 8
num_channels = 12 # will be increased later to 19

loss_fns = [tf.keras.losses.CategoricalCrossentropy(from_logits = False), tf.keras.losses.MeanAbsoluteError()]
optimizer = tf.keras.optimizers.Adam(learning_rate = 1e-3)

def gen_conv2d():
    return Conv2D(filters = 256, kernel_size=(3, 3), strides = 1, padding = 'same', data_format = 'channels_last', use_bias = False)

def gen_norm():
    return BatchNormalization(axis = -1)

def init_nnet():
    input_layer = Input(shape = (board_height, board_width, num_channels))
    x = gen_conv2d()(input_layer)
    x = gen_norm()(x)
    x = relu(x)

    # residual tower
    for _ in range(19):
        # layer 1 of residual block
        y = gen_conv2d()(x)
        y = gen_norm()(y)
        y = relu(y)
        # layer 2 of residual block
        y = gen_conv2d()(y)
        y = gen_norm()(y)
        y = relu(y)
        # combining
        x = Add()([y, x])
        x = gen_norm()(x)
        x = relu(x)

    p = gen_conv2d()(x)
    p = gen_norm()(p)
    p = relu(p)
    p = Conv2D(filters = 73, kernel_size = (3, 3), strides = 1, padding = 'same', data_format = 'channels_last', use_bias = False)(p) # not sure about kernel size, stride, bias, or batch normalization for this one
    p = Flatten(data_format = 'channels_last')(p)

    v = Conv2D(filters = 1, kernel_size=(1, 1), strides = 1, data_format = 'channels_last', use_bias = False)(x)
    v = gen_norm()(v)
    v = relu(v)
    v = Dense(units = 256, activation = 'relu', use_bias = False)(v)
    v = Flatten(data_format = 'channels_last')(v)
    v = Dense(units = 1, activation = 'tanh', use_bias = False)(v)

    model = Model(inputs = input_layer, outputs = [p,v])
    model.compile(optimizer = optimizer, loss = loss_fns, metrics = ['accuracy'], loss_weights = [0.5, 1])

    return model

def train_nnet(nnet, examples):
    new_nnet = tf.keras.models.clone_model(nnet)
    new_nnet.compile(optimizer = optimizer, loss = loss_fns, metrics = ['accuracy'], loss_weights = [0.5, 1])

    x_train, p_train, v_train = zip(*examples)
    new_nnet.fit(np.array(x_train), [np.array(p_train), np.array(v_train)], epochs = 500, verbose = 2)
    return new_nnet


##m = init_nnet()
##g = Game()
##inputs = g.get_nnet_inputs()
##new_inputs = np.array(inputs)
##new_inputs = new_inputs.reshape(1, board_height, board_width, num_channels)
##
##policy, value = m(new_inputs)
##
##print('og value')
##print(value[0])
##
##print(inputs[0].shape)
##print(policy[0].shape)
##print(value[0].shape)
##
##training_data = ((inputs, policy[0], value[0]), (inputs, policy[0], value[0]))
##m2 = train_nnet(m, training_data)
##
##policy, value = m2(new_inputs)
##print('val 2')
##print(value[0])
##











    
