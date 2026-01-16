import cv2
from pathlib import Path

"""
Generate a video from simulation images stored in the tmp directory.

Uses opencv-python to assemble a sequence of images into a video.
The first image defines the frame size of the video, and the result video is stored as an AVI file.
"""
output_video = "video.avi"  # output name and filetype

frames = sorted(Path("tmp").glob("img_*.png"))
if not frames:
    raise RuntimeError("No frames found in tmp/. Cannot create video.")

# Read first frame to get size
frame = cv2.imread(str(frames[0]))
if frame is None:
    raise RuntimeError(f"Could not read first frame: {frames[0]}")

height, width, layers = frame.shape

# Define video writer
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
video = cv2.VideoWriter(output_video, fourcc, 15, (width, height))

# Iterate through frames and write them to the video if they exist
for frame_path in frames:
    img = cv2.imread(str(frame_path))
    if img is None:
        raise RuntimeError(f"Could not rad frame: {frame_path}")
    video.write(img)

video.release()
cv2.destroyAllWindows()

print(f"Video saved as {output_video}")
