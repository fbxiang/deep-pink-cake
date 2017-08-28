import tensorflow as tf
import numpy as np
import osu


def _weight_and_bias(in_size, out_size):
    weight = tf.truncated_normal([in_size, out_size])
    bias = tf.constant(0, dtype=tf.float32, shape=[out_size])
    return tf.Variable(weight, name='weight'), tf.Variable(bias, name='bias')


class OSUModel:

    def __init__(self, lstm_state_size=200, n_lstm_layers=3, target_size=2):
        self.lstm_state_size = lstm_state_size
        self.n_lstm_layers = n_lstm_layers

        self.target_size = target_size
        self.lstm = tf.nn.rnn_cell.MultiRNNCell([tf.nn.rnn_cell.BasicLSTMCell(self.lstm_state_size) for i in range(self.n_lstm_layers)])
        self.weight, self.bias = _weight_and_bias(self.lstm_state_size, target_size)

    def _create_lstm_layers(self, input_batch):
        """
        create LSTM layers over the input batch

          input_batch: input of shape [batch_size, time, feature_size]
        """
        outputs, state = tf.nn.dynamic_rnn(self.lstm, input_batch, dtype=tf.float32)
        return outputs

    def prediction(self, input_batch):
        lstm_output = self._create_lstm_layers(input_batch)
        flat_lstm_output = tf.reshape(lstm_output, [-1, self.lstm_state_size])

        flat_prediction = tf.nn.softmax(tf.matmul(flat_lstm_output, self.weight) + self.bias)
        prediction = tf.reshape(flat_prediction, [-1, tf.shape(input_batch)[1], self.target_size])
        return prediction

    def loss(self, input_batch, target):
        prediction = self.prediction(input_batch)
        flat_prediction = tf.reshape(prediction, [-1, tf.shape(target)[2]])
        flat_target = tf.reshape(target, [-1, tf.shape(target)[2]])
        return tf.reduce_mean(-tf.reduce_sum(flat_target * tf.log(flat_prediction), axis=1))

    def optimize(self, input_batch, target):
        loss = self.loss(input_batch, target)
        optimizer = tf.train.AdamOptimizer()
        return optimizer.minimize(loss)


from osu import OSUData

print('Reading data...')
data = OSUData()
data.read_osu('./sample.osu')
data.read_music('./sample.wav')
label, data = data.encode_stft_one_hot()
data = data.reshape([1, data.shape[0], data.shape[1]])
label = label.reshape([1, label.shape[0], label.shape[1]])

session = tf.Session(config=tf.ConfigProto(log_device_placement=True))

print('Building model...')
model = OSUModel()
input_batch = tf.placeholder(tf.float32, [None, None, 1025], name="input")
target_batch = tf.placeholder(tf.float32, [None, None, 2], name="target")
optimize = model.optimize(input_batch, target_batch)
loss = model.loss(input_batch, target_batch)

print('Initializing variables...')
init = tf.global_variables_initializer()
session.run(init)

print('Training...')

for i in range(100):
    loss_value, optimize_value = session.run([loss, optimize], feed_dict={ input_batch: data, target_batch: label })
    print(i, loss_value, optimize_value)
