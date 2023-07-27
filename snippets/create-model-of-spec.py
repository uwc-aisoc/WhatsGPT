import tensorflow as tf




def create_model_of_spec(path,length=-1):
    file = open(path, 'rb')
    text = file.read(length).decode('utf-8')
    vocab = sorted(set(text))

    char2id = tf.keras.layers.StringLookup(vocabulary=list(vocab), mask_token=None)
    id2char = tf.keras.layers.StringLookup(vocabulary=char2id.get_vocabulary(), invert=True, mask_token=None)

    # Length of the vocabulary in StringLookup Layer
    vocab_size = len(char2id.get_vocabulary())
    print("The vocab size is", vocab_size)
    # The embedding dimension
    embedding_dim = 256

    # Number of RNN units
    rnn_units = 1024

    class MyModel(tf.keras.Model):
        def __init__(self, vocab_size, embedding_dim, rnn_units) -> object:
            super().__init__(self)
            self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)
            self.gru = tf.keras.layers.GRU(rnn_units,
                                           return_sequences=True,
                                           return_state=True)
            self.dense = tf.keras.layers.Dense(vocab_size)

        def call(self, inputs, states=None, return_state=False, training=False):
            x = inputs
            x = self.embedding(x, training=training)
            if states is None:
                states = self.gru.get_initial_state(x)
            x, states = self.gru(x, initial_state=states, training=training)
            x = self.dense(x, training=training)

            if return_state:
                return x, states
            else:
                return x

    # print("init model")
    model = MyModel(
        vocab_size=vocab_size,
        embedding_dim=embedding_dim,
        rnn_units=rnn_units)
    return model
