#CODE 8

import cv2
import numpy as np

img = np.zeros((500, 500, 3), dtype="uint8")

# Draw shapes
cv2.line(img, (0, 0), (500, 500), (255, 0, 0), 5)
cv2.rectangle(img, (50, 50), (200, 200), (0, 255, 0), 3)
cv2.circle(img, (300, 300), 80, (0, 0, 255), -1)

# Add text
cv2.putText(img, "OpenCV Demo", (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

cv2.imshow("Shapes and Text", img)
cv2.waitKey(0)
cv2.destroyAllWindows()