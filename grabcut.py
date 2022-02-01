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

def rect_mask(to_process, to_show, mask, repeat_op=False):
  cv2.destroyAllWindows()
  bgdModel = np.zeros((1,65), np.float64)
  fgdModel = np.zeros((1,65), np.float64)
  if not repeat_op:
    roi = ROI(to_show.copy(), name='RECTANGLE: press \'r\' to reset, \'c\' to confirm')
    rect, success = roi.get_mask()
  if repeat_op or success:
    cv2.grabCut(to_process, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
  return

def freehand_mask(to_process, to_show, mask, repeat_op=False):
  cv2.destroyAllWindows()
  bgdModel = np.zeros((1,65), np.float64)
  fgdModel = np.zeros((1,65), np.float64)
  if not repeat_op:
    roi = FGBG(to_show.copy(), name='FREEHAND: press \'r\' to reset, \'c\' to confirm \'b\' for BG, \'f\' for FG, \'u\' for undo')
    fmask, success = roi.get_mask()
    if success:
      mask[fmask == cv2.GC_BGD] = cv2.GC_BGD
      mask[fmask == cv2.GC_FGD] = cv2.GC_FGD
    if repeat_op or success:
      cv2.grabCut(to_process, mask, None, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)
  return

def final(mask):
  out = np.where((mask==1)+(mask==3), 255, 0).astype(np.uint8)
  return out

def process(img):
  clone = img.copy()
  mask  = np.zeros(img.shape[:2], np.uint8) + cv2.GC_PR_BGD 
  prev  = None
  window_title = 'Satisfied?: \'r\': rect, \'f\': freehand, \'c\': continue previous \'Esc\': quit'
  cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
  while(1):
    output = mask_overlay(img, final(mask))
    cv2.imshow(window_title, output)
    k = cv2.waitKey(1)
    if k != 27 and k != ord('r') and k != ord('f') and k != ord('c'):
      continue
    elif k == 27:
      break
    elif k == ord('r'):
      rect_mask(clone, output, mask)
      prev = rect_mask
    elif k == ord('f'):
      freehand_mask(clone, output, mask)
      prev = freehand_mask  
    elif k == ord('c') and prev is not None:
      prev(clone, output, mask, repeat_op=True)
  cv2.destroyAllWindows()
  return final(mask)


def main(img, scale):
  h, w = img.shape[:2]
  if scale != 1:
    sh, sw = int(scale*h), int(scale*w)
    print('Processing at size ({}, {})'.format(sw, sh))
    input = cv2.resize(img, (sw, sh))
    mask  = process(input)
    mask  = cv2.resize(mask, (w, h), cv2.INTER_NEAREST)
  else:
    mask  = process(img)
  return mask


def mask_overlay(img, mask, color=(0, 255, 0)):
  out = img.copy()
  color = np.array(color, dtype=np.float32)
  vals = img[mask>0].astype(np.float32)*0.5 + color*0.5
  out[mask>0] = vals.astype(np.uint8)
  return out


def imshow(name, img):
  cv2.namedWindow(name, cv2.WINDOW_NORMAL)
  cv2.imshow(name, img)


if __name__=='__main__':
  args = get_args()
  img  = cv2.imread(args.image, cv2.IMREAD_COLOR)
  if img is None:
    print('Unable to load image \'{}\'. Quitting.'.format(args.image))
    exit()
  mask = main(img, args.scale)
  op   = mask_overlay(img, mask)
  if args.output is None or args.output == '':
    imshow('input', img)
    imshow('output', op)
    cv2.waitKey(0)
  else:
    cv2.imwrite(args.output, mask)
    cv2.imwrite(args.output+'_seg.png', op)
    print('Output saved to \'{}\''.format(args.output))

