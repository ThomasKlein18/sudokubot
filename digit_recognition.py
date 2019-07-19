import os
import numpy as np 
import tensorflow as tf 

mnist = tf.keras.datasets.mnist

(train_images, train_labels), (test_images, test_labels) = mnist.load_data()
train_images = train_images / 255.0
test_images = test_images / 255.0

model = tf.keras.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(128, activation=tf.nn.relu),
    tf.keras.layers.Dense(10, activation=tf.nn.softmax)
])

callback = tf.keras.callbacks.ModelCheckpoint(filepath="checkpoint.h5",
                                    #save_best_only=True,
                                    period=1)

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(train_images, train_labels, epochs=10, callbacks=[callback])

test_loss, test_acc = model.evaluate(test_images, test_labels)

print('Test accuracy:', test_acc)
