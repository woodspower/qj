# -*- coding: utf-8 -*-
import os
import logging
import time
import numpy as np

import datetime
import sqlite3
import pickle
import json
# use ordereddict to keep key seq of vott file
from collections import OrderedDict

from object_detection.utils import label_map_util

logging.basicConfig(filename='command.log', level=logging.DEBUG)
LABEL_MAP_FILE = os.path.join('/home/leo/qj/object_detection/data/pascal_label_map.pbtxt')

label2id_map = label_map_util.get_label_map_dict(LABEL_MAP_FILE)

id2label_map = {}
for key in label2id_map.keys():
    val = label2id_map[key]
    id2label_map[val] = key

# minimum 3 seconds between each decision 
DECISION_PERIOD_JUMP_MINIMUM = 8

start_time = datetime.datetime.now()
last_decision_time = datetime.datetime.now()

conn = sqlite3.connect('file:qjdb?mode=memory&cache=shared') 

def print_delta_time(tagname):
    global start_time
    current_time = datetime.datetime.now()
    delta_time = current_time - start_time
    start_time = current_time
    print(tagname, " : ", delta_time.seconds)

gBookDict = {}
def load_cmdbook(bookpath):
    global gBookDict
    # Read input file
    for fname in os.listdir(bookpath):
        if not fname.endswith(".cmd"):
            continue

        logging.info('Loading book: %s'%(fname))
        fin = open(os.path.join(bookpath,fname), 'r')
        d = json.load(fin, object_pairs_hook=OrderedDict)
        fin.close()
        # Filename should be same as book key name
        book = os.path.splitext(fname)[0]
        assert not gBookDict.has_key(book), \
            "book %s is duplicate in file:%s"%(book,fname)
        gBookDict[book] = d[book]
        # Check valid of the book
        for bunit in d[book]:
            for kunit in bunit[u'KeyBody']:
                check_dict = {u'Allow':[u'Percent',u'Tags'],\
                              u'Disallow':[u'Tags']}
                for cunit in kunit[u'Conditions']:
                    for uk in check_dict.keys():
                        for unit in cunit[uk]:
                            for val in check_dict[uk]:
                                assert unit.has_key(val), \
                                    "%s not in file:%s-[%s], \
                                    [u'KeyBody']-[%s], \
                                    [u'Conditions']-[%s], \
                                    [%s]-[%s]"\
                                    %(val,fname,\
                                    bunit[u'Name'],\
                                    kunit[u'Name'],\
                                    cunit[u'Name'],\
                                    uk,unit[u'Name'])
                check_dict = {u'Click':[u'DecisionPeriod',u'StartTag',\
                                        u'StartOffset',u'EndTag',\
                                        u'EndOffset',u'Duration'],\
                              u'Goto':[u'DecisionPeriod',u'BookName']}
                for cunit in kunit[u'Actions']:
                    key = cunit[u'Command']
                    for val in check_dict[key]:
                        assert cunit.has_key(val), \
                            "%s not in file:%s-[%s], \
                            [u'KeyBody']-[%s], \
                            [u'Actions']-[%s])"\
                            %(val,fname,\
                            bunit[u'Name'],\
                            kunit[u'Name'],\
                            cunit[u'Name'])
                if kunit.has_key(u'GoBack'):
                    for cunit in kunit[u'GoBack']:
                        for check in [u'DecisionPeriod',u'StartTag',\
                                      u'StartOffset',u'EndTag',\
                                      u'EndOffset',u'Duration']:
                            assert cunit.has_key(val), \
                                "%s not in file:%s-[%s], \
                                [u'KeyBody']-[%s], \
                                [u'GoBack']-[%s])"\
                                %(val,fname,\
                                bunit[u'Name'],\
                                kunit[u'Name'],\
                                cunit[u'Name'])
            
    
def decision_do(detection_time, tags):
    global last_decision_time
    current_time = datetime.datetime.now()
    detection_time = datetime.datetime.strptime(detection_time, "%y:%m:%d:%H:%M:%S:%f")
    delta = (detection_time - last_decision_time).total_seconds()*1000
    print("delta is: %s ms"%(delta))
    if(delta <= 0):
        return

    image_size = tags['image_size']
    boxes = tags['tag_boxes']
    scores = tags['tag_scores']
    classes = tags['tag_classes']
    num = tags['tag_num']

    pos_dict = {}
    for label_name in label2id_map:
        pos_dict[label_name] = []
    #box should have minimun 60% possibility
    min_score_thresh = .6
    for i in range(num):
        if(scores[i]<min_score_thresh): 
            break 
        pos_dict[id2label_map[classes[i]]].append(i)
    
    # Loop the Index book
    logging.info('Loop the Index book')
    for bunit in gBookDict[u'Index']:
        for kunit in bunit['KeyBody']:
            # Check conditions is ok or not.
            logging.info('Check condition for Index[%s][%s]'\
                        %(bunit[u'Name'],kunit[u'Name']))
            disallow_result = False
            allow_result = False
            for cond in kunit[u'Conditions']:
                if disallow_result:
                    break
                for disallow in cond[u'Disallow']:
                    if disallow_result:
                        break
                    for tag in disallow[u'Tags']:
                        if pos_dict.has_key(tag):
                            disallow_result = True
                            logging.info('Not satisfied by tag disallow:%s'%(tag))
                            break
                for allow in cond[u'Allow']:
                    if allow_result:
                        break
                    allow_num_req = int(len(allow[u'Tags'])*allow[u'Percent'])
                    allow_num = 0
                    taglist = []
                    for tag in allow[u'Tags']:
                        if not pos_dict.has_key(tag):
                            continue
                        if pos_dict[tag]:
                            allow_num += 1
                            taglist.append(tag)
                    logging.debug('tag require:%d/100 of %s'%(100*allow[u'Percent'], allow[u'Tags']))
                    logging.debug('tag detect: %s'%(str(taglist)))
                    if(allow_num >= allow_num_req):
                        allow_result = True
                        break
            if disallow_result or not allow_result:
                continue
            # kunit condition is ok, do the action.
            print('Condition for Index[%s][%s] is ready...'\
                        %(bunit[u'Name'],kunit[u'Name']))
            for actunit in kunit[u'Actions']:
                decision_period = actunit[u'DecisionPeriod']
                if(delta < decision_period):
                    print("Delta:%f is less than DecisionPeriod:%f"%(delta, float(decision_period)))
                    logging.info("Delta:%f is less than DecisionPeriod:%f"%(delta, float(decision_period)))
                    continue
                else:
                    print("Do action:", kunit[u'Actions'])
                    logging.info('Do actions: %s'%(str(kunit[u'Actions'])))
                    last_decision_time = current_time
            return
            
                


    
	
