# -*- coding: utf-8 -*-
"""
    Fire detector for CanSAT drone vision subsystem.

    References:
        Fullscreen snipplet
        https://gist.github.com/ronekko/dc3747211543165108b11073f929b85e
"""

import numpy as np
import cv2
import screeninfo
import time

# Projector constants
SCREEN_ID = 0
projector_window_name = 'projector'
picture_in_picture = False

test_image_square_size = 100

# Frame
frame_width = 640
frame_height = 480


# def get_multiview_composition(images, screen_height, screen_width):
#     color_images = []
#     for image in images:
#         if len(image.shape) != 3:
#             color_images.append(cv2.cvtColor(image, cv2.COLOR_GRAY2RGB))
#         else:
#             color_images.append(image)
#
#     fill_color = (35, 35, 35)  # dark gray
#     result = np.full((screen_height, screen_width, 3), fill_color, dtype=np.uint8)
#
#     resized_image_height = screen_height // 2
#
#     r = resized_image_height / image.shape[1]
#     dim = (resized_image_height, int(image.shape[0] * r))
#
#     resized_images = []
#     for image in color_images:
#         resized_images.append(cv2.resize(image, dim, interpolation=cv2.INTER_LANCZOS4))
#
#     padding = 50
#
#     result[padding:int(image.shape[0] * r)+padding, padding:resized_image_height+padding] = resized_images[0]
#     result[padding:int(image.shape[0] * r)+padding, 2*padding+resized_image_height:2*resized_image_height+2*padding] = resized_images[1]
#     result[padding:int(image.shape[0] * r)+padding, 3*padding+2*resized_image_height:3*resized_image_height+3*padding] = resized_images[2]
#
#     result[2*padding+int(image.shape[0] * r):2*int(image.shape[0] * r)+2*padding, padding:resized_image_height+padding] = resized_images[3]
#     result[2*padding+int(image.shape[0] * r):2*int(image.shape[0] * r)+2*padding, 2*padding+resized_image_height:2*resized_image_height+2*padding] = resized_images[4]
#     result[2*padding+int(image.shape[0] * r):2*int(image.shape[0] * r)+2*padding, 3*padding+2*resized_image_height:3*resized_image_height+3*padding] = resized_images[5]
#
#     return result


# def create_test_image(screen_height, screen_width, square_size):
#     test_squares_image = np.ones((screen_height, screen_width, 3), dtype=np.float32)
#     test_squares_image[:square_size, :square_size] = 0  # black at top-left corner
#     test_squares_image[screen_height - square_size:, :square_size] = [1, 0,
#                                                                       0]  # blue at bottom-left
#     test_squares_image[:square_size, screen_width - square_size:] = [0, 1,
#                                                                      0]  # green at top-right
#     test_squares_image[screen_height - square_size:, screen_width - square_size:] = [0, 0,
#                                                                                      1]  # red at bottom-right
#     return test_squares_image


