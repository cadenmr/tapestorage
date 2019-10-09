# This project is to create a video that is recordable onto a VHS tape
# which contains data.

# This script creates a video using the specified file or folder.


# Setup section

import argparse
import os
import video

# Set up the argument parser
parser = argparse.ArgumentParser(description='Decodes a video from a VHS tape')
parser.add_argument('format', metavar='f', type=str, nargs='+', help='Video format (vhs / s-vhs)')
parser.add_argument('file', metavar='F', type=str, nargs='+', help='File to decode')
parser.add_argument('file_out', metavar='F', type=str, nargs='+', help='File to write')
args = parser.parse_args()

# End setup section

# Variables section

# Get the file argument
file_list_path = args.file[0]
file_out = args.file_out[0]

# Script section

if not os.path.isfile(args.file[0]):
    raise FileNotFoundError

# Initialize the video class using the file list
video = video.Video(args.format[0], args.file[0], file_out)

video.decode()