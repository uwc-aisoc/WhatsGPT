import tensorflow as tf
import numpy
path= "Datasets/katya-final.txt"
length=5000
file=open(path, 'rb')
text=file.read(length).decode('utf-8')
vocab= sorted(set(text))

def id2text(ids):
  return tf.strings.reduce_join(id2char(ids), axis=-1)

text_split = tf.strings.unicode_split(text, input_encoding='UTF-8') # turns all of the text into split bytes as raggedtensor object
# e.g, tf.Tensor([b'I' b'\xe2\x80\x99' b'l' ... b'a' b's' b' '], shape=(4853,), dtype=string)
print(text_split)

# create layers
char2id=tf.keras.layers.StringLookup(vocabulary=list(vocab), mask_token=None)
id2char=tf.keras.layers.StringLookup(vocabulary=char2id.get_vocabulary(), invert=True, mask_token=None)

ids=char2id(text_split) #assigns an id number to all the characters and replaces them according to vocab
print(ids) # i.e, tf.Tensor([27 69 54 ... 43 61  2], shape=(4853,), dtype=int64)
idSet=tf.data.Dataset.from_tensor_slices(ids) # forms the Tensor into a dataset that technically could be processed

sequenceLength=100
sequenceSet=idSet.batch(sequenceLength+1,drop_remainder=True) # makes sequenceSet that can

