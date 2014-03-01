from cv2 import *
vc = VideoCapture(0)

while waitKey(30) < 1:
    rv, frame = vc.read()
    imshow('preview', frame)
