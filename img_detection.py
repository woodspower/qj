
# coding: utf-8

# # Object Detection Demo
# Welcome to the object detection inference walkthrough!  This notebook will walk you step by step through the process of using a pre-trained model to detect objects in an image. Make sure to follow the [installation instructions](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/installation.md) before you start.

# # Imports

# In[19]:


import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import logging
import time
logging.basicConfig(filename='command.log', level=logging.DEBUG)

from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

if tf.__version__ < '1.4.0':
  raise ImportError('Please upgrade your tensorflow installation to v1.4.* or later!')


# ## Env setup

# In[20]:


# This is needed to display the images.
# get_ipython().run_line_magic('matplotlib', 'inline')

# This is needed since the notebook is stored in the object_detection folder.
# sys.path.append("..")


# ## Object detection imports
# Here are the imports from the object detection module.

# In[21]:


from utils import label_map_util

from utils import visualization_utils as vis_util


# # Model preparation 

# ## Variables
# 
# Any model exported using the `export_inference_graph.py` tool can be loaded here simply by changing `PATH_TO_CKPT` to point to a new .pb file.  
# 
# By default we use an "SSD with Mobilenet" model here. See the [detection model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) for a list of other models that can be run out-of-the-box with varying speeds and accuracies.

# In[22]:


# What model to download.
MODEL_PATH_PREFIX = '/home/leo/qj/object_detection'
MODEL_PATH        = os.path.join(MODEL_PATH_PREFIX, 'frcnn_inference_graph')
LABEL_PATH        = os.path.join(MODEL_PATH_PREFIX, 'data')


# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = os.path.join(MODEL_PATH, 'frozen_inference_graph.pb')

# List of the strings that is used to add correct label for each box.
PATH_TO_LABEL = os.path.join(LABEL_PATH, 'pascal_label_map.pbtxt')

NUM_CLASSES = 117


# ## Download Model

# ## Load a (frozen) Tensorflow model into memory.

# In[23]:


detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')


# ## Loading label map
# Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine

# In[24]:


label_map = label_map_util.load_labelmap(PATH_TO_LABEL)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)


# ## Helper code

# In[25]:


def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)


# # Detection

# In[26]:

# with detection_graph.as_default():
qj_sess = tf.Session(graph=detection_graph)
# Definite input and output Tensors for detection_graph
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
# Each box represents a part of the image where a particular object was detected.
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
# Each score represent how level of confidence for each of the objects.
# Score is shown on the result image, together with the class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
num_detections = detection_graph.get_tensor_by_name('num_detections:0')


def qj_detection(image_name):
    # Size, in inches, of the output images.
    IMAGE_SIZE = (12, 8)
    start_time = time.time()
    image = Image.open(image_name)
#convert PNG to JPG
    r,g,b,a=image.split()
    image = Image.merge("RGB", (r,g,b))
    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.
    image_np = load_image_into_numpy_array(image)
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    # Actual detection.
    loaded_time = time.time()
    logging.debug("Detection of loading image time: %f"%(loaded_time-start_time))
    start_time = loaded_time
    (boxes, scores, classes, num) = qj_sess.run(
      [detection_boxes, detection_scores, detection_classes, num_detections],
      feed_dict={image_tensor: image_np_expanded})

    detected_time = time.time()
    logging.debug("Detection of detecting image time: %f"%(detected_time-start_time))
    # Visualization of the results of a detection.
    vis_util.visualize_boxes_and_labels_on_image_array(
      image_np,
      np.squeeze(boxes),
      np.squeeze(classes).astype(np.int32),
      np.squeeze(scores),
      category_index,
      use_normalized_coordinates=True,
      line_thickness=8)

    boxes = np.squeeze(boxes).tolist()
    scores = np.squeeze(scores).tolist()
    classes = np.squeeze(classes).astype(np.int32).tolist()
    num = num.astype(np.int32).tolist()[0]

    return (image_np, image.size, boxes, scores, classes, num)

    im_width, im_height = image.size
#    print("image size is:", im_width, im_height)
#
#    print("==========================boxes========================\n")
#    print(boxes)
#    print("==========================scores========================\n")
#    print(scores)
#    print("==========================classes========================\n")
#    print(classes)
#    print("==========================num========================\n")
#    print(num)

    #find first position which equal to class actor(=1)
    actor_class = 1
    actor_index = classes.index(actor_class)
    ymin,xmin,ymax,xmax = boxes[actor_index]
    actor_y_norm = ymax
    actor_x_norm = xmin + (xmax - xmin)/2.0
    
    #force the actor to be drawed by change the possibility to 100%
    scores[actor_index] = 1.0
    
    #find target object position which has minimum y value of the screen
    target_index = 0
    target_y_norm = 1
    target_x_norm = 0
    #box should have minimun 60% possibility
    min_score_thresh = .6
    for i in range(num):
        #target object should not be same as actor
        if(classes[i] == actor_class):
            continue
        if(scores[i]<min_score_thresh): 
            break 
        ymin,xmin,ymax,xmax = boxes[i]
        y_norm = ymin + (ymax - ymin)/2.0
        if(y_norm < target_y_norm):
            target_y_norm = y_norm
            target_index = i
            target_x_norm = xmin + (xmax - xmin)/2.0
    target_class = classes[target_index]

#    print("==========================Actor Judgement========================\n")
#    print("actor index is:", actor_index)
#    print("actor class is:", actor_class)
#    print("actor pos is:", actor_y_norm, actor_x_norm)
#
#    print("==========================Target Judgement========================\n")
#    print("target index is:", target_index)
#    print("target class is:", target_class)
#    print("target pos is:", target_y_norm, target_x_norm)


    return ((actor_class, actor_y_norm*im_height, actor_x_norm*im_width), (target_class, target_y_norm*im_height, target_x_norm*im_width), image_np)

    plt.figure(figsize=IMAGE_SIZE)
    plt.imshow(image_np)
    plt.show()
    #return (np.squeeze(boxes), np.squeeze(scores), np.squeeze(classes), num)
    #return ((actor_class, actor_y_norm*im_height, actor_x_norm*im_width), (target_class, target_y_norm*im_height, target_x_norm*im_width))

#qj_detection('/Users/leo/ai/qj/object_detection/command/image1.jpg')
# (boxes, scores, classes, num) = qj_detection('/Users/leo/ai/qj/object_detection/command/autojump.png')
# jugdement = qj_detection('/Users/leo/ai/qj/object_detection/command/autojump.png')


    

