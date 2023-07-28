import tensorflow as tf
import time
import os

# -------------tf stuff ------------- #

def model_of_spec(path_to_training_text, length=-1):
    file = open(path_to_training_text, 'rb')
    text = file.read(length).decode('utf-8')
    vocab = sorted(set(text))

    char2id = tf.keras.layers.StringLookup(vocabulary=list(vocab), mask_token=None)
    id2char = tf.keras.layers.StringLookup(vocabulary=char2id.get_vocabulary(), invert=True, mask_token=None)

    # length of the vocabulary in StringLookup Layer
    vocab_size = len(char2id.get_vocabulary())
    print("The vocab size is", vocab_size)

    # make the dimensions for da embedding and gru layers
    embedding_dim = 256
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
    return MyModel(
        vocab_size=vocab_size,
        embedding_dim=embedding_dim,
        rnn_units=rnn_units)


def one_step_model(path_to_training_text, model, length=-1, ):
    file = open(path_to_training_text, 'rb')
    text = file.read(length).decode('utf-8')
    vocab = sorted(set(text))

    char2id = tf.keras.layers.StringLookup(vocabulary=list(vocab), mask_token=None)
    id2char = tf.keras.layers.StringLookup(vocabulary=char2id.get_vocabulary(), invert=True, mask_token=None)

    class OneStep(tf.keras.Model):
        def __init__(self, model, chars_from_ids, ids_from_chars, temperature=1.0):
            super().__init__()
            self.temperature = temperature
            self.model = model
            self.chars_from_ids = chars_from_ids
            self.ids_from_chars = ids_from_chars

            # Create a mask to prevent "[UNK]" from being generated.
            skip_ids = self.ids_from_chars(['[UNK]'])[:, None]
            sparse_mask = tf.SparseTensor(
                # Put a -inf at each bad index.
                values=[-float('inf')] * len(skip_ids),
                indices=skip_ids,
                # Match the shape to the vocabulary
                dense_shape=[len(ids_from_chars.get_vocabulary())])
            self.prediction_mask = tf.sparse.to_dense(sparse_mask)

        @tf.function
        def generate_one_step(self, inputs, states=None):
            # Convert strings to token IDs.
            input_chars = tf.strings.unicode_split(inputs, 'UTF-8')
            input_ids = self.ids_from_chars(input_chars).to_tensor()

            # Run the model.
            # predicted_logits.shape is [batch, char, next_char_logits]
            predicted_logits, states = self.model(inputs=input_ids, states=states,
                                                  return_state=True)
            # Only use the last prediction.
            predicted_logits = predicted_logits[:, -1, :]
            predicted_logits = predicted_logits / self.temperature
            # Apply the prediction mask: prevent "[UNK]" from being generated.
            predicted_logits = predicted_logits + self.prediction_mask

            # Sample the output logits to generate token IDs.
            predicted_ids = tf.random.categorical(predicted_logits, num_samples=1)
            predicted_ids = tf.squeeze(predicted_ids, axis=-1)

            # Convert from token ids to characters
            predicted_chars = self.chars_from_ids(predicted_ids)

            # Return the characters and model state.
            return predicted_chars, states

    return OneStep(model, id2char, char2id)  # substitute this line with mapping functions


# -------------general------------- #


# ---------------------------------------------------- #
# Dependents: all Datasets/format/ programs            #
# Dependencies: none                                   #
# ---------------------------------------------------- #


def yesNo(prompt):
    response = ""
    yes = ['y', 'Y']
    no = ['n', 'N']
    while response not in yes and response not in no:
        response = input(str(prompt) + " (y/n): ")
        if response in yes:
            return True
        elif response in no:
            return False
        else:
            print(f"Response \'{response}\' not valid, try again: ")


# ---------------------------------------------------- #
# Dependents: all Datasets/format/ programs            #
# Dependencies: os, yesNo.py                           #
# ---------------------------------------------------- #




def fileexplorer(fileMustExist=False, directoriesSelectable=False):
    print(f"Selected file must exist?: {fileMustExist}")
    print(f"Directories are selectable?: {directoriesSelectable}")
    print("Note: This program cannot create directories.")  # todo: allow creation of directories
    while True:
        cwdpath = ""
        print(f"Current directory: {os.getcwd()}\nDirectory contents:\n{os.listdir()}\n.. and . are accepted")
        cwdpath: str = input("Select file or directory: ")
        if os.path.isdir(cwdpath):
            if directoriesSelectable and yesNo(
                    "Do you wish to select this directory? If not, this program will change directories instead"):
                return os.getcwd() + "/" + cwdpath + "/"
            print(f">cd {cwdpath}")
            os.chdir(cwdpath)
        elif os.path.isfile(cwdpath):
            if yesNo(f"Confirm: {cwdpath}"):
                return os.getcwd() + "/" + cwdpath
            else:
                print("Cancelled, reenter:")
        elif not fileMustExist:
            if yesNo(
                    f"You are attempting to return a FILE that does not exist. This likely means that the program will create it instead.\nConfirm: {cwdpath}"):
                return os.getcwd() + "/" + cwdpath
            else:
                print("Cancelled, reenter:")
        else:
            print("The path does not exist. Please try again.")

