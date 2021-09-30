import cv2
import time
import numpy as np

from os import environ
environ['DISPLAY'] = ':0.0'

frame_width = 800
frame_height = 600

camera0_capture = cv2.VideoCapture(0, cv2.CAP_V4L2)
camera0_capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
camera0_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
camera0_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
camera0_capture.set(cv2.CAP_PROP_FPS, 30)

elapsed_time = 0
fps = 0
avg_fps_counter = 0

while True:
    # start frame and conversion
    start_time = time.time()

    # 1. Capture frame from camera
    frame_ok, image_from_camera = camera0_capture.read()
    if not frame_ok:
        continue

    image_grayscale = cv2.cvtColor(image_from_camera, cv2.COLOR_RGB2GRAY)
    # 3. Apply Gaussian Blur
    gaussian_blur_kernel = (11, 11)  # try (3,3) or (5,5) or (7,7) or (11,11)
    image_gaussian = cv2.GaussianBlur(image_grayscale, gaussian_blur_kernel, 0)

    res, image_threshold = cv2.threshold(image_gaussian, 180, 255, cv2.THRESH_BINARY)

    # 5. Erode
    erode_kernel = np.ones((5, 5), "uint8")
    image_erode = cv2.erode(image_threshold, erode_kernel, iterations=1)

    # 6. Dilate some
    dilation_kernel = np.ones((5, 5), "uint8")
    image_dilation = cv2.dilate(image_erode, dilation_kernel, iterations=1)

    stop_time = time.time()
    # stop conversion

    elapsed_time = stop_time - start_time

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image_dilation, f'FPS: {1/elapsed_time:.8f}', (0, 25), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.moveWindow("frame", 0, 0)
    cv2.imshow("frame", image_from_camera)

    key = cv2.waitKey(1)

    if key == ord('q'):
        break

cv2.destroyAllWindows()
camera0_capture.release()
