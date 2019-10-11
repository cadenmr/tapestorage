# This is a class make_video.py and decode_video.py will use
# Currently using 200 symbols per field

import cv2
import bitstring
import numpy as np
import glob
import os


class Video:
    # Take in a list of files if encoding
    def __init__(self, type_format, files=None, file_out_name=None):
        self.files = files
        self.__format = type_format
        self.file_out = file_out_name

        # Set the frame resolution depending on format
        if self.__format == 'vhs':
            self.__initial_resolution = (213, 240)
        elif self.__format == 's-vhs':
            self.__initial_resolution = (320, 480)
        else:
            raise ValueError('Format provided was not vhs or s-vhs')

        # Set up variables

        # Framing
        self.__final_resolution = (640, 480)  # x, y
        self.__side_pad = 5
        self.__ref_size = 3

        # Colors
        self.__background_color = np.array([39.6, 89.8, 96.7])
        self.__on_color = np.array([0, 0, 100])
        self.__off_color = np.array([0, 0, 0])

        # Define size bounds
        self.__ref_line_start = (self.__side_pad, self.__side_pad)
        self.__ref_line_end = (self.__initial_resolution[0] - self.__side_pad, self.__side_pad)
        self.__data_start_px = (self.__side_pad, self.__side_pad + self.__ref_size)
        self.__data_end_px = (self.__initial_resolution[0] - self.__side_pad,
                              self.__initial_resolution[1] - self.__side_pad)

        # Speed
        self._framerate = 29.97

        # Statistics
        self.__symbol_count = self.__data_end_px[0] * self.__data_end_px[1]
        self.__transfer_speed = (self.__symbol_count * self._framerate) / 1e+6

        # Initialize position counters
        self._x_pos = self.__data_start_px[0]
        self._y_pos = self.__data_start_px[1]

        # Create the frame pointer but don't assign anything to save memory
        self._frame = None

        # Initial reference bar state
        self._bar_state = False

    # This function resets the frame variables
    # Intended to be run each new frame to create a blank slate
    def _reset_framevars(self):
        # Set cursor
        self._x_pos = self.__data_start_px[0]
        self._y_pos = self.__data_start_px[1]
        # Make an empty image
        self._frame = np.zeros((self.__initial_resolution[1], self.__initial_resolution[0], 3))

        # Set the background color
        for i in range(self.__initial_resolution[1]):
            for b in range(self.__initial_resolution[0]):
                self._frame[i, b] = self.__background_color

        # Create stripe
        for i in range(self.__ref_line_start[0], self.__ref_line_end[0]):
            if self._bar_state:
                if i % 2 == 0:
                    self._frame[self.__ref_line_start[1], i] = np.array((0, 0, 0))
                else:
                    self._frame[self.__ref_line_start[1], i] = np.array((255, 255, 255))
            else:
                if i % 2 == 0:
                    self._frame[self.__ref_line_start[1], i] = np.array((255, 255, 255))
                else:
                    self._frame[self.__ref_line_start[1], i] = np.array((0, 0, 0))

        # Flip the state bit
        self._bar_state = not self._bar_state

    # Automate the encode process
    def encode(self):
        # Show some data
        print(f'Format: {self.__format}')
        print(f'Framerate: {self._framerate}')
        print(f'Bits per frame: {self.__symbol_count}')
        print(f'Transfer Speed (mbps): {self.__transfer_speed}')
        print('--------------------------------------')

        print('loading file...')
        with open(self.files) as file:
            bs = bitstring.BitArray(file)
        print('done')

        # Begin data encoding
        # Set initial values for the x and y position of the pixel, and initial value for the file name
        filename = 0

        print('making frames (v2)...')
        # Start by resetting the framing variables and generating a new frame
        self._reset_framevars()

        # For every item (True/False) in the bitstring object
        for b in bs:
            # Line length limit
            if self._x_pos >= self.__data_end_px[0]:
                self._x_pos = self.__data_start_px[0]
                self._y_pos += 1

            # End of frame limit
            if self._y_pos > self.__data_end_px[1]:
                # Resize the frame
                self._frame = cv2.resize(self._frame, self.__final_resolution, interpolation=cv2.INTER_NEAREST)
                # Save it
                cv2.imwrite(f'outputfiles/output{filename}.png', self._frame)
                # Increment the file name
                filename += 1
                # Reset everything and generate a new frame
                self._reset_framevars()

            # Set bit
            if b:
                self._frame[self._y_pos, self._x_pos] = np.array((255, 255, 255))
            elif not b:
                self._frame[self._y_pos, self._x_pos] = np.array((0, 0, 0))

            self._x_pos += 1

        print('done')

        # Create a video
        print('converting frames to video...')
        # LOSSLESS: hfyu
        out = cv2.VideoWriter('data.avi', cv2.VideoWriter_fourcc(*'HFYU'), self._framerate, self.__final_resolution)
        image_path_list = []
        for name in sorted(glob.glob('outputfiles/output*.png'), key=os.path.getctime):
            img = cv2.imread(name)
            out.write(img)
            image_path_list.append(name)

        for i in image_path_list:
            os.remove(i)

        out.release()
        print('done')
        print('Finished')

    # Image decoder function
    def decode(self):
        # Set the correct pixel offset based on format
        if self.__format == 'vhs':
            offset = 1
        elif self.__format == 's-vhs':
            offset = 0
        else:
            offset = 1

        stop_low = np.array([0, 93, 73])
        stop_high = np.array([180, 255, 151])
        
        video = cv2.VideoCapture(self.files)
        frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)

        # Main crunch
        data = bitstring.BitArray()
        counter = 0

        while True:
            ret, frame = video.read()

            x_pos = self.__data_start_px[0] + offset
            y_pos = self.__data_start_px[1]

            if ret:
                image = cv2.resize(frame, self.__initial_resolution, interpolation=cv2.INTER_NEAREST)
                image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

                mask_stop = cv2.inRange(image_hsv, stop_low, stop_high)

                while True:
                    if x_pos >= self.__data_end_px[0] + offset:
                        x_pos = self.__data_start_px[0] + offset
                        y_pos += 1

                    if mask_stop[y_pos, x_pos]:
                        counter += 1
                        break

                    if image[y_pos, x_pos, 0] >= 255 / 2:
                        data.append(bin(True))
                    elif image[y_pos, x_pos, 0] < 255 / 2:
                        data.append(bin(False))
                    else:
                        break

                    x_pos += 1
            else:
                break

        with open(self.file_out, 'wb') as file:
            file.write(data.tobytes())

        print('Complete')
