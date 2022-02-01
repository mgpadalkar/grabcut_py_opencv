# import the necessary packages
import cv2
import argparse

# construct the argument parser and parse the arguments
def get_args():
  ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
  description='Demo for rectangle selection in OpenCV.')
  ap.add_argument("-i", "--image", type=str, default='', help="Path to the input image")
  args = ap.parse_args()
  return args


class ROI(object):
  def __init__(self, image, name='press \'r\' to reset, \'c\' to confirm'):
    self.image = image
    self.clone = image.copy()
    self.name  = name
    self.ref_point = []
    self.recording = False

  def draw_rect(self, event, x, y, flags, param):
    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being performed
    if event == cv2.EVENT_LBUTTONDOWN:
      self.recording = True
      self.ref_point = [(x, y)]
      self.image = self.clone.copy()
    # for mouse movement
    elif event == cv2.EVENT_MOUSEMOVE and self.recording:
      self.image = self.clone.copy()
      cv2.rectangle(self.image, self.ref_point[0], (x, y), (0, 255, 0), 2)
      
    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP and self.recording:
      self.recording = False
      # record the ending (x, y) coordinates and indicate that
      # the cropping operation is finished
      self.ref_point.append((x, y))
      # draw a rectangle around the region of interest
      cv2.rectangle(self.image, self.ref_point[0], self.ref_point[1], (0, 255, 0), 2)
      # cv2.imshow(self.name, self.image)

  def points_to_rect(self, pt):
    if len(pt) > 1:
      x1 = pt[0][0]; x2 = pt[-1][0]
      y1 = pt[0][1]; y2 = pt[-1][1]
      rect = (min(x1, x2), min(y1, y2), abs(x2-x1), abs(y2-y1))
      success = True
    else:
      rect = (0, 0, self.image.shape[:-1], self.image.shape[-2])
      success = False
    return (rect, success)


  def get_mask(self, ):
    cv2.namedWindow(self.name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(self.name, self.draw_rect)
    while True:
      # display the image and wait for a keypress
      cv2.imshow(self.name, self.image)
      key = cv2.waitKey(1) & 0xFF
      # press 'r' to reset the window
      if key == ord('r'):
        self.image = self.clone.copy()
      # press 'c' to break from the loop
      elif key == ord('c'):
        break
    cv2.destroyAllWindows()
    return self.points_to_rect(self.ref_point)


if __name__ == '__main__':
  args = get_args()
  image = cv2.imread(args.image)
  roi = ROI(image)
  rect, success = roi.get_mask()
  if success:
    print('selected rect: ')
    print(rect)


