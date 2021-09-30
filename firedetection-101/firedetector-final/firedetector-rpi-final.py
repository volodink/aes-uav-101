import picamera
from picamera.array import PiRGBArray
import time
import cv2
import numpy as np

from os import environ
environ['DISPLAY'] = ':0.0'

frame_resolution = (640, 480)


camera = picamera.PiCamera()
camera.resolution = frame_resolution
camera.framerate = 32
# camera.color_effects = (128,128)
rawCapture = PiRGBArray(camera, size=frame_resolution)

time.sleep(0.5)

stream = camera.capture_continuous(rawCapture,
			format="bgr", use_video_port=True)

elapsed_time = 0.1
fps = 1
number_of_averages = 0

font = cv2.FONT_HERSHEY_SIMPLEX

selected_image = 1

for f in stream:
	# start frame and conversion
	start_time = time.time()

	image_from_camera = f.array

	image_grayscale = cv2.cvtColor(image_from_camera, cv2.COLOR_RGB2GRAY)

	gaussian_blur_kernel = (5, 5)  # try (3,3) or (5,5) or (7,7) or (11,11)
	image_gaussian = cv2.GaussianBlur(image_grayscale, gaussian_blur_kernel, 0)

	res, image_threshold = cv2.threshold(image_gaussian, 180, 255, cv2.THRESH_BINARY)

	# 5. Erode
	erode_kernel = np.ones((5, 5), "uint8")
	image_erode = cv2.erode(image_threshold, erode_kernel, iterations=1)

	# 6. Dilate some
	dilation_kernel = np.ones((5, 5), "uint8")
	image_dilation = cv2.dilate(image_erode, dilation_kernel, iterations=1)

	key = cv2.waitKey(1)
	if key == ord('q'):
		break
	elif key == ord('1'):
		selected_image = 1
	elif key == ord('2'):
		selected_image = 2
	elif key == ord('3'):
		selected_image = 3

	if selected_image == 1:
		projected_image = image_from_camera
	elif selected_image == 2:
		projected_image = cv2.cvtColor(image_gaussian, cv2.COLOR_GRAY2RGB)
	elif selected_image == 3:
		projected_image = cv2.cvtColor(image_threshold, cv2.COLOR_GRAY2RGB)

	# 7. Find contours
	contours, hierarchy = cv2.findContours(image_dilation, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

	# 8. Find largest contour
	largest_contour = None
	max_area = 0
	for idx, contour in enumerate(contours):
		area = cv2.contourArea(contour)
		if area > max_area:
			max_area = area
			largest_contour = contour

	if largest_contour is not None:
		rect = cv2.minAreaRect(largest_contour)
		box = np.int0(cv2.boxPoints(rect))

		cv2.drawContours(projected_image, [box], 0, (0, 0, 255), 2)

		cv2.circle(projected_image, (int(rect[0][0]), int(rect[0][1])), 10, (0, 0, 255), -1)

		# Draw crisshair lines
		cv2.line(projected_image, (int(rect[0][0]), int(rect[0][1])), (int(rect[0][0]), frame_resolution[1]), (0, 0, 255), 2)
		cv2.line(projected_image, (int(rect[0][0]), int(rect[0][1])), (int(rect[0][0]), 0), (0, 0, 255), 2)
		cv2.line(projected_image, (int(rect[0][0]), int(rect[0][1])), (frame_resolution[0], int(rect[0][1])), (0, 0, 255), 2)
		cv2.line(projected_image, (int(rect[0][0]), int(rect[0][1])), (0, int(rect[0][1])), (0, 0, 255), 2)

		# Show center
		cv2.putText(projected_image, f'x={int(rect[0][0])} y={int(rect[0][1])}', (250, 25), font, 1, (255, 255, 255), 2,
					cv2.LINE_AA)

	cv2.putText(projected_image, f'FPS: {fps:.2f}', (0, 25), font, 1, (255, 255, 255), 2, cv2.LINE_AA)


	stop_time = time.time()
	# stop conversion

	if number_of_averages == 10:
		number_of_averages = 0
		elapsed_time /= 10
		fps = 1 / elapsed_time
	else:
		elapsed_time += stop_time - start_time
		number_of_averages += 1

	cv2.moveWindow("frame", 0, 0)
	cv2.imshow("frame", projected_image)

	rawCapture.truncate(0)


stream.close()
rawCapture.close()
camera.close()
