# -*- coding: utf-8 -*-
import os
import sys, getopt
import re
import random
import logging
import time
import numpy as np
import struct
import subprocess

import sqlite3
import pickle
import json
# use ordereddict to keep key seq of vott file
from collections import OrderedDict

from object_detection.utils import label_map_util

from img_detection import Detector
from device import Device


class Decisionor:
    def __init__(self, device, bookPath):
        self.gStartTime = time.time()
        self.gLastDecisionActions = []
        self.gDevice = device
        self.gBooks = {}
        self.logger = logging.getLogger('decision-%s'%(device.ip))
        self.logger.setLevel(logging.DEBUG)
        self.load_cmdbook(bookPath)

    def jobClear(self, bookname):
        job = self.gBooks[bookname]
        # each time add 0.1, check muli-times will finish, when it>=1.0
        job['JobClear'] = job['JobClear'] + 0.1

    def jobReset(self):
        gBooks = self.gBooks
        for bookname in gBooks:
            gBooks[bookname]['JobClear'] = 0.0

    def getDelta(self, tagname=''):
        start = self.gStartTime
        current = time.time()
        delta = current - start
        self.gStartTime = current
        return delta


    # Check valid of the diction , initial default value
    # Format is as tmpl.
    def init_book_keybody_condition_job(self, job):
        # Init default value from template
        tmpl = {
            "Name": "",
            "Status": ">0",
            "Bookname": None
        }
        for key in tmpl:
            # Set default value for job
            if not key in job:
                job[key] = tmpl[key]
            # Some field should not use default
            assert job[key] != None, \
                "key:%s MUST set a value in job body:%s"%(key,job)

    # Check valid of the diction , initial default value
    # Format is as tmpl.
    def init_book_keybody_condition_disallow(self, disallow):
        # Init default value from template
        tmpl = {
            "Name": "",
            "Seconds": 0,
            "Tags": None
        }
        for key in tmpl:
            # Set default value for disallow
            if not key in disallow:
                disallow[key] = tmpl[key]
            # Some field should not use default
            assert disallow[key] != None, \
                "key:%s MUST set a value in disallow body:%s"%(key,disallow)
        # Unify the following field to list
        if not isinstance(disallow['Tags'], list):
            disallow['Tags'] = [disallow['Tags']]

    # Check valid of the diction , initial default value
    # Format is as tmpl.
    def init_book_keybody_condition_allow(self, allow):
        # Init default value from template
        tmpl = {
            "Name": "",
            "Percent": 1.0,
            "Tags": None
        }
        for key in tmpl:
            # Set default value for allow
            if not key in allow:
                allow[key] = tmpl[key]
            # Some field should not use default
            assert allow[key] != None, \
                "key:%s MUST set a value in allow body:%s"%(key,allow)
        # Unify the following field to list
        if not isinstance(allow['Tags'], list):
            allow['Tags'] = [allow['Tags']]

    # Check valid of the diction , initial default value
    # Format is as:
    #    {
    #        "Name": "",
    #        "Allow": [...]
    #        "Jobs": [...]
    #        "Disallow": [...]
    #    }
    def init_book_keybody_condition(self, cunit):
        # Init default value
        if not 'Name' in cunit:
            cunit['Name'] = ''
        if not 'Allow' in cunit:
            cunit['Allow'] = []
        if not 'Jobs' in cunit:
            cunit['Jobs'] = []
        if not 'Disallow' in cunit:
            cunit['Disallow'] = []

        # Unify the following field to list
        if not isinstance(cunit['Allow'], list):
            cunit['Allow'] = [cunit['Allow']]
        if not isinstance(cunit['Jobs'], list):
            cunit['Jobs'] = [cunit['Jobs']]
        if not isinstance(cunit['Disallow'], list):
            cunit['Disallow'] = [cunit['Disallow']]

        for allow in cunit['Allow']:
            self.init_book_keybody_condition_allow(allow)

        for disallow in cunit['Disallow']:
            self.init_book_keybody_condition_disallow(disallow)

        for job in cunit['Jobs']:
            self.init_book_keybody_condition_job(job)


    # Check valid of the diction , initial default value
    # Format is as acTemplate.
    def init_book_keybody_action(self, cunit):
        # Init default value
        acTemplate = {
            "Action_Click": {
                    "Name": "",
                    "Command": "Click",
                    "DecisionPeriod": 0,
                    "PresetPeriod": 0,
                    "StartTag": None,
                    "StartOffset": [],
                    "EndTag": [],
                    "EndOffset": [],
                    "Duration": "20~50"
            },
            "Action_Reload": {
                    "Name": "",
                    "Command": "Reload",
                    "DecisionPeriod": 0,
                    "PresetPeriod": 2000
            },
            "Action_Goto": {
                    "Name": "",
                    "Command": "Goto",
                    "DecisionPeriod": 0,
                    "PresetPeriod": 0,
                    "BookName": None
            }
        }
        cmd = cunit[u'Command']
        tmpl = acTemplate["Action_"+cmd]
        # TODO: support StartTag,EndTag list convert
        for key in tmpl:
            # Set default value for cunit
            if not key in cunit:
                cunit[key] = tmpl[key]
            # Some field should not use default
            assert cunit[key] != None, \
                "key:%s MUST set a value in Action body:%s"%(key,cunit)


    # Check valid of the diction , initial default value
    # Format is as:
    #    {
    #        "Name": "",
    #        "Conditions": [...],
    #        "Actions": [...],
    #    }
    def init_book_keybody(self, kunit):
        # Init default value
        if not 'Name' in kunit:
            kunit['Name'] = ''
        # Unify the following field to list
        if not isinstance(kunit['Conditions'], list):
            kunit['Conditions'] = [kunit['Conditions']]
        for cunit in kunit[u'Conditions']:
            self.init_book_keybody_condition(cunit)
        # Unify the following field to list
        if not isinstance(kunit['Actions'], list):
            kunit['Actions'] = [kunit['Actions']]
        for cunit in kunit[u'Actions']:
            self.init_book_keybody_action(cunit)

    # Check valid of the source book diction , initial default value
    # Format is as:
    # {
    #     "BookName": "",
    #     "InferenceFile": "",
    #     "LabelMapFile": "",
    #     "Sequence": [
    #         {
    #             "Name": "",
    #             "KeyBody": [...]
    #         }
    #      ]
    # }
    def init_book(self, d):
        gBooks = self.gBooks
        # load book unit
        # Check valid of the book
        # Unify the following field to list
        if not isinstance(d['Sequence'], list):
            d['Sequence'] = [d['Sequence']]
        for bunit in d['Sequence']:
            # Init default value
            if not 'Name' in bunit:
                bunit['Name'] = ''
            # Unify the following field to list
            if not isinstance(bunit['KeyBody'], list):
                bunit['KeyBody'] = [bunit['KeyBody']]
            for kunit in bunit[u'KeyBody']:
                self.init_book_keybody(kunit)
        

    def load_cmdbook(self, bookpath):
        gBooks = self.gBooks
        # Read input file
        for fname in os.listdir(bookpath):
            if not fname.endswith(".cmd"):
                continue

            self.logger.info('LOADING book: %s'%(fname))
            fin = open(os.path.join(bookpath,fname), 'r')
            d = json.load(fin, object_pairs_hook=OrderedDict)
            #d = json.load(fin)
            fin.close()
            infname = d['InferenceName']
            bookname = os.path.basename(fname).split('.')[0].strip()
            assert bookname not in gBooks, \
                "book %s in file:%s is duplicated"%(bookname,fname)

            book = {}
            if infname in gBooks:
                self.logger.debug("book %s in file:%s using existing inference:%s"%(bookname,fname,infname))
                book['label2id_map'] = gBooks['infname']['label2id_map']
                book['id2label_map'] = gBooks['infname']['id2label_map']
                book['Detector'] = gBooks['infname']['Detector']

            else:
                # load label map
                label2id_map = label_map_util.get_label_map_dict(d['LabelMapFile'])
                id2label_map = {}
                for key in label2id_map.keys():
                    val = label2id_map[key]
                    id2label_map[val] = key
                book['label2id_map'] = label2id_map
                book['id2label_map'] = id2label_map
                # load a detector
                detectorName = self.gDevice.ip+'-'+bookname
                book['Detector'] = Detector(detectorName, d['InferenceFile'], d['LabelMapFile'])

            self.init_book(d)
            book['Sequence'] = d['Sequence']
            # How much jobs already done in this book
            book['JobClear'] = 0.0
            gBooks[bookname] = book

            
    
    def decision_do(self, tags, bookname, pos_dict):
        gBooks = self.gBooks
        jobUpdated = False

        image_size = tags['image_size']
        boxes = tags['tag_boxes']
        scores = tags['tag_scores']
        classes = tags['tag_classes']
        num = tags['tag_num']

        book = gBooks[bookname]

        # Loop the book
        self.logger.debug('Loop the book')
        # record the bunit which need to adjust sequence
        for bunit in book['Sequence']:
            kunit2move = {}
            for kunit in bunit['KeyBody']:
                # Check conditions is ok or not.
                self.logger.debug('Check condition [%s][%s][%s]'\
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
                            if not pos_dict[tag]:
                                # clear the timecount
                                disallow['timelast'] = 0.0
                                continue
                            # found disallowed tag
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
                            self.logger.debug('Not satisfied by tag disallow:%s'%(tag))
                            break
                    # Check allow condition before check disallow
                    # otherwise some disallow condition will always happen
                    for allow in cond[u'Allow']:
                        if allow_result:
                            break
                        allow_num_req = int(len(allow[u'Tags'])*allow[u'Percent'])
                        if allow_num_req == 0:
                            # At least one tag should be found
                            allow_num_req = 1
                        allow_num = 0
                        taglist = []
                        for tag in allow[u'Tags']:
                            if not pos_dict.has_key(tag):
                                continue
                            if pos_dict[tag]:
                                allow_num += 1
                                taglist.append(tag)
                        self.logger.debug('tag require:%d/100 of %s'%(100*allow[u'Percent'], allow[u'Tags']))
                        self.logger.debug('tag detect: %s'%(str(taglist)))
                        if(allow_num >= allow_num_req):
                            allow_result = True
                            break
                if disallow_result or not allow_result:
                    # adjust priority of the current condition unit, put it to end of list
                    # it is very dangours to change multiple list member at same time
                    # so i just change one at one time
                    if not kunit2move:
                        kunit2move = kunit
                    continue
                # kunit condition is ok, do the action.
                self.logger.debug('Condition is ready...')
                jobUpdated = self.do_action(bookname, bunit, kunit, tags, pos_dict)
                if jobUpdated:
                    # Only one of the first real actived condition in KeyBody list will be executed
                    break
            # adjust priority of the current task, put it to end of Keybody list
            # this adjust is import to avoid dead loop switch in two tasks
            # DO NOT adjust if no condition is correct last time
            if jobUpdated and kunit2move:
                self.logger.info('Adjust kunit to end. Book:%s, bunit:%s, kunit:%s'\
                            %(bookname,bunit['Name'],kunit2move))
                bunit['KeyBody'].remove(kunit2move)
                bunit['KeyBody'].append(kunit2move)
                kunit2move = {}

        return jobUpdated
            

    def do_action(self, bookname, bunit, kunit, tags, pos_dict):
        gLastDecisionActions = self.gLastDecisionActions
        jobUpdated = False
        actions = kunit[u'Actions']
        num = len(actions)
        for idx in range(num):
            action = actions[idx]
            current_time = time.time()
            self.logger.debug('entering action: %s'%(str(action)))
            if len(gLastDecisionActions) > idx:
                if gLastDecisionActions[idx]['Action'] == action:
                    delta = (current_time - gLastDecisionActions[idx]['Time'])*1000
                    decision_period = float(action[u'DecisionPeriod'])
                    if(delta < decision_period):
                        self.logger.debug('delay this action since \
                            delta:%f < decision period:%f'%(delta, decision_period))
                        jobUpdated = True
                        continue
            if action[u'Command'] == u'Click':
                temp = self.do_action_click(bookname, actions, idx, tags, pos_dict)
                if temp == True:
                    jobUpdated = True
            elif action[u'Command'] == u'Goto':
                temp = self.do_action_goto(bookname, actions, idx, tags, pos_dict)
                if temp == True:
                    jobUpdated = True
            else:
                self.logger.info('DO ACTION:%s, PARAM:this action is tbd..., BODY:%s'\
                                %(action['Command'],str(action)))
                continue
        return jobUpdated
            
    def do_action_goto(self, current_book, actions, idx, tags, pos_dict):
        gLastDecisionActions = self.gLastDecisionActions
        jobUpdated = False
        # Nested call decision_loop('GotoBook')
        # If the 'GotoBook' find nothing, will come back to UpperBook.
        action = actions[idx]
        target_book = action[u'BookName']
        if(len(gLastDecisionActions) <= idx):
            gLastDecisionActions.append({ 'CurrentBook':current_book, \
                                    'Time' : time.time(), \
                                    'Action': action, \
                                    'Command':action['Command'],\
                                    'Params': { 'target_book':target_book }
                                    })
        else:
            gLastDecisionActions[idx] = { 'CurrentBook':current_book, \
                                    'Time' : time.time(), \
                                    'Action': action, \
                                    'Command':action['Command'],\
                                    'Params': { 'target_book':target_book }
                                    }
        param = 'From book:%s goto book:%s'%(current_book, target_book)
        self.logger.info('DO ACTION:Goto, PARAM:%s, BODY:%s'\
                        %(param, gLastDecisionActions[idx]))
        jobUpdated = self.decision_loop(target_book)
        param = 'End Loop inside book: %s, back to:%s'%(target_book, current_book)
        self.logger.info('DO ACTION:GoBack, PARAM:%s'%(param))
        return jobUpdated


    def do_action_click(self, current_book, actions, idx, tags, pos_dict):
        gLastDecisionActions = self.gLastDecisionActions
        # Always need to updated if click ready
        jobUpdated = True
        gDevice = self.gDevice
        action = actions[idx]
        im_width, im_height = tags['image_size']
        boxes = tags['tag_boxes']
        scores = tags['tag_scores']
        classes = tags['tag_classes']
        num = tags['tag_num']

        #find click start point where first StartTag[...] match
        start_key = ''
        for key in action[u'StartTag']:
            if pos_dict.has_key(key):
                start_key = key
                break
        if not start_key:
            param = 'No match StartTag : %s'%(str(action[u'StartTag']))
            self.logger.info('CANCEL ACTION:Click, PARAM:%s, BODY:%s'\
                            %(param, str(action)))
            return jobUpdated
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
        self.logger.debug('[start point] key:%s, rxmin:%f, rymin:%f, rxmax:%f, rymax:%f, \
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
            self.logger.debug('[end point] key:%s, rxmin:%f, rymin:%f, rxmax:%f, rymax:%f, \
                            rxoffset:%f, ryoffset:%f, xend:%d, yend:%d'%\
                            (end_key, rxmin, rymin, rxmax, rymax, \
                            rxoffset, ryoffset, xend, yend))
        #get how many millisecond to swipe
        #it will be a random value like 2~5, default is 10~50ms
        duration_range = self.parse_range(action[u'Duration'])
        if not duration_range:
            duration_range = [10, 50]
        duration = random.randint(duration_range[0], duration_range[1])
        gDevice.swipe(xstart, ystart, xend, yend, duration)
        if(len(gLastDecisionActions) <= idx):
            gLastDecisionActions.append({ 'CurrentBook':current_book, \
                                    'Time' : time.time(), \
                                    'Action': action, \
                                    'Command':action['Command'],\
                                    'Params': { 'start_key':start_key,'xstart':xstart,'ystart':ystart,\
                                                'end_key':end_key,'xend':xend,'yend':yend,'duration':duration}
                                    })
        else:
            gLastDecisionActions[idx] = { 'CurrentBook':current_book, \
                                    'Time' : time.time(), \
                                    'Action': action, \
                                    'Command':action['Command'],\
                                    'Params': { 'start_key':start_key,'xstart':xstart,'ystart':ystart,\
                                                'end_key':end_key,'xend':xend,'yend':yend,'duration':duration}
                                    }
        param = str(gLastDecisionActions[idx])
        self.logger.info('DO ACTION:Click, PARAM:%s, BODY:%s'\
                        %(param, str(action)))
        return jobUpdated
    
    # range format should be a string like '2~5' or '3'
    def parse_range(self, fromto):
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


    def decision_loop(self, bookname=u'Index'): 
        gDevice = self.gDevice
        gBooks = self.gBooks
        jobUpdated = False
        if not bookname in gBooks:
            self.logger.warn('book:%s do not exist'%(bookname))
            return jobUpdated
        book = gBooks[bookname]
        while True:
            self.logger.info('===============START ACTION: Loop inside book: %s============'%(bookname))
            self.getDelta("Before Call getNumpyData")
            err, image_size, img_np = gDevice.getNumpyData()
            self.logger.debug('DETECT: getNumpyData used:%s seconds, image size:%s'\
                            %(self.getDelta(),image_size))
            if err:
                self.logger.warn('getNumpyData failed, \
                                  sleep 5s, error:%s'%(err))
                time.sleep(5)
                continue
            self.getDelta("Before Call detection")
            (image_np, tag_boxes, tag_scores, tag_classes, tag_num) = book['Detector'].detect(img_np)
            self.logger.debug('Book:%s, detect used:%s seconds'%(bookname, self.getDelta()))
            tags = {'image_size':image_size, \
                    'tag_boxes':tag_boxes, \
                    'tag_scores':tag_scores, \
                    'tag_classes':tag_classes,\
                    'tag_num':tag_num}
            #store the detected object index position in tags
            pos_dict = {}
            for label_name in book['label2id_map']:
                pos_dict[label_name] = []
            #box should have minimun 60% possibility
            min_score_thresh = .8
            for i in range(tag_num):
                if(tag_scores[i]<min_score_thresh): 
                    break 
                pos_dict[book['id2label_map'][tag_classes[i]]].append(i)

            tagsFound = {}
            for name in pos_dict:
                if pos_dict[name]:
                    tagsFound[name] = {'scores':[],'boxes':[]}
                    for pos in pos_dict[name]:
                        tagsFound[name]['scores'].append(tag_scores[pos])
                        tagsFound[name]['boxes'].append(tag_boxes[pos])
            
            self.logger.debug('DETECT: found tags:%s'%(tagsFound.keys()))
            self.logger.debug('DETECT: tags detail:%s'%(tagsFound))

            if not tagsFound:
                self.logger.debug('DETECT: book:%s do not detect any tags'%(bookname))
                #subbook will be terminated
                if(bookname!=u'Index'):
                    break
                #Index book will be conitnued
                time.sleep(1)
                continue

            jobUpdated = self.decision_do(tags, bookname, pos_dict)
            #subbook will be terminated if meet with incorrect decision
            #if(bookname!=u'Index' and jobUpdated==False):
            if(jobUpdated==True):
                #job updated
                self.jobReset()
            else:
                self.jobClear(bookname)
                self.logger.debug('DETECT: book:%s do not satify any condition,wrong book or job clear:[%f].'\
                                %(bookname, self.gBooks[bookname]['JobClear']))
                # switching between books need double check, so Index book cannot break directly
                if(bookname!='Index'):
                    break
                # It has been double checked 
                elif(self.gBooks['Index']['JobClear'] >=1.0):
                    break
            # Continue to next round.
            jobUpdated = False
            time.sleep(1)
        return jobUpdated






