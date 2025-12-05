#CODE 9

import cv2

img = cv2.imread(r"/home/jhasu/Pictures/Infosys Practice/computer vision/images.jpeg", 0)  # Load in grayscale

_, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

cv2.imshow("Original", img)
cv2.imshow("Thresholded", thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()
