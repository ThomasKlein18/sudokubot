import os
import numpy as np 
import tensorflow as tf 

import matplotlib.pyplot as plt

def get_dataset_from_folder(folder):

    imgs = []
    labels = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            print(file)
            if file[-4:] == ".png":
                labels.append(int(file.split("_")[0]))
                img = plt.imread(os.path.join(folder,file))
                img = np.sum(img, axis=2)
                img = img / np.max(img)
                print(np.max(img))
                imgs.append(img)

    return np.reshape(np.array(imgs), [len(imgs),28,28,1]), np.array(labels)
    

mnist = tf.keras.datasets.mnist
real_imgs, real_labels = get_dataset_from_folder("train_images")

(train_images, train_labels), (test_images, test_labels) = mnist.load_data()
train_images = train_images / 255.0
test_images = test_images / 255.0

train_images = np.reshape(train_images, [train_images.shape[0], 28, 28, 1])
test_images = np.reshape(test_images, [test_images.shape[0], 28, 28, 1])


callback = tf.keras.callbacks.ModelCheckpoint(filepath="checkpoint.h5",
                                        #save_best_only=True,
                                        period=1)

starting_cold = False

if(starting_cold):
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(filters=32, kernel_size=3, activation=tf.nn.relu, input_shape=[28,28,1]),
        tf.keras.layers.Conv2D(filters=64, kernel_size=3, activation=tf.nn.relu),
        tf.keras.layers.MaxPool2D(),
        tf.keras.layers.Dropout(0.25),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation=tf.nn.relu),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(10, activation=tf.nn.softmax)
    ])

    model.compile(optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy'])

    model.fit(train_images, train_labels, epochs=12, callbacks=[callback])

    test_loss, test_acc = model.evaluate(test_images, test_labels)

    print('Test accuracy:', test_acc)

else:

    model = tf.keras.models.load_model("checkpoint.h5")
    model.fit(real_imgs, real_labels, epochs=5, callbacks=[callback])

