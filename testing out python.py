#This is generative RSS training
import tensorflow as tf
path= "Datasets/katya whatsapp log.txt"

rank_2_tensor = tf.constant([[1, 2],
                             [3, 4],
                             [5, 6]], dtype=tf.float16)
print(rank_2_tensor)