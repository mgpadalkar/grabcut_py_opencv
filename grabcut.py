import argparse
import numpy as np
import cv2

from draw_rect import ROI
from draw_freehand import FGBG

# construct the argument parser and parse the arguments
def get_args():
  ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
  description='Demo for GrabCut in OpenCV.')
  ap.add_argument("-i", "--image", type=str, default='', help="Path to the input image")
  ap.add_argument("-o", "--output", type=str, default='output.png', help="Path to the output image")
  ap.add_argument("-s", "--scale", type=float, default=1., help="Scale for processing")
  ap.add_argument("-r", "--roi", type=str, choices=['freehand', 'rect'], default='freehand', help="ROI type")
  args = ap.parse_args()
  return args

def mask_overlay(img, mask, color=(0, 255, 0)):
  color = np.array(color, dtype=np.float32)
  vals = img[mask>0].astype(np.float32)*0.5 + color*0.5
  img[mask>0] = vals.astype(np.uint8)
  return img

def process(img, roi_type, scale=1.):
  h, w = img.shape[:2]
  if scale != 1.0:
    sh, sw = int(h*scale), int(w*scale)
    img = cv2.resize(img, (sw, sh), cv2.INTER_CUBIC)
    print('Processing at size ({}, {})'.format(sw, sh))
  # init
  bgdModel = np.zeros((1,65),np.float64)
  fgdModel = np.zeros((1,65),np.float64)
  if roi_type == 'rect':
    # get roi
    roi = ROI(img.copy())
    rect = roi.get_mask()
    mask = np.zeros(img.shape[:2],np.uint8)
    # apply algo
    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
  else:
    roi = FGBG(img.copy())
    mask = roi.get_mask()
    cv2.grabCut(img, mask, None, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)
  # get output
  mask2 = np.where((mask==1)|(mask==3),255,0).astype('uint8')
  if scale != 1.:
    mask2 = cv2.resize(mask2, (w, h), cv2.INTER_NEAREST)
  return mask2
  
def imshow(name, img):
  cv2.namedWindow(name, cv2.WINDOW_NORMAL)
  cv2.imshow(name, img)

def main(img, roi_type, scale, output):
  mask = process(img.copy(), roi_type, scale)
  op   = mask_overlay(img, mask)
  if output is None or output == '':
    imshow('input', img)
    imshow('output', op)
    cv2.waitKey(0)
  else:
    cv2.imwrite(output, mask)
    cv2.imwrite(output+'_seg.png', op)
    print('Output saved to \'{}\''.format(output))

if __name__=='__main__':
  args = get_args()
  img  = cv2.imread(args.image, cv2.IMREAD_COLOR)
  if img is None:
    print('Unable to load image \'{}\'. Quitting.'.format(args.image))
    exit()
  main(img, args.roi, args.scale, args.output)

