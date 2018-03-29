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
        self.name = name + '-' + ip
        self.tool = "/opt/genymobile/genymotion/tools/adb"
        self.logger = logging.getLogger('device-%s'%(ip))
        self.logger.setLevel(logging.DEBUG)

    # List all devices, and return a device ip list
    def getAll(self):
        tool = self.tool
        proc = subprocess.Popen([tool,"devices"], \
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # The output format is as:
        # 'List of devices attached\n192.168.56.102:5555\tdevice\n192.168.56.101:5555\tdevice\n\n'
        (out,err) = proc.communicate()
        if err:
            self.logger.error('Error when call device.getall:%s'%(err))
            return []
        ipList = []
        # lines = ['List of devices attached', '192.168.56.102:5555\tdevice', '192.168.56.101:5555\tdevice', '', '']
        lines = re.split('\n', out)
        # line = ['192.168.56.101:5555\tdevice']
        for line in lines:
            # dev = ['192.168.56.101:5555','device']
            dev = re.split('\t', line)
            if len(dev)==2 and dev[1]=='device':
                ipList.append(dev[0].split(':')[0])
        self.logger.debug('Get ipList:%s'%(ipList))
        return ipList

    # return errcode, image_size, image_np
    # image_np is a numpy array of image data which is defined by detect.py
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
            self.logger.error('Failed getNumpyData:%s'%(err))
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
        self.logger.debug(cmd)

