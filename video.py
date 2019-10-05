# This is a class make_video.py and decode_video.py will use
# Currently using 200 symbols per field

import cv2
import bitstring
import numpy as np
import glob
import os
# import multiprocessing


class Video:
    # Take in a list of files if encoding
    def __init__(self, files=None):
        self.files = files

        # Set up variables
        # Framing
        self.__initial_resolution = (320, 240)  # x, y
        self.__final_resolution = (640, 480)  # x, y
        self.__side_pad = 5
        self.__ref_size = 3
        self.__symbol_count = (self.__initial_resolution[0] - self.__ref_size - (self.__side_pad * 2)) * \
                              (self.__initial_resolution[1] - (self.__side_pad * 2))

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

    # Automate the encode process
    def encode(self):
        # Create an empty list for colors
        color_array = []

        # Iterate through the file path list
        for i in self.files:
            # Iterate through all files
            print('creating bit list...')

            with open(i) as file:
                bs = bitstring.BitArray(file)
                for d in range(len(bs)):
                    color_array.append(bs[d])

            print('done')

        # Chop raw bits into frames
        print('chopping bit list into frames...')
        parsed_array = [color_array[i:i+self.__symbol_count] for i in range(0, len(color_array), self.__symbol_count)]
        print('done')

        # Clean up, save memory
        del color_array

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
        image_list = []
        image_path_list = []
        for name in sorted(glob.glob('outputfiles/output*.png'), key=os.path.getctime):
            img = cv2.imread(name)
            image_list.append(img)
            image_path_list.append(name)

        out = cv2.VideoWriter('data.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 29.97, self.__final_resolution)

        for i in range(len(image_list)):
            out.write(image_list[i])

        for i in image_path_list:
            os.remove(i)

        out.release()
        print('done')

        print('Finished')

    # def decode(self):
    #     bits = []
    #
    #     if len(self.files) > 1:
    #         raise IndexError('Can only input one file')
    #
    #     with open(self.files[0]) as data_file:
