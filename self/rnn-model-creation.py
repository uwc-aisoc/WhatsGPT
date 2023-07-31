import tensorflow as tf
import numpy as np
import os
import time

import snippets

print("Select path to training text")
path = snippets.fileexplorer(True, "file")[0]
length = -1  # -1 means all of file
file = open(path, 'rb')
text = file.read(length).decode('utf-8')
vocab = sorted(set(text))

text_split = tf.strings.unicode_split(text,
                                      input_encoding='UTF-8')  # turns all of the text into split bytes as raggedtensor object
# e.g, tf.Tensor([b'I' b'\xe2\x80\x99' b'l' ... b'a' b's' b' '], shape=(4853,), dtype=string)
# print(type(text_split)) # ~ <class 'tensorflow.python.framework.ops.EagerTensor'>

# create layers that process EagerTensor types
char2id = tf.keras.layers.StringLookup(vocabulary=list(vocab), mask_token=None)
id2char = tf.keras.layers.StringLookup(vocabulary=char2id.get_vocabulary(), invert=True, mask_token=None)


def id2text(setofids):
    return tf.strings.reduce_join(id2char(setofids), axis=-1)


ids = char2id(text_split)  # assigns an id number to all the characters and replaces them according to vocab
# print(ids) # i.e, tf.Tensor([27 69 54 ... 43 61  2], shape=(4853,), dtype=int64)
idSet = tf.data.Dataset.from_tensor_slices(ids)  # forms the Tensor into a dataset that technically could be processed

sequenceLength = 100
sequenceSet = idSet.batch(sequenceLength + 1,
                          drop_remainder=True)  # makes set of datatype "tensorflow.python.data.ops.batch_op._BatchDataset". will refer to as tf.batchdataset from now on
# tf.batchdataset can be
numberOfSamples = sequenceSet.cardinality() # todo: this is a bug??? why does it only take 450?? commented and replaced future instances with sequenceSet for now
# sequences = sequenceSet.take(numberOfSamples)  # however many of the sequences of previously specified length you want


# print(type(sequences)) # ~ <class 'tensorflow.python.data.ops.take_op._TakeDataset'>
# tf.batchdataset can be split into type TakeDataset. https://www.tensorflow.org/api_docs/python/tf/data/Datase
# These behave like arrays in the sense that by using the for..in method,
# they get split into EagerTensors, which can be processes with char2id etc.


def split_input_target(sequence):
    input_text = sequence[:-1]
    target_text = sequence[1:]
    return input_text, target_text


# dataset=sequences

dataset = sequenceSet.map(split_input_target)  # map the sequences onto tuples (still datasets) with the input and target.
# the target is one offset from the input. i.e, hell, ello

# Batch size
BATCH_SIZE = 64

# Buffer size to shuffle the dataset
# (TF data is designed to work with possibly infinite sequences,
# so it doesn't attempt to shuffle the entire sequence in memory. Instead,
# it maintains a buffer in which it shuffles elements).


dataset = (
    dataset
        .shuffle(numberOfSamples)
        .batch(BATCH_SIZE, drop_remainder=False)  # dropping the remainder breaks the .unbatch() method
        .prefetch(tf.data.experimental.AUTOTUNE))  # prefetching helps load things faster

# this part just prints all input to training tensors
# for i,j in dataset.unbatch():
#     print(id2text(i),"\n",id2text((j)))


model = snippets.model_of_spec(path) # todo: There is a bit of redundancy here because it makes id2char etc. layers again.


print("test model")
for input_example_batch, target_example_batch in dataset.take(1):
    # print(input_example_batch,"\n",target_example_batch)
    example_batch_predictions = model(input_example_batch)
    print(example_batch_predictions.shape, "# (batch_size, sequence_length, vocab_size)")
    print(model.summary())

print("Test the output")

sampled_indices = tf.random.categorical(example_batch_predictions[0], num_samples=1)
sampled_indices = tf.squeeze(sampled_indices, axis=-1).numpy()
print("Input:\n", id2text(input_example_batch[0]).numpy())
print()
print("Next Char Predictions:\n", id2text(sampled_indices).numpy().decode('utf-8'))

# loss time
# loss is the function of certainty of the next thing
print("This is the result of the first pass:")
loss = tf.losses.SparseCategoricalCrossentropy(from_logits=True)

example_batch_mean_loss = loss(target_example_batch, example_batch_predictions)
print("Prediction shape: ", example_batch_predictions.shape, " # (batch_size, sequence_length, vocab_size)")
print("Mean loss:        ", example_batch_mean_loss.numpy())
print("Mean loss exp():  ", tf.exp(example_batch_mean_loss).numpy())  # this is e^loss

model.compile(optimizer='adam', loss=loss)

# Training time

# Directory where the checkpoints will be saved
checkpoint_dir = snippets.fileexplorer(False, "directory")
pathexists=checkpoint_dir[2]
if not pathexists:
    os.mkdir(checkpoint_dir[0])

# Name of the checkpoint files
checkpoint_prefix = os.path.join(checkpoint_dir[0], "ckpt_{epoch}")

checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_prefix,
    save_weights_only=True)

history = model.fit(dataset, epochs=4000, callbacks=[checkpoint_callback])  # specify number of epochs here
