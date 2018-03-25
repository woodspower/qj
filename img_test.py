import time
import os

import cv2
import mss
import numpy
import struct
import pyscreenshot as ImageGrab
from PIL import Image

TEST_TIME=5

import subprocess
def pull_screenshot_direct():
#    ret = os.system('/opt/genymobile/genymotion/tools/adb shell screencap -p /sdcard/snapshot.png')
#    ret = os.system('/opt/genymobile/genymotion/tools/adb pull /sdcard/snapshot.png %s'%(IMAGE_FILE))
    fps = 0
    last_time = time.time()
    title = '[ADB.ImageGrab] FPS benchmark'

    while time.time() - last_time < TEST_TIME:
        # raw data format from adb:
        # 4Bytes(width) + 4Bytes(heigh) + 4Bytes(format) + ...N*4Bytes(each byte is a bitmap:RGBA)
        # fp = os.popen("/opt/genymobile/genymotion/tools/adb exec-out screencap")
        proc = subprocess.Popen(["/opt/genymobile/genymotion/tools/adb","exec-out","screencap"], \
                                stdout=subprocess.PIPE)
        (out,err) = proc.communicate()
        if err:
            print err
            sleep(1)
            continue
        head = out[:12]
        w,h,ft = struct.unpack_from('3i',head)
        data = out[12:]
        assert(len(data) == w*h*4)
        img = numpy.asarray(struct.unpack_from('%dB'%(w*h*4), data), dtype=numpy.uint8).reshape([h,w,4])
#        img = numpy.zeros([h,w,4])
#        img[:,:100] = [0, 0, 255, 255]
        fps += 1
        cv2.imshow(title, img)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
    return fps

IMAGE_FILE = 'test.png'
def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return numpy.array(image.getdata()).reshape(
      (im_height, im_width, 4)).astype(numpy.uint8)

def pull_screenshot_file():
    fps = 0
    last_time = time.time()
    title = '[ADB.ImageGrab] FPS benchmark'

    while time.time() - last_time < TEST_TIME:
        # raw data format from adb:
        # 4Bytes(width) + 4Bytes(heigh) + 4Bytes(format) + ...N*4Bytes(each byte is a bitmap:RGBA)
        # fp = os.popen("/opt/genymobile/genymotion/tools/adb shell screencap | sed 's/\r$//'")
        os.system('/opt/genymobile/genymotion/tools/adb shell screencap -p /sdcard/snapshot.png')
        os.system('/opt/genymobile/genymotion/tools/adb pull /sdcard/snapshot.png %s'%(IMAGE_FILE))
        image_origin = Image.open(IMAGE_FILE)
        image = load_image_into_numpy_array(image_origin)

        fps += 1
        cv2.imshow(title, image)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
#        cv2.imshow(title, img)
#        if cv2.waitKey(25) & 0xFF == ord('q'):
#            cv2.destroyAllWindows()
#            break
    return fps

def screen_record():

    # 800x600 windowed mode
    mon = (0, 40, 800, 640)

    title = '[PIL.ImageGrab] FPS benchmark'
    fps = 0
    last_time = time.time()

    while time.time() - last_time < TEST_TIME:
        img = numpy.asarray(ImageGrab.grab(bbox=mon))
        fps += 1

#        cv2.imshow(title, cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
#        if cv2.waitKey(25) & 0xFF == ord('q'):
#            cv2.destroyAllWindows()
#            break

    return fps


def screen_record_efficient():
    # 800x600 windowed mode
    mon = {'top': 40, 'left': 0, 'width': 800, 'height': 640}

    title = '[MSS] FPS benchmark'
    fps = 0
    sct = mss.mss()
    last_time = time.time()

    while time.time() - last_time < TEST_TIME:
        img = numpy.asarray(sct.grab(mon))
        fps += 1

        cv2.imshow(title, img)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

    return fps


print('CAPDIRECT:', pull_screenshot_direct())
#print('CAPFILE:', pull_screenshot_file())
#print('MSS:', screen_record_efficient())
#print('PIL:', screen_record())
