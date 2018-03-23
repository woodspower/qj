# -*- coding: utf-8 -*-
import os
import sys, getopt
import re
import logging
logging.basicConfig(filename='command.log', 
                    format='%(asctime)s %(levelname)-6s %(name)-12s %(message)s',
                    datafmt='%m-%d%H:%M:%S',
                    level=logging.DEBUG)
import time

from decision import Decisionor
from device import Device



def main(argv):
    gDeviceIPs = []
    logger = logging.getLogger('robot')
    logger.setLevel(logging.DEBUG)

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
            gDeviceIPs = arg.strip().split(', ')
            break
                
    if not gDeviceIPs:
        devs = Device('qj', '')
        gDeviceIPs = devs.getAll()
        if not gDeviceIPs:
            print 'No device found'
            sys.exit()

    for ip in gDeviceIPs:
        try:
            pid = os.fork()
        except OSError:
            exit("Could not create a child process")
        if pid == 0:
            print("In child process:%s, dev is:%s"%(format(pid),ip))
            logger.info('NEW DEVICE: process-device pair: (%s, %s)'%(format(pid), ip))
            device = Device('qj', ip)
            decisionor = Decisionor(device, 'qj_book')
            decisionor.decision_loop()
            exit()

    print("In the parent process after forking the child {}".format(pid))
    finished = os.waitpid(0, 0)
    print(finished)



if __name__ == "__main__":
    main(sys.argv[1:])

