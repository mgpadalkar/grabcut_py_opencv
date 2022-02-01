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
  args = ap.parse_args()
  return args


class SegmentGC(object):
  def __init__(self, img, scale=1.0):
    self.img_big = img
    self.h, self.w   = img.shape[:2]
    self.sh, self.sw = [int(i*scale) for i in img.shape[:2]]
    self.color   = {'FGD': (0, 255, 0), 'BGD': (0, 0, 255), 'PR_FGD': (127, 255, 127), 'PR_BGD': (0, 0, 127), 'RECT': (255, 0, 0)} 
    self.key     = {'BGD': 0, 'FGD': 1, 'PR_BGD': 2, 'PR_FGD': 3, 'RECT': -1}
    self.mode    = 'FGD'
    self.is_rect = False
    self.window_title = '\'0\': BGD, \'1\': FGD, \'2\': PR_BGD, \'3\': PR_FGD, \'c\': confirm, \'u\': undo last, \'r\': reset, \'s\': segment'
    self.thickness = 3

  def reset(self, ):
    if hasattr(self, 'img'): delattr(self, 'img')
    if hasattr(self, 'masks'): delattr(self, 'mask')
    if hasattr(self, 'ref'): delattr(self, 'ref')
    self.img   = cv2.resize(self.img_big, (self.sw, self.sh))
    self.clone = self.img.copy()
    self.mask  = np.zeros((self.sh, self.sw), np.uint8) + cv2.GC_PR_BGD
    self.xy    = ()
    self.rect  = ()
    self.drawing_rect = False
    self.drawing_line = False
    if hasattr(self, 'prev_img'): delattr(self, 'prev_img')
    if hasattr(self, 'prev_mask'): delattr(self, 'prev_mask')
    return

  def undo(self, ):
    if hasattr(self, 'prev_img'):
      self.img = self.prev_img.copy()
      delattr(self, 'prev_img')
    if hasattr(self, 'prev_mask'):
      self.mask = self.prev_mask.copy()
      delattr(self, 'prev_mask')
    return

  def mouse_callback(self, event, x, y, flags, param):
    if event == cv2.EVENT_RBUTTONDOWN:
      self.drawing_rect = True
      self.xy   = (x, y)
      self.rect = ()
      self.is_rect = True
    elif event == cv2.EVENT_MOUSEMOVE and self.drawing_rect:
      self.img = self.clone.copy()
      x0, y0 = self.xy
      cv2.rectangle(self.img, (x0, y0), (x, y), self.color['RECT'], self.thickness)
      self.rect = (min(x, x0), min(y, y0), abs(x-x0), abs(y-y0))
    elif event == cv2.EVENT_RBUTTONUP and self.drawing_rect:
      self.drawing_rect = False
      x0, y0 = self.xy
      cv2.rectangle(self.img, (x0, y0), (x, y), self.color['RECT'], self.thickness)
      self.rect = (min(x, x0), min(y, y0), abs(x-x0), abs(y-y0))
      self.xy = ()
      print('Press \'s\' for segmentation')

    elif event == cv2.EVENT_LBUTTONDOWN:
      if len(self.rect) == 0:
        print('Select a rectangle first')
        return
      self.is_rect = False
      self.drawing_line = True
      self.xy = (x, y)
      self.prev_img  = self.img.copy()
      self.prev_mask = self.mask.copy()
    elif event == cv2.EVENT_MOUSEMOVE and self.drawing_line:
      x0, y0 = self.xy
      self.xy = (x,y)
      cv2.line(self.img, (x0, y0), (x, y), self.color[self.mode], self.thickness)  
      cv2.line(self.mask, (x0, y0), (x, y), self.key[self.mode], self.thickness)
    elif event == cv2.EVENT_LBUTTONUP and self.drawing_line:
      self.drawing_line = False
      x0, y0  = self.xy
      self.xy = ()
      cv2.line(self.img, (x0, y0), (x, y), self.color[self.mode], self.thickness)  
      cv2.line(self.mask, (x0, y0), (x, y), self.key[self.mode], self.thickness)
      print('Press \'s\' for segmentation')
    return

  def segment(self, ):
    bgdmodel = np.zeros((1,65),np.float64)
    fgdmodel = np.zeros((1,65),np.float64)
    if self.is_rect and len(self.rect) > 0:
      print(self.rect)
      cv2.grabCut(self.clone, self.mask, self.rect, bgdmodel, fgdmodel, 1, cv2.GC_INIT_WITH_RECT)
    elif not self.is_rect:
      cv2.grabCut(self.clone, self.mask, self.rect, bgdmodel, fgdmodel, 1, cv2.GC_INIT_WITH_MASK)
    return

  def full_mask(self, ):
    mask = np.where((self.mask==1) + (self.mask==3),255,0).astype('uint8')
    return cv2.resize(mask, (self.w, self.h), cv2.INTER_NEAREST)

  def prepare_callback(self, ):
    cv2.namedWindow(self.window_title, cv2.WINDOW_NORMAL)
    cv2.namedWindow('output', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(self.window_title, self.mouse_callback)
    while(1):
      cv2.imshow(self.window_title, self.img)
      k = cv2.waitKey(1)
      if k == ord('c'):# or ord('q') or k == 27:
        break
      elif k == ord('0'):
        print('mark background with left mouse button')
        self.mode = 'BGD'
      elif k == ord('1'):
        print('mark foreground with left mouse button')
        self.mode = 'FGD'
      elif k == ord('2'):
        print('mark probable background with left mouse button')
        self.mode = 'PR_BGD'
      elif k == ord('3'):
        print('mark probable foreground with left mouse button')
        self.mode = 'PR_FGD'
      elif k == ord('u'):
        self.undo()
      elif k == ord('r'):
        self.reset()
      elif k == ord('s'):
        self.segment()
      mask = np.where((self.mask==1) + (self.mask==3), 255, 0).astype('uint8')
      output = cv2.bitwise_and(self.clone, self.clone, mask=mask) 
      cv2.imshow('output', output)
    cv2.destroyAllWindows()
    return

  def get_mask(self, ):
    self.reset()
    self.prepare_callback()
    return self.full_mask()


if __name__=='__main__':
  args = get_args()
  img  = cv2.imread(args.image, cv2.IMREAD_COLOR)
  if img is None:
    print('Unable to load image \'{}\'. Quitting.'.format(args.image))
    exit()
  obj = SegmentGC(img, args.scale)
  mask = obj.get_mask()
  out  = cv2.bitwise_and(img, img, mask=mask)
  cv2.imwrite(args.output, mask)
  cv2.imwrite(args.output+'_seg.png', out)


