# This is a class make_video.py and decode_video.py will use
# Currently using 50 symbols per field

import cv2
import bitstring


class Video:
    # Take in a list of files if encoding
    def __init__(self, files=None):
        self.files = files

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
            bit_repr_chopped = (bit_repr[i:i+3] for i in range(0, len(bit_repr), 3))

            # Iterate through all 3 or less bit segments
            for d in bit_repr_chopped:
                # Assign color to segment
                # 3-bit colors
                if len(d) == 3:
                    if d == '000':
                        color = 'black'
                    elif d == '111':
                        color = 'white'
                    elif d == '100':
                        color = 'blue'
                    elif d == '110':
                        color = 'green'
                    elif d == '101':
                        color = 'red'
                    elif d == '010':
                        color = 'purple'
                    elif d == '011':
                        color = 'yellow'
                    elif d == '001':
                        color = 'pink'
                    else:
                        print('ERROR')
                        break
                # Sub 3-bit colors
                else:
                    for item in d:
                        if item == '0':
                            color = 'brown'
                        elif item == '1':
                            color = 'orange'

                color_array.append(color)

        # Print out an item from the color array
        print(list((color_array[i:i+50] for i in range(0, len(color_array), 50)))[0])
