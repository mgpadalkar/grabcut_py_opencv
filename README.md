# Grabcut demo with Python and OpenCV

## Usage
```bash
$ python grabcut_in_one_file.py --image images/messi5.jpg --scale 1.0 --output op_grabcut.png
```

<table border=0>
  <tr>
    <th width=25%>Input</th>
    <th width=25%>ROI selection</th>
    <th width=25%>Output mask</th>
    <th width=25%>Segmented image</th>
  </tr>
  <tr>
    <td><img src=images/input.png alt="Input"></td>
    <td><img src=images/select.png alt="ROI selection"></td>
    <td><img src=images/op_grabcut.png alt="Output mask"></td>
    <td><img src=images/op_grabcut.png_seg.png alt="Segmented image"></td>
  </tr>
</table>  

## Alternate code usage
```bash
$ python grabcut.py --image images/messi5.jpg --scale 1.0 --output op_grabcut.png # uses draw_rect.py and draw_freehand.py
```

## Code based on:
 - https://github.com/makelove/OpenCV-Python-Tutorial/blob/master/%E5%AE%98%E6%96%B9samples/grabcut.py \[grabcut_in_one_file.py\]
 - https://docs.opencv.org/3.4/d8/d83/tutorial_py_grabcut.html \[grabcut.py\]
 - https://www.geeksforgeeks.org/python-draw-rectangular-shape-and-extract-objects-using-opencv/ \[draw_rect.py\, draw_freehand.py]