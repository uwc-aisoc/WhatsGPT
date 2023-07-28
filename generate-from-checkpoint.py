import tensorflow as tf
import os
import time

import module_tf
import module_general

print("Select the training material of the model:")
path = module_general.fileexplorer(True, False)
model = module_tf.model_of_spec(path)

# time to load shit lmfao

print("Select directory that holds the checkpoints:")
checkpoint_path = module_general.fileexplorer()

model.load_weights(checkpoint_path)

# Copy paste from generative_rnn the onestep model


one_step_model = module_tf.one_step_model(path, model)

start = time.time()
states = None
prompt: str = input("Prompt the model: ")
next_char = tf.constant([prompt])
result = [next_char]

response = input("Input the -number- of characters to generate: ")

for n in range(int(response)):  # change this value however
    next_char, states = one_step_model.generate_one_step(next_char, states=states)
    result.append(next_char)

result = tf.strings.join(result)
end = time.time()
print(result[0].numpy().decode('utf-8'), '\n\n' + '_' * 80)
print('\nRun time:', end - start)