def decision_loop(): 
    while True:
        cursor = conn.cursor() 
        cursor.execute("select * from tags where key='latest'")
        query = cursor.fetchone()
        if not query:
            cursor.close()
            print('no data in db')
            return
        key, newflag, detection_time, s = query
        tags = pickle.loads(s)
        # print('tags:' , tags)
        if(tags["tag_num"] == 0):
            print('tag is not init in db')
            return
        decision_do(detection_time, tags)
        time.sleep(1)


    image_size = tags['image_size']
    boxes = tags['tag_boxes']
    scores = tags['tag_scores']
    classes = tags['tag_classes']
    num = tags['tag_num']


#    boxes = np.squeeze(boxes).tolist()
#    scores = np.squeeze(scores).tolist()
#    classes = np.squeeze(classes).astype(np.int32).tolist()
#    num = num.astype(np.int32).tolist()[0]

    im_width, im_height = image_size
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
    actor_class = label2id_map['actor']
    score_class = label2id_map['score']
    actor_index = classes.index(actor_class)
    ymin,xmin,ymax,xmax = boxes[actor_index]
    actor_y_norm = ymax
    actor_x_norm = xmin + (xmax - xmin)/2.0
    
    #force the actor to be drawed by change the possibility to 100%
    scores[actor_index] = 1.0
    
    #find target object position which has minimum y value of the screen
    target_index = -1
    target_y_norm = 1
    target_x_norm = 0
    #box should have minimun 60% possibility
    min_score_thresh = .6
    for i in range(num):
        #target object should not be same as actor
        if((classes[i] == actor_class) or (classes[i] == score_class)):
            continue
        if(scores[i]<min_score_thresh): 
            break 
        ymin,xmin,ymax,xmax = boxes[i]
        y_norm = ymin + (ymax - ymin)/2.0
        if(y_norm < target_y_norm):
            target_y_norm = y_norm
            target_index = i
            target_x_norm = xmin + (xmax - xmin)/2.0
    if( target_index == -1):
        print("target not found.")
        return
    target_class = classes[target_index]

    actor = (actor_class, actor_y_norm*im_height, actor_x_norm*im_width)
    target = (target_class, target_y_norm*im_height, target_x_norm*im_width)

    print("==========================Actor Judgement========================\n")
    print("actor index is:", actor_index)
    print("actor class is:", actor_class)
    print("actor pos is:", actor_y_norm, actor_x_norm)

    print("==========================Target Judgement========================\n")
    print("target index is:", target_index)
    print("target class is:", target_class)
    print("target pos is:", target_y_norm, target_x_norm)


    distance = (target[2]-actor[2])**2 + (target[1]-actor[1])**2
    distance = distance ** 0.5
    print('auto distance = ', distance)
    
    if(distance <=500):
        press_time = distance * 1.
    else:
        press_time = 500*1. + distance-500
    x1 = np.random.randint(600,700)
    x2 = x1 + np.random.randint(0,5)
    y1 = np.random.randint(2000,2100)
    y2 = y1 + np.random.randint(0,5)
    press_time = int(press_time)
    cmd = 'adb shell input swipe %d %d %d %d '%(x1,y1,x2,y2) + str(press_time)
    print(cmd)
    os.system(cmd)

    if(delta < DECISION_PERIOD_JUMP_MINIMUM):
        cursor.close()
        print('current_time is:', current_time)
        print('detection_time is:', detection_time)
        print('last_decision_time is:', last_decision_time)
        return
    else:
#        cursor.execute("update tags set timestamp=? where key = 'latest'", (current_time_str,))
#        cursor.close()
#        conn.commit()
        last_decision_time = current_time

#    if(newflag == 'no'):
#        cursor.close()
#        print('flag is not new in db')
#        return
#    else:
#        cursor.execute("update tags set newflag='no'")
#        cursor.close()
#        conn.commit()
#    cursor.execute("select * from tags")
#    if(cursor.rowcount < 1):
#        print('no data in db:' , cursor.rowcount)
#        return


load_cmdbook('./qj_book')
decision_loop()




