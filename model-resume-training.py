import snippets
import tensorflow as tf


print("Select the training material of the model:")
path = snippets.fileexplorer(True, False)
model = snippets.model_of_spec(path)


print("Select directory that holds the checkpoints:")
checkpoint_path = snippets.fileexplorer()

model.load_weights(checkpoint_path)