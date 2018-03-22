# -*- coding: utf-8 -*-
import os
import sys, getopt
import re
import logging
import numpy as np
import struct
import subprocess

import json
# use ordereddict to keep key seq of vott file
from collections import OrderedDict


class Device:
    def __init__(self, name, ip):
        self.ip = ip
        self.name = name
        self.tool = "/opt/genymobile/genymotion/tools/adb"

    # return errcode, image_size, image_np
    # image_np is a numpy array of image data which is defined by img_detection.py
    # Data format should be shape of [H, W, 3], 
    # The first dimension is pixel of each Heigh point,
    # The second dimension is pixel of each Width point,
    # The last dimension is pixel of is each (R,G,B) point.
    def getNumpyData(self):
        ip = self.ip
        tool = self.tool
        # raw data format from adb:
        # 4Bytes(width) + 4Bytes(heigh) + 4Bytes(format) + ...N*4Bytes(each byte is a bitmap:RGBA)
        # fp = os.popen("/opt/genymobile/genymotion/tools/adb exec-out screencap")
        #ret = os.system('/opt/genymobile/genymotion/tools/adb shell screencap -p /sdcard/snapshot.png')
        #ret = os.system('/opt/genymobile/genymotion/tools/adb pull /sdcard/snapshot.png %s'%(IMAGE_FILE))
        proc = subprocess.Popen([tool,"-s", ip,"exec-out","screencap"], \
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out,err) = proc.communicate()
        if err:
            #print('Error when getNumpyData:%s'%(err))
            return err, (), []
        head = out[:12]
        # recover data form ctype
        w,h,ft = struct.unpack_from('3i',head)
        data = out[12:]
        if(len(data) != w*h*4):
            #print('data len of getNumpyData:%d, is same as Width*Heigh(%d*%d)'%(len(data),w,h))
            return 'error len:%d, w:%d, h:%d'%(len(data),w,h), (), []
        img = np.asarray(struct.unpack_from('%dB'%(w*h*4), data), dtype=np.uint8).reshape([h,w,4])
        # Change last dimension from (R,G,B,A) to (R,G,B)
        img = np.delete(img, 3, axis=2)
        return '', (w,h), img


    def swipe(self, xstart, ystart, xend, yend, duration):
        # swipe it
        ip = self.ip
        tool = self.tool
        cmd = '%s -s %s shell input swipe %d %d %d %d '%\
                (tool, ip, xstart,ystart,xend,yend) + str(duration)
        os.system(cmd)
        print cmd

