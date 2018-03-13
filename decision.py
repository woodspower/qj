# -*- coding: utf-8 -*-
import os
import re
import random
import logging
import time
import numpy as np
import struct

import datetime
import sqlite3
import pickle
import json
# use ordereddict to keep key seq of vott file
from collections import OrderedDict

from object_detection.utils import label_map_util

from img_detection import Detector

logging.basicConfig(filename='command.log', level=logging.DEBUG)

# minimum 3 seconds between each decision 
DECISION_PERIOD_JUMP_MINIMUM = 8

start_time = datetime.datetime.now()
gLastDecisionActions = []



import subprocess
# return errcode, image_size, image_np
# image_np is a numpy array of image data which is defined by img_detection.py
# Data format should be shape of [H, W, 3], 
# The first dimension is pixel of each Heigh point,
# The second dimension is pixel of each Width point,
# The last dimension is pixel of is each (R,G,B) point.
def pull_screenshot():
    # raw data format from adb:
    # 4Bytes(width) + 4Bytes(heigh) + 4Bytes(format) + ...N*4Bytes(each byte is a bitmap:RGBA)
    # fp = os.popen("/opt/genymobile/genymotion/tools/adb exec-out screencap")
    #ret = os.system('/opt/genymobile/genymotion/tools/adb shell screencap -p /sdcard/snapshot.png')
    #ret = os.system('/opt/genymobile/genymotion/tools/adb pull /sdcard/snapshot.png %s'%(IMAGE_FILE))
    proc = subprocess.Popen(["/opt/genymobile/genymotion/tools/adb","exec-out","screencap"], \
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out,err) = proc.communicate()
    if err:
        #print('Error when pull_screenshot:%s'%(err))
        return err, (), []
    head = out[:12]
    # recover data form ctype
    w,h,ft = struct.unpack_from('3i',head)
    data = out[12:]
    if(len(data) != w*h*4):
        #print('data len of pull_screenshot:%d, is same as Width*Heigh(%d*%d)'%(len(data),w,h))
        return 'error len:%d, w:%d, h:%d'%(len(data),w,h), (), []
    img = np.asarray(struct.unpack_from('%dB'%(w*h*4), data), dtype=np.uint8).reshape([h,w,4])
    # Change last dimension from (R,G,B,A) to (R,G,B)
    img = np.delete(img, 3, axis=2)
    return '', (w,h), img

def print_delta_time(tagname):
    global start_time
    current_time = datetime.datetime.now()
    delta_time = current_time - start_time
    start_time = current_time
    print(tagname, " : ", delta_time.seconds)

gBooks = {}
def load_cmdbook(bookpath):
    global gBooks
    # Read input file
    for fname in os.listdir(bookpath):
        if not fname.endswith(".cmd"):
            continue

        print 'load cmdbook:', fname
        logging.info('Loading book: %s'%(fname))
        fin = open(os.path.join(bookpath,fname), 'r')
        d = json.load(fin, object_pairs_hook=OrderedDict)
        fin.close()
        bookname = d['Name']
        assert not gBooks.has_key(bookname), \
            "book %s is duplicate in file:%s"%(bookname,fname)
        book = {}
        gBooks[bookname] = book

        # load label map
        label2id_map = label_map_util.get_label_map_dict(d['LabelMapFile'])
        id2label_map = {}
        for key in label2id_map.keys():
            val = label2id_map[key]
            id2label_map[val] = key
        book['label2id_map'] = label2id_map
        book['id2label_map'] = id2label_map

        # load main book unit
        # each book include a sequence of decision book unit
        book['Sequence'] = d['Sequence']
        # Check valid of the book
        for bunit in d['Sequence']:
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
                        # Doing the type check
                        for check in [(u'DecisionPeriod', float),\
                                      (u'StartTag',list),\
                                      (u'StartOffset',list),\
                                      (u'EndTag',list),\
                                      (u'EndOffset',list),\
                                      (u'Duration',str)]:
                            try:
                                check[1](check[0])
                            except: 
                                print "%s wrong in file:%s-[%s], \
                                [u'KeyBody']-[%s], \
                                [u'GoBack']-[%s])"\
                                %(val,fname,\
                                bunit[u'Name'],\
                                kunit[u'Name'],\
                                cunit[u'Name'])
        # load a detector
        book['Detector'] = Detector(book, d['InferenceFile'], d['LabelMapFile'])
            
    
