#CODE 14

import cv2
import numpy as np

img = cv2.imread("person.jpg")
mask = np.zeros(img.shape[:2], np.uint8)

bgdModel = np.zeros((1, 65), np.float64)
fgdModel = np.zeros((1, 65), np.float64)

rect = (50, 50, 400, 500)  # ROI

cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
result = img * mask2[:, :, np.newaxis]

cv2.imshow("Original", img)
cv2.imshow("Foreground Extracted", result)
cv2.waitKey(0)
cv2.destroyAllWindows()