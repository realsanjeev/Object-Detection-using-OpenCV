import cv2
import numpy as np

image = cv2.imread("menu.png")
print(f"[INFO] Shape of menu image: {image.shape}")

blank = np.zeros((100, 999, 3), dtype="uint8")
blank[:90,:634] = image

cv2.imshow("instruction", blank)
cv2.imshow("menu", image)

cv2.waitKey(0)
cv2.destroyAllWindows()