def decision_do(detection_time, tags, bookname, pos_dict):
    correct_decision = False
#    global gLastDecisionActions
#    global gLastDecisionTime
#    delta = (detection_time - gLastDecisionTime).total_seconds()*1000
#    print("delta is: %f ms"%(delta))
#    if(delta <= 0):
#        # Need try again later
#        return True

    image_size = tags['image_size']
    boxes = tags['tag_boxes']
    scores = tags['tag_scores']
    classes = tags['tag_classes']
    num = tags['tag_num']

    book = gBooks[bookname]

    # Loop the book
    logging.info('Loop the book')
    # record the bunit which need to adjust sequence
    bunit2move = {}
    for bunit in book['Sequence']:
        for kunit in bunit['KeyBody']:
            # Check conditions is ok or not.
            logging.info('Check condition [%s][%s][%s]'\
                        %(bookname, bunit[u'Name'],kunit[u'Name']))
            disallow_result = False
            allow_result = False
            for cond in kunit[u'Conditions']:
                if disallow_result:
                    break
                for disallow in cond[u'Disallow']:
                    if disallow_result:
                        break
                    for tag in disallow[u'Tags']:
                        # Need check how long will triger disallow condition
                        # Set timelast and Seconds key in disallow
                        if not u'Seconds' in disallow:
                            # How many seconds will triger
                            disallow[u'Seconds'] = 0
                        if not 'timelast' in disallow:
                            # Last time checked, it is a time.time() float
                            disallow['timelast'] = 0.0
                        if not tag in pos_dict:
                            # clear the timecount
                            disallow['timelast'] = 0.0
                            continue
                        if pos_dict[tag]:
                            # check how long will triger disallow condition
                            if disallow[u'Seconds'] != 0:
                                if disallow['timelast'] == 0.0:
                                    # start to record time and count
                                    disallow['timelast'] = time.time()
                                    continue
                                timenow = time.time()
                                delta = timenow - disallow['timelast']
                                if delta <= disallow[u'Seconds']:
                                    continue
                            disallow_result = True
                            logging.info('Not satisfied by tag disallow:%s'%(tag))
                            break
                # Check allow condition before check disallow
                # otherwise some disallow condition will always happen
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
                # adjust priority of the current task, put it to end of list
                # it is very dangours to change multiple list member at same time
                # so i just change one at one time
                if not bunit2move:
                    bunit2move = bunit
                continue
            # kunit condition is ok, do the action.
            logging.info('Condition is ready...')
            correct_decision=True
            do_action(bookname, bunit, kunit, tags, pos_dict)
            # Only one of the first condition in KeyBody list will be executed
            break
    # adjust priority of the current task, put it to end of list
    if bunit2move:
        book['Sequence'].remove(bunit2move)
        book['Sequence'].append(bunit2move)
        bunit2move = {}

    return correct_decision
            

def do_action(bookname, bunit, kunit, tags, pos_dict):
    global gLastDecisionActions

    actions = kunit[u'Actions']
    num = len(actions)
    for idx in range(num):
        action = actions[idx]
        current_time = datetime.datetime.now()
        logging.info('entering action: %s'%(str(action)))
        if len(gLastDecisionActions) > idx:
            if gLastDecisionActions[idx]['Action'] == action:
                delta = (current_time - gLastDecisionActions[idx]['Time']).total_seconds()*1000
                decision_period = float(action[u'DecisionPeriod'])
                if(delta < decision_period):
                    logging.info('delay this action since delta:%f < decision period:%f'%(delta, decision_period))
                    continue
        if action[u'Command'] == u'Click':
            do_action_click(bookname, actions, idx, tags, pos_dict)
        elif action[u'Command'] == u'Goto':
            do_action_goto(bookname, actions, idx, tags, pos_dict)
        else:
            logging.info('this action is tbd....')
            continue
            
def do_action_goto(current_book, actions, idx, tags, pos_dict):
    global gLastDecisionActions
    # Nested call decision_loop('GotoBook')
    # If the 'GotoBook' find nothing, will come back to UpperBook.
    action = actions[idx]
    target_book = action[u'BookName']
    logging.info('From book:%s goto book:%s'%(current_book, target_book))
    if(len(gLastDecisionActions) <= idx):
        gLastDecisionActions.append({ 'CurrentBook':current_book, \
                                'Time' : datetime.datetime.now(), \
                                'Action': action, \
                                'Command':action['Command'],\
                                'Params': { 'target_book':target_book }
                                })
    else:
        gLastDecisionActions[idx] = { 'CurrentBook':current_book, \
                                'Time' : datetime.datetime.now(), \
                                'Action': action, \
                                'Command':action['Command'],\
                                'Params': { 'target_book':target_book }
                                }
    print('DO: %s'%(str(gLastDecisionActions[idx])))
    logging.info('DO: %s'%(str(gLastDecisionActions[idx])))
    decision_loop(target_book)
    logging.info('End Loop inside book: %s'%(target_book))


