
# coding: utf-8

# # Object Detection Demo
# Welcome to the object detection inference walkthrough!  This notebook will walk you step by step through the process of using a pre-trained model to detect objects in an image. Make sure to follow the [installation instructions](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/installation.md) before you start.

# # Imports

# In[19]:


import numpy as np
import os
import sys
import tensorflow as tf
import logging
import time

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
# Any model exported using the `export_inference_graph.py` tool can be loaded here simply by changing `inference_file` to point to a new .pb file.  
# 
# By default we use an "SSD with Mobilenet" model here. See the [detection model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) for a list of other models that can be run out-of-the-box with varying speeds and accuracies.


# should not be too many classes
MAX_NUM_CLASSES = 999



class Detector:
    # inference_file is frozen detection graph. This is the actual model that is used for the object detection.
    # label_file is used to add correct label for each box.
    def __init__(self, name, inference_file, label_file):
        # ## Loading label map
        # Label maps map indices to category names, so that when our
        # convolution network predicts `5`, we know that this corresponds to
        # `airplane`.  Here we use internal utility functions, but anything
        # that returns a dictionary mapping integers to appropriate string
        # labels would be fine
        label_map = label_map_util.load_labelmap(label_file)
        categories = label_map_util.convert_label_map_to_categories(\
                    label_map, max_num_classes=MAX_NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)
        self.logger = logging.getLogger('detect-%s'%(name))
        self.logger.setLevel(logging.DEBUG)

        # ## Load a (frozen) Tensorflow model into memory.
        detection_graph = tf.Graph()
        with detection_graph.as_default():
          od_graph_def = tf.GraphDef()
          with tf.gfile.GFile(inference_file, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

        # Create a session for detection
        self.sess = tf.Session(graph=detection_graph)
        # Definite input and output Tensors for detection_graph
        self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    # # Detection
    # Input a numpy array of image data, should be shape of [H, W, 3], 
    # The first dimension is pixel of each Heigh point,
    # The second dimension is pixel of each Width point,
    # The last dimension is pixel of is each (R,G,B) point.
    def detect(self, image_np):
        start_time = time.time()
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image_np, axis=0)
        # Actual detection.
        loaded_time = time.time()
        self.logger.debug("loading image time: %f"%(loaded_time-start_time))
        start_time = loaded_time
        (boxes, scores, classes, num) = self.sess.run(
          [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
          feed_dict={self.image_tensor: image_np_expanded})

        detected_time = time.time()
        self.logger.debug("detecting image time: %f"%(detected_time-start_time))
        # Visualization of the results of a detection.
#        vis_util.visualize_boxes_and_labels_on_image_array(
#          image_np,
#          np.squeeze(boxes),
#          np.squeeze(classes).astype(np.int32),
#          np.squeeze(scores),
#          self.category_index,
#          use_normalized_coordinates=True,
#          line_thickness=8)

        boxes = np.squeeze(boxes).tolist()
        scores = np.squeeze(scores).tolist()
        classes = np.squeeze(classes).astype(np.int32).tolist()
        num = num.astype(np.int32).tolist()[0]

        return (image_np, boxes, scores, classes, num)

