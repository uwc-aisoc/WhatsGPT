import snippets
import tensorflow as tf


print("Select the training material of the model:")
path = snippets.fileexplorer(True, "file")[0]
model = snippets.model_of_spec(path)


print("Select directory that holds the checkpoints:")
checkpoint_path = snippets.fileexplorer(True, "directory")[0]

checkpoint_path = snippets.ckpt(checkpoint_path)

model.load_weights(checkpoint_path)