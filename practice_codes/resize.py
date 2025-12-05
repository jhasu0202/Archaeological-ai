import cv2

# Load an image
img = cv2.imread(r"/home/jhasu/Pictures/Infosys Practice/computer vision/images.jpeg")   # Replace with your file path

# Check if the image loaded correctly
if img is None:
    print("Error: Could not read image.")
    exit()

# Resize image (width=300, height=300)
resized = cv2.resize(img, (300, 300))

# Show both
cv2.imshow("Original", img)
cv2.imshow("Resized", resized)

# Wait for a key press
cv2.waitKey(0)
cv2.destroyAllWindows()

# Optional: Save the resized image
cv2.imwrite("resized_output.jpg", resized)