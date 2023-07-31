import snippets
import tensorflow as tf
import os

# print("Select the training material of the model:")
# path = snippets.fileexplorer(True, "file")[0]

path='./Datasets/fam-final-christina.txt'

model = snippets.model_of_spec(path)


# print("Select directory that holds the checkpoints:")
# checkpoint_path = snippets.fileexplorer(True, "directory")[0]
checkpoint_path = './checkpoints/family-gc/run_mum/'

checkpoint_path = snippets.ckpt(checkpoint_path)

model.load_weights(checkpoint_path)

loss = tf.losses.SparseCategoricalCrossentropy(from_logits=True)
model.compile(optimizer='adam',loss=loss)


checkpoint_dir = ["./checkpoints/family-gc/run_test"]
checkpoint_prefix = os.path.join(checkpoint_dir[0], "ckpt_{epoch}")

checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_prefix,
    save_weights_only=True)

history = model.fit(dataset, epochs=4000, callbacks=[checkpoint_callback])  # specify number of epochs here
