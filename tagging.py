# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('TKAgg')

import os
import time
import numpy as np

import img_detection as detector


import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image

import datetime
import sqlite3
import pickle



IMAGE_FILE = os.path.join(os.getenv("HOME"), 'aiswap/qj/snapshot.png')

start_time = datetime.datetime.now()

conn = sqlite3.connect('file:qjdb?mode=memory&cache=shared') 
cursor = conn.cursor() 
try: 
    cursor.execute('drop table tags') 
except: 
    print('Table user do not existing') 
 
#key: what kind of record. current only have 'latest' type
#newflag: when a new image is processed, this flag will set to 'yes'
#s: result from tensorflow detection function, serilized to store in db
cursor.execute('create table tags (key varchar(20) primary key, newflag varchar(20), timestamp varchar(30), s BLOB)')

tags = {'image_size':0, 'tag_boxes':0, 'tag_scores':0, 'tag_classes':0, 'tag_num':0}
s = pickle.dumps(tags)
cursor.execute("insert into tags (key, newflag, timestamp, s) values (\'latest\', \'no\', ?, ?)", (datetime.datetime.strftime(start_time, "%y:%m:%d:%H:%M:%S:%f"), sqlite3.Binary(s),))
cursor.close()
conn.commit()

def pull_screenshot():
#    ret = os.system('/opt/genymobile/genymotion/tools/adb shell screencap -p > %s'%(IMAGE_FILE))
    ret = os.system('/opt/genymobile/genymotion/tools/adb shell screencap -p /sdcard/snapshot.png')
    ret = os.system('/opt/genymobile/genymotion/tools/adb pull /sdcard/snapshot.png %s'%(IMAGE_FILE))
    return ret>>8


update = True
auto_conitinue = True
IMAGE_SIZE = (12, 8)
fig = plt.figure(figsize=IMAGE_SIZE)
pull_screenshot()
img = np.array(Image.open(IMAGE_FILE))
im = plt.imshow(img, animated=True)
plt.axis('off')
(image_np, image_size, tag_boxes, tag_scores, tag_classes, tag_num) = detector.qj_detection(IMAGE_FILE)



def update_data():
    return np.array(Image.open('snapshot.png'))

def print_delta_time(tagname):
    global start_time
    current_time = datetime.datetime.now()
    delta_time = current_time - start_time
    start_time = current_time
    print(tagname, " : ", delta_time.seconds)

def init():
    global image_np
    im.set_array(image_np)
    return im,


#TBD: Add timestamp into db
def updatefig(*args):
    global update
    global image_size
    global tag_boxes
    global tag_scores
    global tag_classes
    global tag_num
    global image_np
    if update:
        print_delta_time("Call pull")
        if(pull_screenshot() != 0):
            time.sleep(5)
            return im,
        print_delta_time("After Call pull")
        (image_np, image_size, tag_boxes, tag_scores, tag_classes, tag_num) = detector.qj_detection(IMAGE_FILE)
        print_delta_time("After Call detection")
        im.set_array(image_np)

        tags = {'image_size':image_size, 'tag_boxes':tag_boxes, 'tag_scores':tag_scores, 'tag_classes':tag_classes, 'tag_num':tag_num}
        s = pickle.dumps(tags)
        current_time = datetime.datetime.now()

        cursor = conn.cursor() 
        cursor.execute("update tags set s=?, newflag='yes', timestamp=? where key = 'latest'", (sqlite3.Binary(s),datetime.datetime.strftime(current_time, "%y:%m:%d:%H:%M:%S:%f"),))


        cursor.close()
        conn.commit()
        update = True


    return im,

def on_click(event):
    global update
    update = not update
    if(update):
        print("=======------- AI mode is Open -------==========")
    else:
        print("=======------- AI mode is Close ------==========")


fig.canvas.mpl_connect('button_press_event', on_click)
ani = animation.FuncAnimation(fig, updatefig, interval=50, blit=True)
#ani = animation.FuncAnimation(fig, updatefig,init_func=init, interval=50, blit=True)
plt.show()
