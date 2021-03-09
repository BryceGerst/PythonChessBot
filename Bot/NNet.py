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

        # input layer
        self.input_layer = Conv2D(input_shape = (board_height, board_width, num_channels), filters = 256, kernel_size=(3, 3), strides = 1, padding = 'same', data_format = 'channels_last', use_bias = False)
        self.input_norm = self.gen_norm()

        # residual tower
        self.first_layers = []
        self.second_layers = []
        self.first_norm_layers = []
        self.second_norm_layers = []
        self.third_norm_layers = []
        self.fourth_norm_layers = []
        for _ in range(19):
            self.first_layers.append(self.gen_conv2d())
            self.first_norm_layers.append(self.gen_norm())
            self.second_layers.append(self.gen_conv2d())
            self.second_norm_layers.append(self.gen_norm())
            self.third_norm_layers.append(self.gen_norm())
            self.fourth_norm_layers.append(self.gen_norm())

        # policy head
        self.policy_one = self.gen_conv2d()
        self.policy_one_norm = self.gen_norm()
        self.policy_two = Conv2D(filters = 73, kernel_size = (3, 3), strides = 1, padding = 'same', data_format = 'channels_last', use_bias = False) # not sure about kernel size, stride, bias, or batch normalization for this one
        self.policy_three = Flatten(data_format = 'channels_last')

        # value head
        self.value_one = Conv2D(filters = 1, kernel_size=(1, 1), strides = 1, data_format = 'channels_last', use_bias = False)
        self.value_one_norm = self.gen_norm()
        self.value_two = Dense(units = 256, activation = 'relu', use_bias = False)
        self.value_three = Flatten(data_format = 'channels_last')
        self.value_four = Dense(units = 1, activation = 'tanh', use_bias = False)

        self.final_concat = tf.keras.layers.Concatenate(axis = -1)

    def gen_conv2d(self):
        return Conv2D(filters = 256, kernel_size=(3, 3), strides = 1, padding = 'same', data_format = 'channels_last', use_bias = False)

    def gen_norm(self):
        return BatchNormalization(axis = -1)

    def call(self, x):
        x = self.input_layer(x)
        x = self.input_norm(x)
        x = relu(x)

        # residual tower
        for i in range(19):
            x_skip = x
            x = self.first_layers[i](x)
            x = self.first_norm_layers[i](x)
            x = relu(x)
            x = self.second_layers[i](x)
            x = self.second_norm_layers[i](x)
            x_skip = self.second_layers[i](x_skip)
            x_skip = self.third_norm_layers[i](x_skip)
            x = (x + x_skip)
            x = self.fourth_norm_layers[i](x)
            

        # output 1
        policy = self.policy_one(x)
        policy = self.policy_one_norm(policy)
        policy = relu(policy)
        policy = self.policy_two(policy)
        policy = self.policy_three(policy)

        # output 2
        value = self.value_one(x)
        value = self.value_one_norm(value)
        value = relu(value)
        value = self.value_two(value)
        value = self.value_three(value)
        value = self.value_four(value)

        #result = self.final_concat([policy, value])
        
        return policy, value#result

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
        inputs, targets = data

        with tf.GradientTape() as tape:
            outputs = self(inputs, training = True)
            loss = self.compiled_loss(targets, outputs)
            #losses = [l(t, o) for l, o, t in zip(self.loss_objects, outputs, targets)]

        gradients = tape.gradient(loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))
        self.compiled_metrics.update_state(outputs, targets)
        return {m.name: m.result() for m in self.metrics}


    # https://stackoverflow.com/questions/59690188/how-do-i-make-a-multi-output-tensorflow-2-neural-network-for-both-regression-and
    # ^^^ this is a thing worth looking at some point


am = AlphaModel()
# categorical cross entropy is the loss function for the policy
# mean squared error is the loss function for the value
loss_objects = [tf.keras.losses.CategoricalCrossentropy(from_logits = False), tf.keras.losses.MeanSquaredError()]
opt = tf.keras.optimizers.Adam(learning_rate = 0.02)
am.compile(optimizer = opt, metrics = ['accuracy'], loss = loss_objects)




g = Game()
inputs = g.get_nnet_inputs()
new_inputs = np.array(inputs)
#print(new_inputs)
new_inputs = new_inputs.reshape(1, board_height, board_width, num_channels)
#print(new_inputs.shape)
#print(new_inputs)
result = am(new_inputs)
#print(result.shape)
#am.summary()
#print(am.optimizer)
#print(am.compiled_metrics)
x_data = (inputs, inputs)
x_data = np.array(x_data)
print(x_data.shape)
#y_data = ((p, v), (p, v))
y_data = ([result[0][0], result[1][0]], [result[0][0], result[1][0]])
#y_data = np.array(y_data)
#print(y_data.shape)


#result = am(x_data)

am.fit(x = x_data, y = y_data)




