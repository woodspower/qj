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

class Decisionor:
    def __init__(self, device, bookPath):
        self.gStartTime = time.time()
        self.gDevice = device
        self.gBooks = {}
        self.gDetectors = {}
        self.ACTION_NUM_OF_SINGLE_LIST_MAX = 10
        self.RELOAD_TIME_IN_ACTION_LIST_DEFAULT = 1000
        self.SELECT_MAX_CLICK_NUM = 100
        # Compare latest self.DEAD_LOOP_NUM_SIMILAR_IMAGE image, if they are all similar, quit.
        self.DEAD_LOOP_NUM_SIMILAR_IMAGE = 29
        # How much diff of two images will trade as same
        self.DEAD_LOOP_COST_SIMILAR_IMAGE = 20.0
        # How many continous time have been checked
        self.gSimilarTimes = 0
        # Last image numpy data
        self.gLastImage = np.array([])
        # Record every last action in the actions list
        self.gLastActions = [None]*self.ACTION_NUM_OF_SINGLE_LIST_MAX
        # call each init function
        self.logger = logging.getLogger('decision-%s'%(device.ip))
        self.logger.setLevel(logging.DEBUG)
        self.loadInfModels(bookPath)
        self.loadCmdBook(bookPath)

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
    def init_book_keybody_action_goto(self, cunit, kunit=None):
        # Init default value
        tmpl = {
            "Name": "",
            "StopOnFail": "Yes",
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
            "StopOnFail": "Yes",
            "PreloadTime": 0,
            "Command": "Click",
            "PostloadTime": 0,
            "DecisionPeriod": 0,
            "StartTag": [],
            "StartOffset": [0.5, 0.5],
            "EndTag": [],
            "EndOffset": [0.5, 0.5],
            "Duration": "20~50",
            "FocusArea":[0.,0.,1.,1.]
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
            
    # Check valid of the aciton_find diction , init default value
    # Format is as tmpl.
    def init_book_keybody_action_find(self, cunit, kunit):
        # Init default value
        tmpl = {
            "Name": "",
            "StopOnFail": "Yes",
            "PreloadTime": 0,
            "Command": "Find",
            "FocusArea": None,
            "PostloadTime": 1000,
            "DecisionPeriod": 0,
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
        assert num <= self.ACTION_NUM_OF_SINGLE_LIST_MAX, \
            "Actions unit number:%d MUST less than:%d in Action body:%s"\
            %(num,self.ACTION_NUM_OF_SINGLE_LIST_MAX,kunit)
        for cunit in actions:
            cmd = cunit['Command']
            if cmd == 'Click':
                self.init_book_keybody_action_click(cunit, kunit)
            elif cmd == 'Goto':
                self.init_book_keybody_action_goto(cunit, kunit)
            elif cmd == 'Find':
                self.init_book_keybody_action_find(cunit, kunit)

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
        
    def loadInfModels(self, path):
        # Find inf files and init inferecne models
        # Inf files may has constant path string:
        # "Index": {
        #     "InferenceFile": "/data/Index/inference_ssd/frozen_inference_graph.pb",
        #     "LabelMapFile": "/data/Index/pascal_label_map.pbtxt"
        # }
        # or may has variable path string:
        # "Main": {
        #     "InferencePath": "/data",
        #     "InferenceFile": "$InferencePath/$InferenceName/inference_ssd/frozen_inference_graph.pb",
        #     "LabelMapFile": "$InferencePath/$InferenceName/pascal_label_map.pbtxt"
        # }
        # $InferenceName is the key of json body, other variable is definable
        infFiles = []
        for root, dirnames, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, '*.inf'):
                infFiles.append(os.path.join(root, filename))
        # init inference files one by one
        for fname in infFiles:
            self.logger.info('LOADING inference models: %s'%(fname))
            fin = open(fname, 'r')
            datas = json.load(fin)
            fin.close()
            # each key in json dict will be the inference name
            for infName in datas:
                d = datas[infName]
                assert infName not in self.gDetectors, \
                    "inference %s in file:%s is duplicated"%(infName,fname)
                # substitute $VAR with proper string
                d['InferenceName'] = infName
                infFile = self.strSubstitute(d['InferenceFile'], d)
                mapFile = self.strSubstitute(d['LabelMapFile'],d)
                self.logger.info('model file: %s, map file: %s'%(infFile, mapFile))
                # load label map
                label2id_map = label_map_util.get_label_map_dict(mapFile)
                id2label_map = {}
                for key in label2id_map.keys():
                    val = label2id_map[key]
                    id2label_map[val] = key
                self.gDetectors[infName] = {}
                detector = self.gDetectors[infName]
                detector['InferenceName'] = infName
                detector['Label2ID'] = label2id_map
                detector['ID2Label'] = id2label_map
                detector['InferenceFile'] = infFile
                detector['LabelMapFile'] = mapFile
                # create a detector
                detectorName = self.gDevice.ip+'-'+infName
                detector['Detector'] = Detector(detectorName, infFile, mapFile)

    # substitute $VAR with proper string
    # here assume string is a path sting
    # s is the string may include $VAR
    # d is the dict include VAR value
    # e.g. s = '$ROOT/$NAME/test'
    #      d = { 'ROOT':'/data',
    #            'NAME':'leo'}
    #      return:'/data/leo/test'
    def strSubstitute(self, s, d):
        # split elements in path string
        elements = s.split('/')
        if elements[0] == '':
            # path is start with '/'
            out = ['/']
        else:
            out = []
        for e in elements:
            if not '$' in e:
                out.append(e)
            else:
                out.append(eval("d['"+e.strip('$')+"']"))
        return reduce(lambda x,y:os.path.join(x,y),out)

    def loadCmdBook(self, bookpath):
        # Find cmd files and bcmd files
        # cmd file has own inferecne model
        # bcmd(branch cmd) file will reuse cmd modle
        # cmd file need be loaded before bcmd
        # Index.cmd file must exist
        indexfile = ''
        cmdfiles = []
        for root, dirnames, filenames in os.walk(bookpath):
            for filename in fnmatch.filter(filenames, '*.cmd'):
                if filename == 'Index.cmd':
                    indexfile = os.path.join(root, filename)
                else:
                    cmdfiles.append(os.path.join(root, filename))
        # load cmd files
        # indexfile must be the first one, it has default value
        assert indexfile, \
            "Index.cmd not found, which must be provided in %s"%(bookpath)
        for fname in [indexfile]+cmdfiles:
            self.logger.info('LOADING book: %s'%(fname))
            fin = open(fname, 'r')
            d = json.load(fin, object_pairs_hook=OrderedDict)
            #d = json.load(fin)
            fin.close()
            bookname = os.path.basename(fname).split('.')[0].strip()
            assert bookname not in self.gBooks, \
                "book %s in file:%s is duplicated"%(bookname,fname)
            self.gBooks[bookname] = {}
            book = self.gBooks[bookname]
            book['Name'] = bookname
            book['InferenceName'] = d['InferenceName']
            if bookname != book['InferenceName']:
                self.logger.debug("book %s in file:%s using others inference:%s"\
                                  %(bookname,fname,book['InferenceName']))
            # Index.cmd must provide default Popup inference file
            # which is used to detect general popup things
            if 'PopupBook' in d:
                book['PopupBook'] = d['PopupBook']
            else:
                book['PopupBook'] = self.gBooks['Index']['PopupBook']
            self.init_book(d)
            book['Sequence'] = d['Sequence']
            # How much jobs already done in this book
            book['JobClear'] = 0.0

    def checkDeadLoop(self, tagsDetail):
        # Compare latest self.DEAD_LOOP_NUM_SIMILAR_IMAGE image, if they are all similar, quit.
        if self.gLastImage.any():
            im = tagsDetail['image_np']
            diff = imdiff.diffByHistogram(im, self.gLastImage, tagsDetail['image_size'])
            if diff <= self.DEAD_LOOP_COST_SIMILAR_IMAGE:
                self.gSimilarTimes = self.gSimilarTimes+1
                self.logger.debug('Found %d times similar image,latest diff: %f<=%f'\
                                %(self.gSimilarTimes, diff, self.DEAD_LOOP_COST_SIMILAR_IMAGE))
            else:
                self.gSimilarTimes = 0
        if self.gSimilarTimes >= self.DEAD_LOOP_NUM_SIMILAR_IMAGE:
            self.logger.debug('Found %d times similar image,exceed: %d'\
                            %(self.gSimilarTimes, self.DEAD_LOOP_NUM_SIMILAR_IMAGE))
            return True
        self.gLastImage = tagsDetail['image_np']
        return False

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
            # if Job of current book is cleared, return direct
            if book['JobClear'] >= 1.0:
                job_forbid = True
                break
            tagsNew = self.tagsAdjustByArea(tagsFound, cond['FocusArea'])
            # check Job status of other book if required
            for job in cond['Jobs']:
                if job_forbid:
                    break
                if not job['Bookname'] in self.gBooks:
                    self.logger.debug('Book not found when check job condition \
                                       of other book:[%s] in book:[%s], conditions:[%s]'\
                                       %(job['Bookname'], bookname, conditions))
                    continue
                jBook = self.gBooks[job['Bookname']]
                if not eval(str(jBook['JobClear']) + job['ClearedExpr']):
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
#                if allow_num_req == 0:
#                    # At least one tag should be found
#                    allow_num_req = 1
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
        # check wether system is deadloop
        deadLoop = self.checkDeadLoop(tagsDetail)
        if job_forbid or disallow_result or not allow_result:
            self.logger.debug('Condition is not ready, job_forbid:%s, \
                               disallow_result:%s, allow_result:%s'\
                               %(job_forbid,disallow_result,allow_result))
            return False, deadLoop
        # conditions is ok
        self.logger.debug('Conditions is ready...')
        return True, deadLoop
            
    
    # There are three level of excution unit list.
    # Sequence unit list, KeyBody unit list, Action unit list
    # Sequence units will excuted one by one without any condition
    # KeyBody units will excuted ONLY first succeed unit and break
    # KeyBody unit of first non-succeed unit will be adjust to the end
    # Action units will excuted one by one following unit.StopOnFail
    # StopOnFail=='Yes' by default, then:
    # Action units will excuted one by one until met a failed unit
    # Action units will excuted ONLY if keybody condition is satified
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
                condStatus, deadLoop = self.check_conditions(bookname, kunit['Conditions'], tagsDetail, tagsFound)
                if deadLoop:
                    self.logger.warn('DEAD ACTION: Dead Loop book:%s, conditions:%s, \
                                      tagsFound:%s, conditionStatus:%s'\
                        %(bookname, kunit['Conditions'], tagsFound, condStatus))
                    # Dead loop, put this kunit to end and try froce update everything
                    jobUpdated = True
                    kunit2move = kunit
                    break
                if not condStatus:
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
    # param idx is the tag index when multiple tags are exist
    # param isLast means whether this action is the last one of actions list
    # isLast is used to do auto reload between action inside actions list
    def do_action(self, bookname, action, tagsDetail, tagsFound, idx=0, isLast=True):
        jobUpdated = False
        self.logger.debug('entering action: %s'%(str(action)))
        book = self.gBooks[bookname]
        # check whether need to preload the data
        if action['PreloadTime'] != 0:
            self.logger.debug('DETECT: Pre-reload img of book:%s, delay time:%s ms'\
                               %(bookname, action['PreloadTime']))
            time.sleep(action['PreloadTime']/1000.0)
            newDetail, newFound, err = self.imgDetect(self.gDetectors[book['InferenceName']])
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
            temp = self.do_action_goto(bookname, action)
            if temp == True:
                jobUpdated = True
        elif action[u'Command'] == u'Find':
            temp = self.do_action_find(bookname, action, tagsDetail, tagsFound)
            if temp == True:
                jobUpdated = True
        else:
            self.logger.info('DO ACTION:%s, PARAM:this action is tbd..., BODY:%s'\
                            %(action['Command'],str(action)))
        # check and process popup
        # nested call Goto 'PopupBook' book if 'Actions' success
        # do not call popup if it is inside popup book
        if jobUpdated and bookname!=book['PopupBook']:
            self.logger.debug('DETECT: Check popup in book:%s \
                               using PopupInference book:%s \
                               after action:%s'\
                               %(bookname, book['PopupBook'], action))
            # prepare and goto popup book
            # assume popup book name equal to popup inference name
            # WARNING: popup book should not use goto,otherwise it will deadlock 
            tmplAction = {
                "Command": "Goto",
                "BookName": book['PopupBook']
            }
            self.init_book_keybody_action_goto(tmplAction)
            # popup action can not change status of jobUpdated
            self.do_action_goto(bookname, tmplAction)
        # nested call 'SubActions' if 'Actions' success
        if jobUpdated and 'SubActions' in action:
            subActions = action['SubActions']
            num = len(subActions)
            i = 0
            self.logger.debug('entering subActions: %s'%(subActions))
            for subAction in subActions:
                i = i+1
                # subaction can not change status of jobUpdated
                self.do_action(bookname, subAction, tagsDetail, tagsFound, isLast=(i==num))
        # check whether need to postload the data
        # isLast is used to do auto reload between action inside actions list
        # Only the last action would not trigle auto reloadTrue
        reloadTime = action['PostloadTime']
        if reloadTime==0 and not isLast:
            # Force reload between action inside same actions list
            reloadTime = self.RELOAD_TIME_IN_ACTION_LIST_DEFAULT
        if reloadTime != 0:
            self.logger.debug('DETECT: Post-reload img of book:%s, delay time:%s ms'\
                               %(bookname, reloadTime))
            time.sleep(reloadTime/1000.0)
            newDetail, newFound, err = self.imgDetect(self.gDetectors[book['InferenceName']])
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
                        time.sleep((decision_period-delta)/1000.0)
            # update last action record
            gLastActions[idx] = { 'CurrentBook':bookname,
                                  'Time' : time.time(),
                                  'Action': action,
                                  'Command':action['Command']
                                }
            # call one action from actions list
            # Any one of action can change jobUpdated to true
            temp = self.do_action(bookname, action, tagsDetail, tagsFound, isLast=(idx==num-1))
            # Action units will excuted one by one following unit.StopOnFail
            # StopOnFail=='Yes' by default, then:
            # Action units will excuted one by one until met a failed unit
            # Action units will excuted ONLY if keybody condition is satified
            if temp == True:
                jobUpdated = True
            else:
                if action['StopOnFail'] == 'Yes':
                    break
        return jobUpdated
            
    def do_action_goto(self, current_book, action):
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

    def do_action_find(self, bookname, action, tagsDetail, tagsFound):
        leftestChecked = False
        # action['Find'] will re-use Click action function
        #NOTE: PreloadTime MUST be 0 before call Click action
        # Otherwise pre-sorted tagsDetail/tagsFound will be overwrited.
        cliAction = copy.deepcopy(action)
        cliAction['Command'] = 'Click'
        cliAction['PreloadTime'] = 0
        # FocusArea will use SELECT its own
        cliAction['FocusArea'] = [0.,0.,1.,1.]
        for i in range(self.SELECT_MAX_CLICK_NUM):
            # sort tagsFound according to FocusArea
            # do_action will change tagsFound at each call
            # default sorting method will be: 
            # current --> leftest-->righter-->righter-->...->rightest
            # e.g. there are tags which has following center x=(x2-x1)/2
            #      tags = {a:[0.4], b:[0.45], c:[0.5], d:[0.55], e:[0.6]}
            #      c will be selcted to check, since FocusArea = [0.4, 0.6]
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
            condStatus, deadLoop  = self.check_conditions(bookname, judgeConditions, tagsDetail, tagsFound)
            if deadLoop:
                self.logger.warn('DEAD ACTION: (SELECT)Dead Loop in book:%s, judgeConditions:%s, \
                                  tagsFound:%s, conditionStatus:%s'\
                    %(bookname, judgeConditions, tagsFound, condStatus))
                # Dead loop, try froce update everything
                return True
            if condStatus:
                param = 'Found a satisfied tag'
                self.logger.info('DO ACTION:Find, PARAM:%s, BODY:%s'\
                                %(param, action))
                return True
            # Go and find next one to be selected
            area = action['FocusArea']
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
            self.logger.info('DO ACTION:Find PARAM:%s, BODY:%s'\
                             %(param, action))
            # force the isLast==False, this will force reload after each action
            self.do_action(bookname, cliAction, tagsDetail, tagsFound, nextPos, isLast=False)
        param = 'Click times:%d exceed MAX:%s, or all tags are slected but not found'\
                %(i, self.SELECT_MAX_CLICK_NUM)
        self.logger.info('CANCEL ACTION:Find PARAM:%s, BODY:%s'\
                         %(param, action))
        return False



    def do_action_click(self, current_book, action, tagsDetail, tagsFound, idx=0):
        # Always need to updated if click ready
        jobUpdated = True
        im_width, im_height = tagsDetail['image_size']
        tagsNew = self.tagsAdjustByArea(tagsFound, action['FocusArea'])

        #find click start point where first StartTag[...] match
        start_key = ''
        for key in action[u'StartTag']:
            if key in tagsNew:
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
        rymin,rxmin,rymax,rxmax = tagsNew[start_key]['boxes'][idx]
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
            if key in tagsNew:
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
            rymin,rxmin,rymax,rxmax = tagsNew[end_key]['boxes'][idx]
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
        # if area is full size, do not need do anything
        if not area or area==[0.,0.,1.,1.]:
            return tagsFound
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
        self.logger.debug('DETECT: Adjust tags from:%s to:%s by area:%s'\
                        %(tagsFound, tagsNew, area))
        return tagsNew


    def imgDetect(self, detector):
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
        (image_np, tag_boxes, tag_scores, tag_classes, tag_num) = detector['Detector'].detect(img_np)
        self.logger.debug('DETECT: inference name:%s, detect used:%s seconds'\
                            %(detector['InferenceName'], self.getDelta()))
        tagsDetail = {'image_size':image_size,
                      'image_np':image_np,
                      'tag_boxes':tag_boxes,
                      'tag_scores':tag_scores,
                      'tag_classes':tag_classes,
                      'tag_num':tag_num}
        #box should have minimun 80% possibility
        min_score_thresh = .8
        for i in range(tag_num):
            labelName = detector['ID2Label'][tag_classes[i]]
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

            tagsDetail, tagsFound, err = self.imgDetect(self.gDetectors[book['InferenceName']])
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
                # switching between books need double check, so Index book cannot break directly
                if(bookname!='Index'):
                    self.jobClear(bookname)
                    self.logger.debug('DETECT: book:%s do not satify any condition,wrong book or job clear:[%f].'\
                                    %(bookname, self.gBooks[bookname]['JobClear']))
                    break
                # It has been double checked 
                if self.jobIsAllClear():
                    break
            # Continue to next round.
            jobUpdated = False
            time.sleep(1)
        return jobUpdated






