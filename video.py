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
            print(bit_repr)