def main():
    print(f'OpenCV version: {cv2.__version__}')

    # get the size of the screen
    screen = screeninfo.get_monitors()[SCREEN_ID]
    print(f'Screen information: {screen}')

    screen_width, screen_height = screen.width, screen.height

    # test_squares_image = create_test_image(screen_height, screen_width, test_image_square_size)
    # test_squares_image_2 = create_test_image(screen_height, screen_width, test_image_square_size * 2)

    projected_image_selector = {"scene": "image_from_camera"}
    bypass_gaussian = False

    show_hud = True

    shift_x = (screen_width - frame_width) // 2
    shift_y = (screen_height - frame_height) // 2

    # Camera capture, uses /dev/video0 device
    camera0_capture = cv2.VideoCapture(0, cv2.CAP_V4L2)
    camera0_capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    camera0_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    camera0_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    camera0_capture.set(cv2.CAP_PROP_FPS, 30)

    avg_fps_counter = 0
    elapsed_time = 0
    fps = 0
    while True:
        start_time = time.time()

        fill_color = (35, 35, 35) # dark gray
        projected_image = np.full((screen_height, screen_width, 3), fill_color, dtype=np.uint8)

        # 1. Capture frame from camera
        frame_ok, image_from_camera = camera0_capture.read()
        if not frame_ok:
            continue

        # 2. Convert to grayscale
        image_grayscale = cv2.cvtColor(image_from_camera, cv2.COLOR_RGB2GRAY)

        # 3. Apply Gaussian Blur
        gaussian_blur_kernel = (11, 11)  # try (3,3) or (5,5) or (7,7) or (11,11)
        image_gaussian = cv2.GaussianBlur(image_grayscale, gaussian_blur_kernel, 0)

        # 4. Apply thresholding
        # 4.1 Bypass gaussian stage to show the difference
        if bypass_gaussian:
            res, image_threshold = cv2.threshold(image_grayscale, 180, 255, cv2.THRESH_BINARY)
        else:
            res, image_threshold = cv2.threshold(image_gaussian, 180, 255, cv2.THRESH_BINARY)

        # 5. Erode
        erode_kernel = np.ones((5, 5), "uint8")
        image_erode = cv2.erode(image_threshold, erode_kernel, iterations=1)

        # 6. Dilate some
        dilation_kernel = np.ones((5, 5), "uint8")
        image_dilation = cv2.dilate(image_erode, dilation_kernel, iterations=1)

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
        else:
            rect = []
            box = []

        end_time = time.time()
        elapsed_time += (end_time - start_time)

        # Choose what to project
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('g'):
            bypass_gaussian = True
        elif key == ord('h'):
            bypass_gaussian = False
        elif key == ord('a'):
            show_hud = True
        elif key == ord('s'):
            show_hud = False
        elif key == ord('1'):
            projected_image_selector["scene"] = "image_from_camera"
        elif key == ord('2'):
            projected_image_selector["scene"] = "image_grayscale"
        elif key == ord('3'):
            projected_image_selector["scene"] = "image_gaussian"
        elif key == ord('4'):
            projected_image_selector["scene"] = "image_threshold"
        elif key == ord('5'):
            projected_image_selector["scene"] = "image_erode"
        elif key == ord('6'):
            projected_image_selector["scene"] = "image_dilation"
        elif key == ord('8'):
            projected_image_selector["scene"] = "test_squares_image"
        elif key == ord('9'):
            projected_image_selector["scene"] = "test_squares_image_2"
        elif key == ord('0'):
            projected_image_selector["scene"] = "multiview"

        # Set image to be projected
        if projected_image_selector["scene"] == "image_from_camera":
            projected_image[shift_y:frame_height + shift_y, shift_x:frame_width + shift_x] = image_from_camera
        elif projected_image_selector["scene"] == "image_grayscale":
            projected_image[shift_y:frame_height + shift_y, shift_x:frame_width + shift_x] = cv2.cvtColor(image_grayscale, cv2.COLOR_GRAY2RGB)
        elif projected_image_selector["scene"] == "image_gaussian":
            projected_image[shift_y:frame_height + shift_y, shift_x:frame_width + shift_x] = cv2.cvtColor(image_gaussian, cv2.COLOR_GRAY2RGB)
        elif projected_image_selector["scene"] == "image_threshold":
            projected_image[shift_y:frame_height + shift_y, shift_x:frame_width + shift_x] = cv2.cvtColor(image_threshold, cv2.COLOR_GRAY2RGB)
        elif projected_image_selector["scene"] == "image_erode":
            projected_image[shift_y:frame_height + shift_y, shift_x:frame_width + shift_x] = cv2.cvtColor(image_erode, cv2.COLOR_GRAY2RGB)
        elif projected_image_selector["scene"] == "image_dilation":
            projected_image[shift_y:frame_height + shift_y, shift_x:frame_width + shift_x] = cv2.cvtColor(image_dilation, cv2.COLOR_GRAY2RGB)
        # elif projected_image_selector["scene"] == "multiview":
        #     images = [image_from_camera, image_grayscale, image_gaussian, image_threshold, image_erode, image_dilation]
        #     projected_image = get_multiview_composition(images, screen_height, screen_width)
        # elif projected_image_selector["scene"] == "test_squares_image":
        #     projected_image = test_squares_image
        # elif projected_image_selector["scene"] == "test_squares_image_2":
        #     projected_image = test_squares_image_2

        if avg_fps_counter == 5:
            fps = 5 / elapsed_time
            elapsed_time = 0
            avg_fps_counter = 0
        else:
            avg_fps_counter += 1

        if show_hud and projected_image_selector["scene"] != "multiview":
            # Output FPS counter
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(projected_image, f'FPS: {fps:.3f}', (0, 25), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

            if box != []:
                # Draw box
                box[:, 0] += shift_x
                box[:, 1] += shift_y

                cv2.drawContours(projected_image, [box], 0, (0, 0, 255), 2)

                # Draw center dot
                rect = ((rect[0][0] + shift_x, rect[0][1] + shift_y), (rect[1][0] + shift_x, rect[1][1] + shift_y), rect[2])

                cv2.circle(projected_image, (int(rect[0][0]), int(rect[0][1])), 10, (0, 0, 255), -1)

                # Draw crisshair lines
                cv2.line(projected_image, (int(rect[0][0]), int(rect[0][1])), (int(rect[0][0]), screen_height), (0, 0, 255), 2)
                cv2.line(projected_image, (int(rect[0][0]), int(rect[0][1])), (int(rect[0][0]), 0), (0, 0, 255), 2)
                cv2.line(projected_image, (int(rect[0][0]), int(rect[0][1])), (screen_width, int(rect[0][1])), (0, 0, 255), 2)
                cv2.line(projected_image, (int(rect[0][0]), int(rect[0][1])), (0, int(rect[0][1])), (0, 0, 255), 2)

                # Show center
                cv2.putText(projected_image, f'x={int(rect[0][0])} y={int(rect[0][1])}', (250, 25), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Now project image to the screen
        cv2.namedWindow(projector_window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.moveWindow(projector_window_name, screen.x - 1, screen.y - 1)
        cv2.setWindowProperty(projector_window_name, cv2.WND_PROP_FULLSCREEN,
                              cv2.WINDOW_FULLSCREEN)
        cv2.imshow(projector_window_name, projected_image)

    cv2.destroyAllWindows()
    camera0_capture.release()

    print('Have a nice day! :)')


if __name__ == '__main__':
    main()
