import cv2

# Load an image
img = cv2.imread(r"/home/jhasu/Pictures/Infosys Practice/computer vision/images.jpeg")   # Replace with your file path

# Check if image loaded correctly
if img is None:
    print("Error: Could not read image.")
    exit()

# Apply Gaussian Blur (15x15 kernel) mostly prefer odd number 
#as kernel size. More the size of kernel more stronger blur
#less the no of size less stronger the kernel
blur = cv2.GaussianBlur(img, (15, 15), 0)

# Show both
cv2.imshow("Original", img)
cv2.imshow("Blurred", blur)

# Wait for key press
cv2.waitKey(0)
cv2.destroyAllWindows()

# Optional: Save the blurred image
cv2.imwrite("blurred_output.jpg", blur)