#CODE 4

import cv2

# Read image
img = cv2.imread(r"/home/jhasu/Pictures/Infosys Practice/computer vision/images.jpeg")

if img is None:
    print("Error: Could not read image.")
else:
    # Flip vertically (0), horizontally (1), or both (-1)
    flip_vertical = cv2.flip(img, 0) #0 is for vertical flip
    flip_horizontal = cv2.flip(img, 1) #1 for horizontal flip
    flip_both = cv2.flip(img, -1) #-1 for both

    # Show results
    cv2.imshow("Original", img)
    cv2.imshow("Flipped Vertically", flip_vertical)
    cv2.imshow("Flipped Horizontally", flip_horizontal)
    cv2.imshow("Flipped Both", flip_both)

    cv2.waitKey(0)
    cv2.destroyAllWindows()