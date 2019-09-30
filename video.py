# This is a class make_video.py and decode_video.py will use

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
        for i in self.files:
            bit_repr = self._get_bitstring(i)
            bit_repr_chopped = (bit_repr[i:i+3] for i in range(0, len(bit_repr), 3))
            for d in bit_repr_chopped:
                if len(d) == 3:
                    if d == '000':
                        print('black, 000')
                    elif d == '111':
                        print('white, 111')
                    elif d == '100':
                        print('blue, 100')
                    elif d == '110':
                        print('green, 110')
                    elif d == '101':
                        print('red, 101')
                    elif d == '010':
                        print('purple, 010')
                    elif d == '011':
                        print('yellow, 011')
                    elif d == '001':
                        print('pink, 001')
                    else:
                        print('ERROR')
                else:
                    for item in d:
                        if item == '0':
                            print('brown,', item)
                        elif item == '1':
                            print('orange,', item)

        # print(len([bit_repr[i:i+3000] for i in range(0, len(bit_repr), 3000)]))
