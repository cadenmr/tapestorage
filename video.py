# This is a class make_video.py and decode_video.py will use
# Currently using 200 symbols per field

import cv2
import bitstring
import numpy as np
import glob
import os


class Video:
    # Take in a list of files if encoding
    def __init__(self, files=None):
        self.files = files

        # Set up variables
        # Framing
        self.__initial_resolution = (167, 240)  # x, y
        self.__final_resolution = (640, 480)  # x, y
        self.__symbol_count = 35639
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

    # Get the bit string representation of a file
    def _get_bitstring(self, file):
        with open(file) as file:
            b = bitstring.BitArray(file)
            return b.bin

    # Automate the encode process
    def encode(self):
        # Create an empty list for colors
        color_array = []

        # Iterate through the file path list
        for i in self.files:
            print(f'loading file "{i}"...')
            # Get the raw bit data of the current file and save the original just-in-case
            bit_repr = self._get_bitstring(i)
            # Chop into 3-bit or less segments and save separately
            bit_repr_chopped = [bit_repr[i:i+1] for i in range(0, len(bit_repr), 1)]
            print('done')

            # Iterate through all 3 or less bit segments
            print('creating video...')
            print('assigning value to bits...')
            for d in bit_repr_chopped:
                # Assign color to segment
                if len(d) == 1:
                    if d == '0':
                        color = False
                    elif d == '1':
                        color = True
                    else:
                        print('ERROR', d)
                        raise IOError('Not a 0 or 1')
                else:
                    print('ERROR', d)
                    raise IOError('Not a 0 or 1')

                # Append the color to the list of all colors
                color_array.append(color)
            print('done')

        # Chop raw bits into frames
        print('chopping bit list into frames...')
        parsed_array = [color_array[i:i+self.__symbol_count] for i in range(0, len(color_array), self.__symbol_count)]
        print('done')

        # Clean up, save memory
        del color_array

        # Begin data encoding
        # Set initial values for the x and y position of the pixel, and initial value for the file name
        x_pos = self.__data_start_px[0]
        y_pos = self.__data_start_px[1]
        filename = 0
        state = False

        # Run though all the frame data
        print('making frames...')
        for d in parsed_array:
            # Create a new frame
            frame = np.zeros((self.__initial_resolution[1], self.__initial_resolution[0], 3))

            # Set the background color
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

            # Resize the frame to 640x480
            frame = cv2.resize(frame, self.__final_resolution, interpolation=cv2.INTER_NEAREST)
            # Save it
            cv2.imwrite(f'outputfiles/output{filename}.png', frame)
            # Update the file name
            filename += 1

        print('done')

        # Create a video
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

        print('Finished')

    # def decode(self):
    #     bits = []
    #
    #     if len(self.files) > 1:
    #         raise IndexError('Can only input one file')
    #
    #     with open(self.files[0]) as data_file:
