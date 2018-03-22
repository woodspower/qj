# -*- coding: utf-8 -*-
import os
import sys, getopt
import re
import logging
import time

from decision import Decisionor
from device import Device



def main(argv):
    global gDeviceIp

    try:
        opts, args = getopt.getopt(argv, "hd:",["device="])
    except getopt.GetoptError:
        print getopt.GetoptError
        print 'decision.py -d <device_ip>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print 'decision.py -d <device_ip>'
            sys.exit()
        elif opt in ("-d", "--device"):
            gDeviceIp = arg
            break
                
    if not gDeviceIp:
        print 'please input a device ip'
        cmd = '/opt/genymobile/genymotion/tools/adb devices'
        os.system(cmd)
        sys.exit()

    logging.basicConfig(filename='command-%s.log'%(gDeviceIp), level=logging.DEBUG)
    device = Device('qj', gDeviceIp)
    decisionor = Decisionor(device, 'qj_book')
    decisionor.decision_loop()


if __name__ == "__main__":
    main(sys.argv[1:])

