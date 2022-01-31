# import the necessary packages
import numpy as np
import cv2
import argparse

# construct the argument parser and parse the arguments
def get_args():
  ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
  description='Demo for foreground and background selection in OpenCV.')
  ap.add_argument("-i", "--image", type=str, default='', help="Path to the input image")
  args = ap.parse_args()
  return args


class FGBG(object):
  def __init__(self, image, name='press \'r\' to reset, \'c\' to confirm \'b\' for BG, \'f\' for FG, \'u\' for undo'):
    self.image = image
    self.clone = image.copy()
    self.name = name
    self.lines = []
    self.color = {'fg': (0, 255, 0), 'bg': (0, 0, 255)}
    self.ref_points = []
    self.size = 3
    self.recording = False
    self.update_mode(is_fg=True)

  def update_mode(self, is_fg):
    self.mode = 'fg' if is_fg else 'bg'
    print('{} selected for drawing.'.format('Foreground' if is_fg else 'Background'))

  def draw_callback(self, event, x, y, flags, param):
    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being performed
    if event == cv2.EVENT_LBUTTONDOWN:
      self.last  = self.image.copy()
      self.ref_points = [(x, y)]
      self.recording = True
    # check to see if the mouse is moving and recording
    if event == cv2.EVENT_MOUSEMOVE and self.recording:
      self.ref_points.append((x, y))
      cv2.line(self.image, self.ref_points[-2], self.ref_points[-1], self.color[self.mode], self.size)
    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
      # record the ending (x, y) coordinates and indicate that
      # the cropping operation is finished
      self.ref_points.append((x, y))
      self.lines.append([self.ref_points, self.mode])
      self.recording = False
      # draw points
      # self.draw_on_image(self.image, [self.ref_points], self.color[self.mode])
      cv2.line(self.image, self.ref_points[-2], self.ref_points[-1], self.color[self.mode], self.size)
      cv2.imshow(self.name, self.image)

  # draw on image
  def draw_on_image(self, image, lines, color):
    for line in lines:
      for i in range(1, len(line)):
        cv2.line(image, line[i-1], line[i], color, self.size)
    # input image itself is updated...nothing to return

  # get mask from lines
  def line_to_mask(self, lines):
    h, w = self.image.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8) + cv2.GC_PR_BGD
    fg_lines = [l[0] for l in self.lines if l[1]=='fg']
    bg_lines = [l[0] for l in self.lines if l[1]=='bg']
    self.draw_on_image(mask, bg_lines, cv2.GC_BGD)
    self.draw_on_image(mask, fg_lines, cv2.GC_FGD)
    return mask

  def get_mask(self, ):
    cv2.namedWindow(self.name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(self.name, self.draw_callback)
    while True:
      # display the image and wait for a keypress
      cv2.imshow(self.name, self.image)
      key = cv2.waitKey(1) & 0xFF
      # set to foreground
      if key == ord('f') and self.mode == 'bg':
        self.update_mode(is_fg=True)
      # set to foreground
      if key == ord('b') and self.mode == 'fg':
        self.update_mode(is_fg=False)
      # press 'r' to reset the window
      if key == ord('r'):
        self.image = self.clone.copy()
        print('Removing all markings')
      # 'u' to undo last
      if key == ord('u'):
        if len(self.lines) > 0: self.lines.pop()
        self.image = self.last.copy()
        print('Removed last marking')
      # press 'c' to break from the loop
      elif key == ord('c'):
        break
    cv2.destroyAllWindows()
    return self.line_to_mask(self.lines)


if __name__ == '__main__':
  args = get_args()
  image = cv2.imread(args.image)
  obj   = FGBG(image)
  mask  = obj.get_mask()
  cv2.imwrite('mask.png', mask*127)