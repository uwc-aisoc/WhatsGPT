import tensorflow as tf
import time
import os


# -------------tf stuff ------------- #


# ----------------------------------- #
# spec: 256 dim units, 1024 rnn units #
# ----------------------------------- #
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
        def __init__(self, vocab_size, embedding_dim, rnn_units):
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


def ckpt(path) -> str:  # takes the directory and returns the latest checkpoint identifier (i.e ckpt_14)
    lscurdir = os.listdir(path)
    highest = 0
    for i in range(len(lscurdir) - 1, -1,
                   -1):  # this looks really cursed but it decrements by 1 from the last element to the first.
        if "data" in lscurdir[i] or "checkpoint" == lscurdir[i]:
            lscurdir.pop(i)  # lscurdir.pop() [being without an argument] should work too
        else:
            lscurdir[i] = os.path.splitext(lscurdir[i])[0]  # remove extension
            print(lscurdir[i])
            curno = int(lscurdir[i][5:])  # "ckpt_" --> 5 characters
            if curno > highest:
                highest = curno
    return path + "ckpt_" + str(highest)  # no need for / as directory is being passed


# -------------general------------- #


# ---------------------------------------------------- #
# Dependents: all Datasets/format/ programs            #
# Dependencies: none                                   #
# Returns a boolean depending on user response         #
# ---------------------------------------------------- #


def yesNo(prompt) -> bool:
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
# Inputs: fileMustExist, forcetype                     #
#    forcetype accepts "file", "directory", forces the #
#    user to enter the type
# Outputs: [path, type]                                #
#    type is either "file" or "directory"              #
# ---------------------------------------------------- #


def fileexplorer(fileMustExist=False, forcetype="none") -> list[str]:
    print(f"Selected file must exist?: {fileMustExist}")
    print(f"Force type: {forcetype}")
    # leave creation of directory or file to calling instance
    while True:
        print(f"Current directory: {os.getcwd()}\nDirectory contents:\n{os.listdir()}\n.. and . are accepted")
        cwdpath: str = input("Select file or directory: ")
        if os.path.isdir(cwdpath):
            if forcetype not in ["file", "directory"]:
                if yesNo(
                        "Do you wish to select this directory? If not, this program will change directories instead"):
                    return [os.getcwd() + "/" + cwdpath, "directory"]
                else:
                    print(f">cd {cwdpath}")
                    os.chdir(cwdpath)
            elif forcetype == "file":
                print(f"This is a directory. Please try again and select a {forcetype}")
            else: # must be directory
                return [os.getcwd() + "/" + cwdpath, "directory"]
        elif os.path.isfile(cwdpath):  # includes symlinks :o
            if forcetype not in ["file", "directory"]:
                if yesNo(f"Confirm: {cwdpath}"):
                    return [os.getcwd() + "/" + cwdpath, "file"]
                else:
                    print("Cancelled, reenter:")
            elif forcetype == "directory":
                print(f"This is a file. Please try again and select a {forcetype}")
            else:
                return [os.getcwd() + "/" + cwdpath, "file"]
        elif not fileMustExist:
            if yesNo(
                    f"You are attempting to return a path that does not exist. Confirm: {cwdpath}"):
                if forcetype == "file":
                    return [os.getcwd() + "/" + cwdpath, "file"]
                elif forcetype == "directory":
                    return [os.getcwd() + "/" + cwdpath, "directory"]
                else:
                    if yesNo("Return a file? If not, the program will return a directory."):
                        return [os.getcwd() + "/" + cwdpath, "file"]
                    else:
                        return [os.getcwd() + "/" + cwdpath, "directory"]
            else:
                print("Cancelled, reenter:")
        else:
            print("The path does not exist. Please try again.")
