#This is generative RSS training
import tensorflow as tf
path="./Datasets/Katya Swaminathan Censored.txt"
text=open(path, 'rt').read() #this line ignores the guidelines to encode then decode by forcing 'b' mode as opposed to 't' and then decoding it
#print(text) #rw test
vocab= sorted(set(text))
print(f'the number of unique characters in the whatsapp text messages is: {len(vocab)}')
example_texts = ["hello there", "what da dog doin' 👍", "abcdefgh"]
print('these are the example texts:',example_texts)
chars = tf.strings.unicode_split(example_texts, input_encoding='UTF-8')
print('split unicode:',chars)
layer=tf.keras.layers.StringLookup(vocabulary=list(vocab), mask_token=None) #known as 'id_from_chars' in the tf web
print('numeric IDs from StringLookup layer:',layer(chars))

def text_from_ids(ids): #this function turns a bunch of chars as a text from the array of ids
  return tf.strings.reduce_join(layer(ids), axis=-1)