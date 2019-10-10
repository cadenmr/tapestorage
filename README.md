# tapestorage
This is a project to store data on VHS tapes.

`make_video.py` uses the `Video` class in `video.py` to generate a recordable video.

`decode_video.py` uses the `Video` class in `video.py` to decode a video.


## Current Status
* Has not been tested with a VHS recording and OpenCV will probably need tuning for it (need a capture device)
* Code needs housekeeping
* Untested on macOS and Windows, YMMV

## Requirements
* Python 3.6 or newer
* opencv-python
* bitstring module

## Instructions
Simply clone the repo and use the `-h` flag on `make_video.py` and `decode_video.py` to see usage information