def do_action_click(current_book, actions, idx, tags, pos_dict):
    global gLastDecisionActions
    action = actions[idx]
    im_width, im_height = tags['image_size']
    boxes = tags['tag_boxes']
    scores = tags['tag_scores']
    classes = tags['tag_classes']
    num = tags['tag_num']

#    print("==========================boxes========================\n")
#    print(boxes)
#    print("==========================scores========================\n")
#    print(scores)
#    print("==========================classes========================\n")
#    print(classes)
#    print("==========================num========================\n")
#    print(num)
#    print("==========================pos_dict========================\n")
#    print(pos_dict)
#    print("==========================image_size========================\n")
#    print(tags['image_size'])

    #find click start point where first StartTag[...] match
    start_key = ''
    for key in action[u'StartTag']:
        if pos_dict.has_key(key):
            start_key = key
            break
    if not start_key:
        logging.info('action cancel since no match StartTag : %s'%(str(action[u'StartTag'])))
        return
    #find click start point
    #start point will caculate from center point of the start_key
    #x = ( rxmin + rxoffset*(rxmax-rxmin) )*im_width
    #y = ( rymin + ryoffset*(rymax-rymin) )*im_height
    #default offset is (1/2, 1/2) in the center of box
    #all the unit start with 'r' means relative distance
    rxoffset, ryoffset = 0.5, 0.5
    rymin,rxmin,rymax,rxmax = boxes[pos_dict[start_key][0]]
    yrand = random.random()*(rymax-rymin)*0.02
    xrand = random.random()*(rxmax-rxmin)*0.02
    if action[u'StartOffset']:
        (rxoffset, ryoffset) = action[u'StartOffset']
    rxstart = rxmin + rxoffset*(rxmax-rxmin)
    rystart = rymin + ryoffset*(rymax-rymin)
    multi = 1
    xstart = int((rxstart + multi*xrand)*im_width)
    ystart = int((rystart + multi*yrand)*im_height)
    if xstart < 0: 
        xstart = 5
    if xstart > im_width: 
        xstart = im_width-1
    if ystart < 0: 
        ystart = 5
    if ystart > im_height: 
        ystart = im_height-1
    logging.debug('[start point] key:%s, rxmin:%f, rymin:%f, rxmax:%f, rymax:%f, \
                    rxoffset:%f, ryoffset:%f, xstart:%d, ystart:%d'%\
                    (start_key, rxmin, rymin, rxmax, rymax, \
                    rxoffset, ryoffset, xstart, ystart))

    #find click end point where first EndTag[...] match
    end_key = ''
    for key in action[u'EndTag']:
        if pos_dict.has_key(key):
            end_key = key
            break
    if not end_key:
        xend = xstart
        yend = ystart
    else:
        #find click end point
        #end point will caculate from center point of the end_key
        #x = end_key.x + end_key.len_x/2 * rxoffset
        #y = end_key.y + end_key.len_y/2 * ryoffset
        #end point offset default is equal to start offset
        rymin,rxmin,rymax,rxmax = boxes[pos_dict[end_key][0]]
        yrand = random.random()*(rymax-rymin)*0.01
        xrand = random.random()*(rxmax-rxmin)*0.01
        if action[u'EndOffset']:
            (rxoffset, ryoffset) = action[u'EndOffset']
        rxend = rxmin + rxoffset*(rxmax-rxmin)
        ryend = rymin + ryoffset*(rymax-rymin)
        multi = 1
        xend = int((rxend + multi*xrand)*im_width)
        yend = int((ryend + multi*yrand)*im_height)
        if xend < 0: 
            xend = 1
        if xend > im_width: 
            xend = im_width-1
        if yend < 0: 
            yend = 1
        if yend > im_height: 
            yend = im_height-1
        logging.debug('[end point] key:%s, rxmin:%f, rymin:%f, rxmax:%f, rymax:%f, \
                        rxoffset:%f, ryoffset:%f, xend:%d, yend:%d'%\
                        (end_key, rxmin, rymin, rxmax, rymax, \
                        rxoffset, ryoffset, xend, yend))
    #get how many millisecond to swipe
    #it will be a random value like 2~5, default is 10~50ms
    duration_range = parse_range(action[u'Duration'])
    if not duration_range:
        duration_range = [10, 50]
    duration = random.randint(duration_range[0], duration_range[1])
    # do it
    cmd = '/opt/genymobile/genymotion/tools/adb shell input swipe %d %d %d %d '%\
            (xstart,ystart,xend,yend) + str(duration)
    os.system(cmd)
    print cmd
    if(len(gLastDecisionActions) <= idx):
        gLastDecisionActions.append({ 'CurrentBook':current_book, \
                                'Time' : datetime.datetime.now(), \
                                'Action': action, \
                                'Command':action['Command'],\
                                'Params': { 'start_key':start_key,'xstart':xstart,'ystart':ystart,\
                                            'end_key':end_key,'xend':xend,'yend':yend,'duration':duration}
                                })
    else:
        gLastDecisionActions[idx] = { 'CurrentBook':current_book, \
                                'Time' : datetime.datetime.now(), \
                                'Action': action, \
                                'Command':action['Command'],\
                                'Params': { 'start_key':start_key,'xstart':xstart,'ystart':ystart,\
                                            'end_key':end_key,'xend':xend,'yend':yend,'duration':duration}
                                }
    print('DO: %s'%(str(gLastDecisionActions[idx])))
    logging.info('DO: %s'%(str(gLastDecisionActions[idx])))

    
