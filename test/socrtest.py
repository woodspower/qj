import sys, getopt
sys.path.append('..')
import numpy as np
from detect import Detector
from PIL import Image
import time


#infFile = "/home/leo/qj/object_detection/data/socr/inference_frcnn/frozen_inference_graph.pb"
#mapFile = "/home/leo/qj/object_detection/data/socr/pascal_label_map.pbtxt"
infFile = "/home/leo/qj/object_detection/data/socr/inference_ssd/frozen_inference_graph.pb"
mapFile = "/home/leo/qj/object_detection/data/socr/pascal_label_map.pbtxt"
#infFile = "/home/leo/qj/object_detection/data/Index/inference_ssd/frozen_inference_graph.pb"
#mapFile = "/home/leo/qj/object_detection/data/Index/pascal_label_map.pbtxt"
imFiles = ["/home/leo/qj/object_detection/data/origin/socr_20180410/JPEGImages/im0505.jpg",
           "/home/leo/qj/object_detection/data/origin/socr_20180410/JPEGImages/im0506.jpg",
           "/home/leo/qj/object_detection/data/origin/socr_20180410/JPEGImages/im0507.jpg",
           "/home/leo/qj/object_detection/data/origin/socr_20180410/JPEGImages/im0508.jpg"]

detector = Detector('socr', infFile, mapFile)

for imFile in imFiles:
    img_np = np.asarray(Image.open(imFile))
    img_np.setflags(write=1)
    s = time.time()
    (image_np, tag_boxes, tag_scores, tag_classes, tag_num) = detector.detect(img_np, visualize=False)
    e = time.time()

    print 'detecting:',imFile
    print 'detect time is:',(e-s)
    print 'tag_num:',tag_num
    for c in tag_classes:
        if tag_scores[c]>=0.8:
            print 'tag:(%s,%f)',c,tag_scores[c]
