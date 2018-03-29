# -*- coding: utf-8 -*-
import os
import sys, getopt
import re
import fnmatch
import random
import logging
import time
import numpy as np
import struct
import subprocess
import copy

import sqlite3
import pickle
import json
# use ordereddict to keep key seq of vott file
from collections import OrderedDict

from object_detection.utils import label_map_util

from detect import Detector
from device import Device
import imdiff

UNIT_NUM_OF_EACH_ACTIONS_MAX = 10
CLICK_TIME_OF_SELECT_ACTION_MAX = 100

class Decisionor:
    def __init__(self, device, bookPath):
        self.gStartTime = time.time()
        self.gLastActions = [None]*UNIT_NUM_OF_EACH_ACTIONS_MAX
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
        for bookname in self.gBooks:
            self.gBooks[bookname]['JobClear'] = 0.0

    def jobIsAllClear(self):
        # check whether all the book jobs are cleared.
        isAllCleared = True
        for bookname in self.gBooks:
            status = self.gBooks[bookname]['JobClear']
            print 'STATUS: book %s job cleared:%f'%(bookname,status)
            if bookname == 'Index':
                # do not check Index book
                continue
            if status < 1.0:
                isAllCleared = False
                break
        return isAllCleared

    def getDelta(self, tagname=''):
        current = time.time()
        delta = current - self.gStartTime
        self.gStartTime = current
        return delta


    # Check valid of the diction , initial default value
    # Format is as tmpl.
    def init_book_keybody_condition_job(self, job):
        # Init default value from template
        tmpl = {
            "Name": "",
            "ClearedExpr": "<1.0",
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
            "Tags": None,
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
    # Format is as tmpl:
    def init_book_keybody_condition(self, cunit, kunit):
        # Init default value from template
        tmpl = {
            "Name": "",
            "Allow": [],
            "Jobs": [],
            "Disallow": [],
            "FocusArea":[0.,0.,1.,1.]
        }
        for key in tmpl:
            # Set default value for cunit
            if not key in cunit:
                cunit[key] = tmpl[key]
            # Some field should not use default
            assert cunit[key] != None, \
                "key:%s MUST set a value in body:%s"%(key,cunit)
        # Unify the following field to list
        if not isinstance(cunit['Allow'], list):
            cunit['Allow'] = [cunit['Allow']]
        if not isinstance(cunit['Jobs'], list):
            cunit['Jobs'] = [cunit['Jobs']]
        if not isinstance(cunit['Disallow'], list):
            cunit['Disallow'] = [cunit['Disallow']]
        # Need do some special init .
        rxmin,rymin,rxmax,rymax = cunit['FocusArea']
        assert (rxmin<=rxmax and rymin<=rymax),\
        "FocusArea:%s MUST be [rxmin,rymin,rxmax,rymax] in body %s"\
                %(cunit['FocusArea'], cunit)

        for allow in cunit['Allow']:
            self.init_book_keybody_condition_allow(allow)

        for disallow in cunit['Disallow']:
            self.init_book_keybody_condition_disallow(disallow)

        for job in cunit['Jobs']:
            self.init_book_keybody_condition_job(job)

    # Check valid of the aciton_goto diction , init default value
    # Format is as tmpl.
    def init_book_keybody_action_goto(self, cunit, kunit):
        # Init default value
        tmpl = {
            "Name": "",
            "PreloadTime": 0,
            "Command": "Goto",
            "PostloadTime": 0,
            "DecisionPeriod": 0,
            "BookName": None
        }
        for key in tmpl:
            # Set default value for cunit
            if not key in cunit:
                cunit[key] = tmpl[key]
            # Some field should not use default
            assert cunit[key] != None, \
                "key:%s MUST set a value in Action body:%s"%(key,cunit)

    # Check valid of the aciton_click diction , init default value
    # Format is as tmpl.
    def init_book_keybody_action_click(self, cunit, kunit):
        # Init default value
        tmpl = {
            "Name": "",
            "PreloadTime": 0,
            "Command": "Click",
            "PostloadTime": 2000,
            "DecisionPeriod": 0,
            "StartTag": [],
            "StartOffset": [0.5, 0.5],
            "EndTag": [],
            "EndOffset": [0.5, 0.5],
            "Duration": "20~50"
        }
        for key in tmpl:
            # Set default value for cunit
            if not key in cunit:
                cunit[key] = tmpl[key]
            # Some field should not use default
            assert cunit[key] != None, \
                "key:%s MUST set a value in Action body:%s"%(key,cunit)
        # Need do some special init .
        # if StatTag do not specified, set it to same as condition Tags
        if not cunit['StartTag']:
            condTags = []
            for cond in kunit['Conditions']:
                for allow in cond['Allow']:
                    condTags.extend(allow['Tags'])
            assert condTags, "StartTag MUST be set or \
                Condition Tag MUST be set in KeyBody:%s"%(kunit)
            cunit['StartTag'] = condTags
        # Unify the following field to list
        if not isinstance(cunit['StartTag'], list):
            cunit['StartTag'] = [cunit['StartTag']]
        if not isinstance(cunit['EndTag'], list):
            cunit['EndTag'] = [cunit['EndTag']]
        if not isinstance(cunit['StartOffset'], list):
            cunit['StartOffset'] = [cunit['StartOffset']]
        if not isinstance(cunit['EndOffset'], list):
            cunit['EndOffset'] = [cunit['EndOffset']]
            
    # Check valid of the aciton_select diction , init default value
    # Format is as tmpl.
    def init_book_keybody_action_select(self, cunit, kunit):
        # Init default value
        tmpl = {
            "Name": "",
            "PreloadTime": 0,
            "Command": "Select",
            "SelectToArea": None,
            "PostloadTime": 0,
            "DecisionPeriod": 5000,
            "StartTag": [],
            "StartOffset": [0.5, 0.5],
            "EndTag": [],
            "EndOffset": [0.5, 0.5],
            "Duration": "20~50",
            "JudgeConditions": None
        }
        for key in tmpl:
            # Set default value for uninitialed key 
            if not key in cunit:
                cunit[key] = tmpl[key]
            # Some field should not use default
            assert cunit[key] != None, \
                "key:%s MUST set a value in Action body:%s"%(key,cunit)
        # Need do some special init .
        # reuse click action init most of params
        self.init_book_keybody_action_click(cunit, kunit)
        if not isinstance(cunit['JudgeConditions'], list):
            cunit['JudgeConditions'] = [cunit['JudgeConditions']]
        for subunit in cunit['JudgeConditions']:
            self.init_book_keybody_condition(subunit, kunit)
        if 'SubActions' in cunit:
            # nested call init_actions
            # Unify the following field to list
            if not isinstance(cunit['SubActions'], list):
                cunit['SubActions'] = [cunit['SubActions']]
            self.init_book_keybody_actions(kunit, cunit['SubActions'])

    def init_book_keybody_actions(self, kunit, actions):
        # action unit number should not more than MAX
        num = len(actions)
        assert num <= UNIT_NUM_OF_EACH_ACTIONS_MAX, \
            "Actions unit number:%d MUST less than:%d in Action body:%s"\
            %(num,UNIT_NUM_OF_EACH_ACTIONS_MAX,kunit)
        for cunit in actions:
            cmd = cunit['Command']
            if cmd == 'Click':
                self.init_book_keybody_action_click(cunit, kunit)
            elif cmd == 'Goto':
                self.init_book_keybody_action_goto(cunit, kunit)
            elif cmd == 'Select':
                self.init_book_keybody_action_select(cunit, kunit)

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
            self.init_book_keybody_condition(cunit, kunit)
        # Unify the following field to list
        if not isinstance(kunit['Actions'], list):
            kunit['Actions'] = [kunit['Actions']]
        self.init_book_keybody_actions(kunit, kunit['Actions'])

    # Check valid of the source book diction , initial default value
    # Format is as:
    # {
    #     "InferenceName": "",
    #     "Name": "",
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
        # Find cmd files and bcmd files
        # cmd file has own inferecne model
        # bcmd(branch cmd) file will reuse cmd modle
        # cmd file need be loaded before bcmd
        cmdfiles = []
        for root, dirnames, filenames in os.walk(bookpath):
            for filename in fnmatch.filter(filenames, '*.cmd'):
                cmdfiles.append(os.path.join(root, filename))
        bcmdfiles = []
        for root, dirnames, filenames in os.walk(bookpath):
            for filename in fnmatch.filter(filenames, '*.bcmd'):
                bcmdfiles.append(os.path.join(root, filename))
    
        # load cmd/bcmd files
        # cmd file need be loaded before bcmd
        for fname in cmdfiles+bcmdfiles:
            self.logger.info('LOADING book: %s'%(fname))
            fin = open(fname, 'r')
            d = json.load(fin, object_pairs_hook=OrderedDict)
            #d = json.load(fin)
            fin.close()
            infname = d['InferenceName']
            bookname = os.path.basename(fname).split('.')[0].strip()
            assert bookname not in self.gBooks, \
                "book %s in file:%s is duplicated"%(bookname,fname)

            book = {}
            book['InferenceName'] = d['InferenceName']
            book['Name'] = bookname
            if infname in self.gBooks:
                self.logger.debug("book %s in file:%s using existing inference:%s"%(bookname,fname,infname))
                book['Label2ID'] = self.gBooks[infname]['Label2ID']
                book['ID2Label'] = self.gBooks[infname]['ID2Label']
                book['Detector'] = self.gBooks[infname]['Detector']

            else:
                # load label map
                label2id_map = label_map_util.get_label_map_dict(d['LabelMapFile'])
                id2label_map = {}
                for key in label2id_map.keys():
                    val = label2id_map[key]
                    id2label_map[val] = key
                book['Label2ID'] = label2id_map
                book['ID2Label'] = id2label_map
                # load a detector
                detectorName = self.gDevice.ip+'-'+bookname
                book['Detector'] = Detector(detectorName, d['InferenceFile'], d['LabelMapFile'])

            self.init_book(d)
            book['Sequence'] = d['Sequence']
            # How much jobs already done in this book
            book['JobClear'] = 0.0
            self.gBooks[bookname] = book

    def check_conditions(self, bookname, conditions, tagsDetail, tagsFound):
        # Check conditions is ok or not.
        book = self.gBooks[bookname]
        self.logger.debug('Check condition in book:[%s], conditions:[%s]'\
                    %(bookname, conditions))
        disallow_result = False
        allow_result = False
        job_forbid = False
        for cond in conditions:
            if disallow_result:
                break
            if job_forbid:
                break
            tagsNew = self.tagsAdjustByArea(tagsFound, cond['FocusArea'])
            for job in cond['Jobs']:
                if job_forbid:
                    break
                if not eval(str(book['JobClear']) + job['ClearedExpr']):
                    job_forbid = True
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
                    if not tag in tagsNew:
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
                    if tag in tagsNew:
                        allow_num += 1
                        taglist.append(tag)
                self.logger.debug('tag require:%d/100 of %s'%(100*allow[u'Percent'], allow[u'Tags']))
                self.logger.debug('tag detect: %s'%(str(taglist)))
                if(allow_num >= allow_num_req):
                    allow_result = True
                    break
        if job_forbid or disallow_result or not allow_result:
            self.logger.debug('Condition is not ready, job_forbid:%s, \
                               disallow_result:%s, allow_result:%s'\
                               %(job_forbid,disallow_result,allow_result))
            return False
        # conditions is ok
        self.logger.debug('Conditions is ready...')
        return True
            
    
    def decision_do(self, tagsDetail, bookname, tagsFound):
        jobUpdated = False
        book = self.gBooks[bookname]
        # record the bunit which need to adjust sequence
        for bunit in book['Sequence']:
            kunit2move = {}
            for kunit in bunit['KeyBody']:
                # Loop the book keybody
                self.logger.debug('Loop the book:%s, sequence:%s, keybody:%s'\
                            %(bookname, bunit[u'Name'],kunit[u'Name']))
                if not self.check_conditions(bookname, kunit['Conditions'], tagsDetail, tagsFound):
                    # adjust priority of the current condition unit, put it to end of list
                    # it is very dangours to change multiple list member at same time
                    # so i just change one at one time
                    if not kunit2move:
                        kunit2move = kunit
                    continue
                # kunit condition is ok, do the action.
                jobUpdated = self.do_actions(bookname, kunit['Actions'], tagsDetail, tagsFound)
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
            
    # do one action
    # NOTE: this function can be nested called when subactions inside action
    def do_action(self, bookname, action, tagsDetail, tagsFound, idx=0):
        jobUpdated = False
        self.logger.debug('entering action: %s'%(str(action)))
        # check whether need to preload the data
        if action['PreloadTime'] != 0:
            print 'pre reload', action['PreloadTime']
            time.sleep(action['PreloadTime']/1000)
            newDetail, newFound, err = self.imgDetect(self.gBooks[bookname])
            if not newFound:
                self.logger.debug('DETECT: reload img of book:%s do not detect any tags'%(bookname))
                # this should not happen
                tagsDetail = {}
                tagsFound = {}
            #NOTE: python need replace key one by one, otherwise the new value 
            # will lost when out of this function scope
            for key in newDetail: tagsDetail[key] = newDetail[key]
            for key in newFound: tagsFound[key] = newFound[key]
        if action[u'Command'] == u'Click':
            temp = self.do_action_click(bookname, action, tagsDetail, tagsFound, idx)
            if temp == True:
                jobUpdated = True
        elif action[u'Command'] == u'Goto':
            temp = self.do_action_goto(bookname, action, tagsDetail, tagsFound)
            if temp == True:
                jobUpdated = True
        elif action[u'Command'] == u'Select':
            temp = self.do_action_select(bookname, action, tagsDetail, tagsFound)
            if temp == True:
                jobUpdated = True
        else:
            self.logger.info('DO ACTION:%s, PARAM:this action is tbd..., BODY:%s'\
                            %(action['Command'],str(action)))
        # Nested call 'SubActions'
        if 'SubActions' in action:
            subActions = action['SubActions']
            self.logger.debug('entering subActions: %s'%(subActions))
            for subAction in subActions:
                # Any one of subaction can change status of jobUpdated
                temp = self.do_action(bookname, subAction, tagsDetail, tagsFound)
                if temp == True:
                    jobUpdated = True
        # check whether need to postload the data
        if action['PostloadTime'] != 0:
            print 'post reload', action['PostloadTime']
            time.sleep(action['PostloadTime']/1000)
            newDetail, newFound, err = self.imgDetect(self.gBooks[bookname])
            if not newFound:
                self.logger.debug('DETECT: reload img of book:%s do not detect any tags'%(bookname))
                # this should not happen
                tagsDetail = {}
                tagsFound = {}
            #NOTE: python need replace key one by one, otherwise the new value 
            # will lost when out of this function scope
            for key in newDetail: tagsDetail[key] = newDetail[key]
            for key in newFound: tagsFound[key] = newFound[key]
        return jobUpdated

    def do_actions(self, bookname, actions, tagsDetail, tagsFound):
        gLastActions = self.gLastActions
        jobUpdated = False
        num = len(actions)
        self.logger.debug('entering actions: %s'%(actions))
        for idx in range(num):
            action = actions[idx]
            current_time = time.time()
            # check whether action is too frequce
            if len(gLastActions) > idx:
                if gLastActions[idx] and gLastActions[idx]['Action'] == action:
                    delta = (current_time - gLastActions[idx]['Time'])*1000
                    decision_period = float(action[u'DecisionPeriod'])
                    if(delta < decision_period):
                        self.logger.debug('delay this action since \
                            delta:%f < decision period:%f'%(delta, decision_period))
                        jobUpdated = True
                        continue
            # update last action record
            gLastActions[idx] = { 'CurrentBook':bookname,
                                  'Time' : time.time(),
                                  'Action': action,
                                  'Command':action['Command']
                                }
            # call one action from actions list
            # Any one of action can change jobUpdated to true
            temp = self.do_action(bookname, action, tagsDetail, tagsFound)
            if temp == True:
                jobUpdated = True
        return jobUpdated
            
    def do_action_goto(self, current_book, action, tagsDetail, tagsFound):
        jobUpdated = False
        # Nested call decision_loop('GotoBook')
        # If the 'GotoBook' find nothing, will come back to UpperBook.
        target_book = action[u'BookName']
        param = 'From book:%s goto book:%s'%(current_book, target_book)
        self.logger.info('DO ACTION:Goto, PARAM:%s, BODY:%s'\
                        %(param, action))
        jobUpdated = self.decision_loop(target_book)
        param = 'End Loop inside book: %s, back to:%s'%(target_book, current_book)
        self.logger.info('DO ACTION:GoBack, PARAM:%s'%(param))
        return jobUpdated

    def do_action_select(self, bookname, action, tagsDetail, tagsFound):
        jobUpdated = False
        leftestChecked = False
        # action['Select'] will re-use Click action function
        #NOTE: PreloadTime MUST be 0 before call Click action
        # Otherwise pre-sorted tagsDetail/tagsFound will be overwrited.
        cliAction = copy.deepcopy(action)
        cliAction['Command'] = 'Click'
        cliAction['PreloadTime'] = 0
        # Compare latest N image, if they are all similar, quit.
        N = 5
        SIMILAR = 20.0
        simiTimes = 0
        imLast = None
        for i in range(CLICK_TIME_OF_SELECT_ACTION_MAX):
            # sort tagsFound according to SelectToArea
            # do_action will change tagsFound at each call
            # default sorting method will be: 
            # current --> leftest-->righter-->righter-->...->rightest
            # e.g. there are tags which has following center x=(x2-x1)/2
            #      tags = {a:[0.4], b:[0.45], c:[0.5], d:[0.55], e:[0.6]}
            #      c will be selcted to check, since SelectToArea = [0.4, 0.6]
            #      a will be next since it is leftest
            #      after round1: {a:[0.5], b:[0.55], c:[0.6], d:[0.65], e:[0.7]}
            #      b will be next since it is righter
            #      after round2: {a:[0.45], b:[0.5], c:[0.55], d:[0.6], e:[0.65]}
            #      c will be next since it is righter
            #      after round3: {a:[0.4], b:[0.45], c:[0.5], d:[0.55], e:[0.6]}
            #      d will be next since it is righter
            #      after round4: {a:[0.35], b:[0.4], c:[0.45], d:[0.5], e:[0.55]}
            #      e will be next and last since it is rightest
            # Check JudgeConditions
            judgeConditions = action['JudgeConditions']
            self.logger.debug('check JudgeConditions: %s'%(judgeConditions))
            jobUpdated = self.check_conditions(bookname, judgeConditions, tagsDetail, tagsFound)
            if jobUpdated:
                param = 'Found a satisfied tag'
                self.logger.info('DO ACTION:Select, PARAM:%s, BODY:%s'\
                                %(param, action))
                return jobUpdated
            # Check whether new image is same as last N images
            if imLast:
                im = tagsDetail['image_np']
                diff = imdiff.diffByHistogram(im, imLast, tagsDetail['image_size'])
                if diff <= SIMILAR:
                    self.logger.debug('click get %d similar image, diff: %f'%(simiTimes, diff))
                    simiTimes = simiTimes+1
                else:
                    simiTimes = 0
            if simiTimes >= N:
                param = 'Click times:%d get %d similar image'%(i, simiTimes)
                self.logger.info('CANCEL ACTION:Select PARAM:%s, BODY:%s'\
                                 %(param, action))
                return False
            imLast = tagsDetail['image_np']
            # Go and find next one to be selected
            area = action['SelectToArea']
            weight = {}
            startPos = -1
            labelName = action['StartTag'][0]
            if labelName not in tagsFound:
                self.logger.debug('can not find any label:%s from tag:%s inside area:%s'%(labelName, tag, area))
                break
            tag = tagsFound[labelName]
            # Find the start position
            for box in tag['boxes']:
                i = tag['boxes'].index(box)
                weight[i] = sum(box)
                if self.boxInsideArea(box, area):
                    self.logger.debug('find label:%s in tag[%d]:%s inside area:%s'%(labelName, i, tag, area))
                    startPos = i
            if startPos <0:
                self.logger.debug('can not find any label:%s from tag:%s inside area:%s'%(labelName, tag, area))
                break
            # sort tags from left to right
            sorted_weight = sorted(weight, key=weight.get)
            # get sorted position of startPos
            startPosIdx = sorted_weight.index(startPos)
            # do we need go leftest first
            if leftestChecked == False:
                # check if startPos itself is the leftest
                if startPosIdx == 0:
                    # yes, it is the leftest, the next will be just righter one
                    nextPosIdx = startPosIdx + 1
                    # go righter from now on
                    leftestChecked = True
                else:
                    # no, use the leftest as the next
                    nextPosIdx = 0
            else:
                # find the righter one as the next
                nextPosIdx = startPosIdx + 1
            if nextPosIdx >= len(sorted_weight):
                # All tag are seleted once
                break
            nextPos = sorted_weight[nextPosIdx]
            param = 'Click times:%d, startPos:%d, nextPos:%d, tag:%s'\
                    %(i, startPos, nextPos, tag)
            self.logger.info('DO ACTION:Select PARAM:%s, BODY:%s'\
                             %(param, action))
            self.do_action(bookname, cliAction, tagsDetail, tagsFound, nextPos)
        param = 'Click times:%d exceed MAX:%s, or all tags are slected but not found'\
                %(i, CLICK_TIME_OF_SELECT_ACTION_MAX)
        self.logger.info('CANCEL ACTION:Select PARAM:%s, BODY:%s'\
                         %(param, action))
        return False



    def do_action_click(self, current_book, action, tagsDetail, tagsFound, idx=0):
        # Always need to updated if click ready
        jobUpdated = True
        im_width, im_height = tagsDetail['image_size']

        #find click start point where first StartTag[...] match
        start_key = ''
        for key in action[u'StartTag']:
            if key in tagsFound:
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
        rymin,rxmin,rymax,rxmax = tagsFound[start_key]['boxes'][idx]
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
            if key in tagsFound:
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
            rymin,rxmin,rymax,rxmax = tagsFound[end_key]['boxes'][idx]
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
        self.gDevice.swipe(xstart, ystart, xend, yend, duration)
        param = {'start_key':start_key,'xstart':xstart,'ystart':ystart,\
                 'end_key':end_key,'xend':xend,'yend':yend,'duration':duration}
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

    def boxInsideArea(self, box, area):
        # NOTE: sequence in cmd book is not same as in tensorflow
        ry1,rx1,ry2,rx2 = box
        rxmin,rymin,rxmax,rymax = area
        return (rx1>=rxmin and ry1>=rymin and rx2<=rxmax and ry2<rymax)
        

    def tagsAdjustByArea(self, tagsFound, area):
        tagsNew = {}
        for labelName in tagsFound:
            tag = tagsFound[labelName]
            for box in tag['boxes']:
                i = tag['boxes'].index(box)
                if self.boxInsideArea(box, area):
                    if not labelName in tagsNew:
                        tagsNew[labelName] = {
                            'poses':[],'scores':[],'boxes':[]}
                    tagsNew[labelName]['poses'].append(tag['poses'][i])
                    tagsNew[labelName]['scores'].append(tag['scores'][i])
                    tagsNew[labelName]['boxes'].append(tag['boxes'][i])
        return tagsNew


    def imgDetect(self, book):
        tagsDetail = {}
        #store the detected tags summerized info
        tagsFound = {}
        self.getDelta("Before Call getNumpyData")
        err, image_size, img_np = self.gDevice.getNumpyData()
        self.logger.debug('DETECT: getNumpyData used:%s seconds, image size:%s'\
                        %(self.getDelta(),image_size))
        if err:
            self.logger.warn('DETECT: getNumpyData failed,error:%s'%(err))
            return tagsDetail, tagsFound, err
        self.getDelta("Before Call detection")
        (image_np, tag_boxes, tag_scores, tag_classes, tag_num) = book['Detector'].detect(img_np)
        self.logger.debug('DETECT: inference name:%s, detect used:%s seconds'\
                            %(book['InferenceName'], self.getDelta()))
        tagsDetail = {'image_size':image_size,
                      'image_np':image_np,
                      'tag_boxes':tag_boxes,
                      'tag_scores':tag_scores,
                      'tag_classes':tag_classes,
                      'tag_num':tag_num}
        #box should have minimun 80% possibility
        min_score_thresh = .8
        for i in range(tag_num):
            labelName = book['ID2Label'][tag_classes[i]]
            if(tag_scores[i]<min_score_thresh): 
                break 
            if not labelName in tagsFound:
                tagsFound[labelName] = {
                    'poses':[],'scores':[],'boxes':[]}
            tagsFound[labelName]['poses'].append(i)
            tagsFound[labelName]['scores'].append(tag_scores[i])
            tagsFound[labelName]['boxes'].append(tag_boxes[i])

        self.logger.debug('DETECT: found tags:%s'%(tagsFound.keys()))
        self.logger.debug('DETECT: tags info:%s'%(tagsFound))
        return tagsDetail, tagsFound, err

    def decision_loop(self, bookname=u'Index'): 
        jobUpdated = False
        if not bookname in self.gBooks:
            self.logger.warn('book:%s do not exist'%(bookname))
            return jobUpdated
        book = self.gBooks[bookname]
        while True:
            self.logger.info('===============START ACTION: Loop inside book: %s============'%(bookname))

            tagsDetail, tagsFound, err = self.imgDetect(book)
            if err:
                self.logger.warn('DETECT: imgDetect failed, \
                                  sleep 5s, error:%s'%(err))
                time.sleep(5)
                continue

            if not tagsFound:
                self.logger.debug('DETECT: book:%s do not detect any tags'%(bookname))
                #subbook will be terminated
                if(bookname!=u'Index'):
                    break
                #Index book will be conitnued
                time.sleep(1)
                continue

            jobUpdated = self.decision_do(tagsDetail, bookname, tagsFound)
            #subbook will be terminated if meet with incorrect decision
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
                if self.jobIsAllClear():
                    break
            # Continue to next round.
            jobUpdated = False
            time.sleep(1)
        return jobUpdated