# range format should be a string like '2~5' or '3'
def parse_range(fromto):
    l = re.split('~', fromto)
    if not l:
        return []
    assert len(l)<=2,'Format err:%s'%(fromto)
    # not digit, it is comments field
    if not l[0].isdigit():
        return []
    if len(l)==1:
        # format like '303 '
        f,t = int(l[0]),int(l[0])
    else:
        # format like '303~ 307' or '303~303'
        f,t = int(l[0]),int(l[1])
    assert f<=t, 'Format err:%s'%(fromto)
    return [f,t]


def decision_loop(bookname=u'Index'): 
    if not gBooks.has_key(bookname):
        logging.info('book:%s do not exist'%(bookname))
        time.sleep(1)
        return
    book = gBooks[bookname]
    while True:
        print('Loop inside book: %s'%(bookname))
        logging.info('Loop inside book: %s'%(bookname))
        print_delta_time("Call pull")
        err, image_size, img_np = pull_screenshot()
        if err:
            print 'call screenshot failed, sleep 5s',err
            time.sleep(5)
            continue
        print_delta_time("After Call pull")
        (image_np, tag_boxes, tag_scores, tag_classes, tag_num) = book['Detector'].detect(img_np)
        tags = {'image_size':image_size, 'tag_boxes':tag_boxes, 'tag_scores':tag_scores, 'tag_classes':tag_classes, 'tag_num':tag_num}
        print_delta_time("After Call detection")
        #store the detected object index position in tags
        pos_dict = {}
        for label_name in book['label2id_map']:
            pos_dict[label_name] = []
        #box should have minimun 60% possibility
        min_score_thresh = .4
        for i in range(tag_num):
            if(tag_scores[i]<min_score_thresh): 
                break 
            pos_dict[book['id2label_map'][tag_classes[i]]].append(i)

        if not pos_dict:
            logging.info('book:%s do not detect any tags'%(bookname))
            #subbook will be terminated
            if(bookname!=u'Index'):
                break
            #Index book will be conitnued
            time.sleep(1)
            continue

        print("==========================image_size========================\n")
        print('book:',bookname)
        print(tags['image_size'])
#        print("==========================pos_dict========================\n")
#        print(pos_dict)
        for name in pos_dict:
            if pos_dict[name]:
                print 'found tag name:', name
                for pos in pos_dict[name]:
                    print 'tag score:', tag_scores[pos]
                    print 'tag boxe:', tag_boxes[pos]
        correct = decision_do(datetime.datetime.now(), tags, bookname, pos_dict)
        #subbook will be terminated if meet with incorrect decision
        if(bookname!=u'Index' and correct==False):
            logging.info('book:%s do not satify any condition'%(bookname))
            break
        time.sleep(1)



load_cmdbook('./qj_book')
decision_loop()




