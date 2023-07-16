import tensorflow as ts
path= "Datasets/katya whatsapp log.txt"
text=open(path, 'rt').read() #text not binary
vocab= sorted(set(text))

id2char=tf.keras.layers.StringLookup(vocabulary=list(vocab), mask_token=None)
char2id=tf.keras.layers.StringLookup(vocabulary=id2char.get_vocabulary(), invert=True, mask_token=None)

chars = tf.strings.unicode_split(example_texts, input_encoding='UTF-8')