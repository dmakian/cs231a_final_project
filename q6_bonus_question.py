import gym
import random
from utils.preprocess import greyscale
from utils.wrappers import PreproWrapper, MaxAndSkipEnv
import numpy as np
import tensorflow as tf
import tensorflow.contrib.layers as layers

from utils.general import get_logger
from utils.test_env import EnvTest
from q1_schedule import LinearExploration, LinearSchedule
from q2_linear import Linear

from configs.q6_bonus_question import config


class MyDQN(Linear):
    """
    Going beyond - implement your own Deep Q Network to find the perfect
    balance between depth, complexity, number of parameters, etc.
    You can change the way the q-values are computed, the exploration
    strategy, or the learning rate schedule. You can also create your own
    wrapper of environment and transform your input to something that you
    think we'll help to solve the task. Ideally, your network would run faster
    than DeepMind's and achieve similar performance!

    You can also change the optimizer (by overriding the functions defined
    in TFLinear), or even change the sampling strategy from the replay buffer.

    If you prefer not to build on the current architecture, you're welcome to
    write your own code.

    You may also try more recent approaches, like double Q learning
    (see https://arxiv.org/pdf/1509.06461.pdf) or dueling networks
    (see https://arxiv.org/abs/1511.06581), but this would be for extra
    extra bonus points.
    """
    def get_q_values_op(self, state, scope, reuse=False):
        """
        Returns Q values for all actions

        Args:
            state: (tf tensor)
                shape = (batch_size, img height, img width, nchannels)
            scope: (string) scope name, that specifies if target network or not
            reuse: (bool) reuse of variables in the scope

        Returns:
            out: (tf tensor) of shape = (batch_size, num_actions)
        """
        # this information might be useful
        num_actions = self.env.action_space.n
        out = state
        ##############################################################
        """
        TODO: implement the computation of Q values like in the paper
                    https://www.cs.toronto.edu/~vmnih/docs/dqn.pdf

        HINT: you may find tensorflow.contrib.layers useful (imported)
              make sure to understand the use of the scope param

              you can use any other methods from tensorflow
              you are not allowed to import extra packages (like keras,
              lasagne, cafe, etc.)
        """
        ##############################################################
        ################ YOUR CODE HERE - 10-15 lines ################

        with tf.variable_scope(scope) as sc:
            if reuse:
                sc.reuse_variables()
            conv1 = tf.layers.conv2d(inputs=state,
                                    filters=32,
                                    kernel_size=[8, 8],
                                    activation=tf.nn.relu,
                                    strides=2)
            conv2 = tf.layers.conv2d(inputs=conv1,
                                    filters=64,
                                    kernel_size=[4,4],
                                    activation=tf.nn.relu,
                                    strides=2)
            conv3 = tf.layers.conv2d(inputs=conv2,
                                    filters=64,
                                    kernel_size=[3,3],
                                    activation=tf.nn.relu,
                                    strides=1)
            # outshape = tf.shape(conv3)
            print conv3.get_shape()
            flattened_filters = tf.reshape(conv3, [-1, 15*15*64])
            # print flattened_filters.get_shape()
            hiddenV = tf.layers.dense(inputs=flattened_filters,units=256, activation=tf.nn.relu)
            hiddenA = tf.layers.dense(inputs=flattened_filters,units=256, activation=tf.nn.relu)
            if scope == 'q':
                self.conv = []
                self.conv.append(conv1)
                self.conv.append(conv2)
                self.conv.append(conv3)
                self.conv_out = flattened_filters
                self.hiddenA = hiddenA
                self.hiddenV = hiddenV

            Wa =  tf.get_variable("weights_a", (256,num_actions))
            ba = tf.get_variable("biases_a", (num_actions))
            A = tf.matmul(hiddenA,Wa)+ba

            Wv =  tf.get_variable("weights_v", (256,1))
            bv = tf.get_variable("biases_v", (1))
            V = tf.matmul(hiddenV,Wv)+bv
            q = V+(A -tf.reduce_mean(A, reduction_indices=1, keep_dims=True))
            # print out.get_shape()

        ##############################################################
        ######################## END YOUR CODE #######################
        return q

"""
Use a different architecture for the Atari game. Please report the final result.
Feel free to change the configuration. If so, please report your hyperparameters.
"""
if __name__ == '__main__':
    # make env
    env = gym.make(config.env_name)
    env = MaxAndSkipEnv(env, skip=config.skip_frame)
    env = PreproWrapper(env, prepro=greyscale, shape=(80, 80, 1),
                        overwrite_render=config.overwrite_render)

    # exploration strategy
    # you may want to modify this schedule
    exp_schedule = LinearExploration(env, config.eps_begin,
            config.eps_end, config.eps_nsteps)

    # you may want to modify this schedule
    # learning rate schedule
    lr_schedule  = LinearSchedule(config.lr_begin, config.lr_end,
            config.lr_nsteps)

    # train model
    model = MyDQN(env, config)
    model.run(exp_schedule, lr_schedule)