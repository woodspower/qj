# -*- coding: utf-8 -*-
import sys, getopt
sys.path.append('..')
import os, fnmatch
import re
import logging
from PIL import Image
import numpy as np
logging.basicConfig(stream=sys.stdout,
                    format='%(asctime)s %(levelname)-6s %(name)-12s %(message)s',
                    datafmt='%m-%d%H:%M:%S',
                    level=logging.DEBUG)
#logging.basicConfig(filename='command.log', 
#                    format='%(asctime)s %(levelname)-6s %(name)-12s %(message)s',
#                    datafmt='%m-%d%H:%M:%S',
#                    level=logging.DEBUG)
import time

from decision import Decisionor
from device import Device

socrCases = [
    {
        "Datas":"./im",
        "Eval": {
            "Inference": "socr",
            "Match": ".*(?P<left>[0-9])/(?P<total>[0-9])",
            "Area": [0.,0.,1.,1.],
            "Checks":"left<total"
        }
    }
]


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
                
    decisionor = Decisionor(None, '../qj_book')

    for case in socrCases:
        decisionor.init_book_keybody_condition_eval(case['Eval'], None)
        path = case['Datas']
        for root, dirnames, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, '*.*pg'):
                im = Image.open(os.path.join(root, filename))
                imNP = np.asarray(im)
                print '==============eval %s========================='%(filename)
                decisionor.evalText(imNP, [case['Eval']])
                #infName = case['Evals']['Inference']
                #detector = decisionor.gDetectors['socr']
                #print '==============using decisionor.imgDetect========================='
                #tagsDetail, tagsFound, err = decisionor.imgDetect(detector, imNP)
                #logger.warn("detect file:%s, using:%s, found tags:%s", filename, 'socr', tagsFound.keys())
            

if __name__ == "__main__":
    main(sys.argv[1:])

