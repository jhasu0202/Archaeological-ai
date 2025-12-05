#CODE 13

import cv2

img = cv2.imread("ball.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Define blue color range
lower_blue = (100, 150, 0)
upper_blue = (140, 255, 255)

mask = cv2.inRange(hsv, lower_blue, upper_blue)
result = cv2.bitwise_and(img, img, mask=mask)

cv2.imshow("Original", img)
cv2.imshow("Mask", mask)
cv2.imshow("Filtered", result)
cv2.waitKey(0)
cv2.destroyAllWindows()