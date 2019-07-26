import math 
import os
import cv2

import numpy as np 
import tensorflow as tf
import matplotlib.pyplot as plt

from skimage.measure import label as label_func
from skimage.measure import regionprops
from skimage.transform import hough_line, hough_line_peaks
from scipy.signal import convolve2d as convolve2d
from scipy.ndimage import sobel, rotate, gaussian_filter
from scipy.ndimage.morphology import binary_erosion, binary_opening
from PIL import Image, ExifTags
from scipy import fftpack

from sudoku_solve import print_sudoku, solve_dancinglinks

model = tf.keras.models.load_model("checkpoint.h5")


def parse_photo(filename):
    """
    Transforms a (potentially skewed) image of a sudoku into the integer matrix that will represent it.

    returns: matrix of integers
    """

    # step 1: read image (rotate if necessary)
    img = Image.open(filename)
    if( not img._getexif() is None):
        exif = { ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS }
        if exif["Orientation"] == 8:
            img = rotate(img, 90, reshape=True, mode="constant", cval=255)

    img = np.array(img, dtype=np.int)

    # step 2: binarize
    bin_img = np.sum(img, axis=2) 
    bin_img = np.invert(bin_img > np.mean(bin_img))

    sobel_vert = sobel(bin_img, 1) # obtain vertical edges
    sobel_hori = sobel(bin_img, 0) # obtain horizontal edges
    sobel_img = sobel_vert + sobel_hori

    # step 3: find largest connected region = sudoku
    labelled = label_func(sobel_img)
    props = regionprops(labelled)
    maxval = 0
    sudoku_patch = None
    for prop in props:
        minrow, mincol, maxrow, maxcol = prop.bbox
        area = (maxrow-minrow)*(maxcol-mincol)
        if area > maxval:
            maxval = area 
            sudoku_patch = prop

    minrow, mincol, maxrow, maxcol = sudoku_patch.bbox
    margin = 0
    img = img[minrow-margin:maxrow+margin, mincol-margin:maxcol+margin]

    # step 4: find angle and rotate image by that angle
    h_space, angles, dist = hough_line(sobel_vert)
    h_space, angles, dist = hough_line_peaks(h_space, angles, dist, num_peaks=1)
    angle = math.degrees(angles[0])
    
    img = rotate(img, angle, reshape=False, mode="constant", cval=255)

    # step 5: divide the image into 81 smaller images
    height, width, colors = img.shape
    h_step = int(height/9)
    w_step = int(width/9)
    tiles = [(img[h_step*i:h_step*i+h_step,w_step*j:w_step*j+w_step], i, j) for i in range(9) for j in range(9)]

    # step 6: use ANN to recognize digits
    sudoku = np.zeros((9,9))
    global model
        
    for tile, i, j in tiles:

        m,n,_ = tile.shape

        tile = np.sum(tile, axis=2) 
        tile = np.invert(tile > np.mean(tile)*0.7).astype(int)

        for k in range(m):
            if np.sum(tile[k,:]) > 0.6*m:
                tile[k,:] = 0
        for k in range(n):
            if np.sum(tile[:,k]) > 0.6*n:
                tile[:,k] = 0
        #opened_tile = tile
        opened_tile = binary_opening(tile, np.ones((3,3))).astype(int)

        if np.sum(opened_tile) / (opened_tile.shape[0]*opened_tile.shape[1]) > 0.01:

            # find center of gravity of number
            props = regionprops(opened_tile)
            maxval = 0
            number_patch = None
            for prop in props:
                if prop.area > maxval:
                    maxval = prop.area 
                    number_patch = prop
            minrow, mincol, maxrow, maxcol = number_patch.bbox
            margin = 4
            
            # pad image with zeros to make it more MNIST-like
            tile = np.pad(tile[minrow:maxrow, mincol:maxcol], [[margin,margin],[2*margin,2*margin]], mode="constant")
            
            tile = cv2.resize(tile.astype(np.uint8), dsize=(28, 28), interpolation=cv2.INTER_CUBIC)
    
            predictions = model.predict(np.reshape(tile, [1,28,28,1]))[0]
            label = np.argmax(predictions)

            sudoku[i,j] = label

    return sudoku.astype(np.uint8)


def sudoku_to_image(sudoku):
    res = np.zeros((28*9,28*9))
    for i in range(9):
        for j in range(9):
            num = sudoku[i,j]
            pic = plt.imread(os.path.join("numbers",str(num)+".png"))
            pic = np.sum(pic, axis=2)
            res[28*i:28*i+28,28*j:28*j+28] = pic

    for i in range(9):
        for j in range(9):
            if j != 0:
                res[:,j*28] = np.max(res)
        if i != 0:
            res[i*28,:] = np.max(res)

    return res

if __name__ == "__main__":
    s = parse_photo("sudoku_imgs/f.jpg")
    s = solve_dancinglinks(s)
    sudoku_to_image(s)