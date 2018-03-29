from PIL import Image
from PIL import ImageChops
import math
import operator


# image_np1, image_np2 is numpy format 
def diffByHistogram(image_np1,image_np2,size=(9,8)):
    image1 = Image.fromarray(image_np1.astype('uint8'), 'RGB').resize(size).convert('L')
    image2 = Image.fromarray(image_np2.astype('uint8'), 'RGB').resize(size).convert('L')
    h = ImageChops.difference(image1, image2).histogram()
    return math.sqrt((float)(reduce(operator.add, map(lambda h, i: h*(i**2), h,range(len(h)))))/(float)(size[0]*size[1]))
