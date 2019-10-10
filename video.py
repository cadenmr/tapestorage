# This is a class make_video.py and decode_video.py will use
# Currently using 200 symbols per field

import cv2
import bitstring
import numpy as np
import glob
import os
import time


class Video:
    # Take in a list of files if encoding
    def __init__(self, format, files=None, file_out_name=None):
        self.files = files
        self.__format = format
        self.file_out = file_out_name

        if format == 'vhs':
            self.__initial_resolution = (213, 240)
        elif format == 's-vhs':
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
        self.__framerate = 29.97

        # Statistics
        self.__symbol_count = self.__data_end_px[0] * self.__data_end_px[1]

        self.__transfer_speed = (self.__symbol_count * self.__framerate) / 1e+6

    # Automate the encode process
    def encode(self):
        # Show some data
        print(f'Format: {self.__format}')
        print(f'Framerate: {self.__framerate}')
        print(f'Bits per frame: {self.__symbol_count}')
        print(f'Transfer Speed (mbps): {self.__transfer_speed}')
        print('-------------------------------------- ')

        # Iterate through the file path list
        for i in self.files:
            # Iterate through all files

            print('loading file...')
            with open(i) as file:
                bs = bitstring.BitArray(file)
            print('done')

        # Chop raw bits into frames
        print('chopping bits into frames...')
        parsed_array = [bs[i:i+self.__symbol_count] for i in range(0, len(bs), self.__symbol_count)]
        bslen = len(bs)
        del bs

        time = round((len(parsed_array) / self.__framerate) / 60, ndigits=1)

        print('done')
        print('-----------------------------')
        print(f'{bslen} bits')
        print(f'need to make {len(parsed_array)} frames')
        print(f'video will be {time} mins')
        print('-----------------------------')

        # Begin data encoding
        # Set initial values for the x and y position of the pixel, and initial value for the file name
        filename = 0
        state = False

        # Run though all the frame data
        print('making frames...')
        for d in parsed_array:
            # Start of frame
            # Set starter values
            x_pos = self.__data_start_px[0]
            y_pos = self.__data_start_px[1]

            # Create blank image
            frame = np.zeros((self.__initial_resolution[1], self.__initial_resolution[0], 3))

            # Run through pixels and set background color for each
            for i in range(self.__initial_resolution[1]):
                for b in range(self.__initial_resolution[0]):
                    frame[i, b] = self.__background_color

            # Create the stripes for synchro
            for i in range(self.__ref_line_start[0], self.__ref_line_end[0]):

                if state:
                    if i % 2 == 0:
                        frame[self.__ref_line_start[1], i] = np.array((0, 0, 0))
                    else:
                        frame[self.__ref_line_start[1], i] = np.array((255, 255, 255))
                else:
                    if i % 2 == 0:
                        frame[self.__ref_line_start[1], i] = np.array((255, 255, 255))
                    else:
                        frame[self.__ref_line_start[1], i] = np.array((0, 0, 0))

            # Flip the state for the synchro bar
            state = not state

            # Check each bit in the frame and set the pixel accordingly
            for i in d:
                # Position limit checks
                # Column limiter
                if x_pos >= self.__data_end_px[0]:
                    x_pos = self.__data_start_px[0]
                    y_pos += 1

                # Line limiter
                if y_pos >= self.__data_end_px[1]:
                    y_pos = self.__data_start_px[1]


                # 1 bit
                if i:
                    frame[y_pos, x_pos] = np.array((255, 255,  255))
                # 0 bit
                else:
                    frame[y_pos, x_pos] = np.array((0, 0, 0))

                # Update the x position every bit
                x_pos += 1

            # Resize the frame to final resolution
            frame = cv2.resize(frame, self.__final_resolution, interpolation=cv2.INTER_NEAREST)
            # Save it & get rid of it
            cv2.imwrite(f'outputfiles/output{filename}.png', frame)
            del frame
            # Increment the file name
            filename += 1

        print('done')

        # Get rid of the bit lists to save memory
        del parsed_array

        # Create a video
        print('converting frames to video')
        # LOSSLESS: hfyu ,
        out = cv2.VideoWriter('data.mp4', cv2.VideoWriter_fourcc(*'mp4v'), self.__framerate, self.__final_resolution)
        image_list = []
        image_path_list = []
        for name in sorted(glob.glob('outputfiles/output*.png'), key=os.path.getctime):
            img = cv2.imread(name)
            out.write(img)
            # image_list.append(img)
            image_path_list.append(name)

        for i in image_path_list:
            os.remove(i)

        out.release()
        print('done')

        print('Finished')

    # Image decoder function
    def decode(self):
        # Low and high color break bounds
        stop_low = np.array([0, 93, 73])
        stop_high = np.array([180, 255, 151])

        # Open the video source
        video = cv2.VideoCapture(self.files)
        # Grab the frame count of video source
        frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
        data = []

        for fr in range(int(frame_count)):
            x_pos = self.__data_start_px[0]
            y_pos = self.__data_start_px[1]

            ret, frame = video.read()
            # frame = cv2.resize(frame, self.__initial_resolution, interpolation=cv2.INTER_NEAREST)
            frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            mask = cv2.inRange(frame_hsv, stop_low, stop_high)

            # cv2.imshow('Video', frame)
            # cv2.imshow('Mask', mask)

            if ret:
                while True:
                    if x_pos >= self.__data_end_px[0]:
                        x_pos = self.__data_start_px[0]
                        y_pos += 1

                    if mask[y_pos, x_pos] == 255:
                        print('BREAK')
                        print(x_pos, y_pos)
                        break

                    symbol = frame[y_pos, x_pos, 0]
                    # print(symbol)

                    if int(symbol) < (255/2):
                        data.append(False)
                        # print(False)
                    elif (255 / 2) < int(symbol) <= 255:
                        data.append(True)
                        # print(True)
                    else:
                        raise ValueError('Range not within 255')

                    x_pos += 1

        print(len(data))


        with open(self.file_out, 'wb') as f:
            f.write(bitstring.BitArray(data).tobytes())