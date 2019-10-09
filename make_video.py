# This project is to create a video that is recordable onto a VHS tape
# which contains data.

# This script creates a video using the specified file or folder.


# Setup section

import argparse
import os
import video

# Set up the argument parser
parser = argparse.ArgumentParser(description='Makes a recordable video from a file or folder')
parser.add_argument('format', metavar='f', type=str, nargs='+', help='Video format (vhs / s-vhs)')
parser.add_argument('file', metavar='F', type=str, nargs='+', help='File to encode')
args = parser.parse_args()

# End setup section

# Variables section

# Get the file argument
file_list_path = args.file[0]
# Make an empty list
file_list = []

# Script section

# Try to get the files in a directory
try:
    for i in os.listdir(file_list_path):
        file_list.append(file_list_path + '/' + i)
# If we can't, just use the name given and assume it's a file
except NotADirectoryError:
    # Make sure the file is valid
    if not os.path.isfile(file_list_path):
        raise FileNotFoundError
    file_list.append(file_list_path)

# Initialize the video class using the file list
video = video.Video(args.format[0], file_list)

video.encode()