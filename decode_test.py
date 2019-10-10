# This is a preliminary decoder test. image only

import cv2
import numpy as np
import bitstring

small_res = (213, 240)
large_res = (640, 480)

side_pad = 5
ref_size = 3

data_start_point = (side_pad, side_pad + ref_size)
data_end_point = (small_res[0] - side_pad, small_res[1] - side_pad)

stop_low = np.array([0, 93, 73])
stop_high = np.array([180, 255, 151])

b_low = np.array([0, 0, 0])
b_high = np.array([1, 1, 1])

w_low = np.array([0, 0, 254])
w_high = np.array([1, 1, 255])

video = cv2.VideoCapture('data.mov')

# Main crunch
data = []
counter = 0

while True:
    ret, frame = video.read()

    x_pos = data_start_point[0] + 1
    y_pos = data_start_point[1]

    if ret:
        image = cv2.resize(frame, small_res, interpolation=cv2.INTER_NEAREST)
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        b_mask = cv2.inRange(image_hsv, b_low, b_high)
        w_mask = cv2.inRange(image_hsv, w_low, w_high)
        mask_stop = cv2.inRange(image_hsv, stop_low, stop_high)

        while True:
            if x_pos == data_end_point[0] + 1:
                x_pos = data_start_point[0] + 1
                y_pos += 1

            if mask_stop[y_pos, x_pos]:
                print(counter)
                counter += 1
                break

            if b_mask[y_pos, x_pos]:
                data.append(False)
            elif w_mask[y_pos, x_pos]:
                data.append(True)
            else:
                break

            x_pos += 1
    else:
        break

with open('DECODETEST.mp4', 'wb') as file:
    file.write(bitstring.BitArray(data).tobytes())

print(len(data))
# print(data)
print('Complete')
