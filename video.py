# This is a class make_video.py and decode_video.py will use
# Currently using 200 symbols per field

import cv2
import bitstring


class Video:
    # Take in a list of files if encoding
    def __init__(self, files=None):
        self.files = files
        self.__symbol_count = 143354

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
            # Get the raw bit data of the current file and save the original just-in-case
            bit_repr = self._get_bitstring(i)
            # Chop into 3-bit or less segments and save separately
            bit_repr_chopped = (bit_repr[i:i+1] for i in range(0, len(bit_repr), 1))

            # Iterate through all 3 or less bit segments
            for d in bit_repr_chopped:
                # Assign color to segment
                # 3-bit colors
                if len(d) == 1:
                    if d == '0':
                        color = 'b'
                    elif d == '1':
                        color = 'w'
                else:
                    print('ERROR')
                    break

                color_array.append(color)

        # Print the number of fields that it will take to encode the file
        print(list(((color_array[i:i+self.__symbol_count] for i in range(0, len(color_array), self.__symbol_count))))[0])
        print(len(list((color_array[i:i+self.__symbol_count] for i in range(0, len(color_array), self.__symbol_count)))))
