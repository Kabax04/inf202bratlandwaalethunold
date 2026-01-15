import cv2
"""
Generate a video from simulation images stored in the tmp directory.

Uses opencv-python to assemble a sequence of images into a video.
The first image defines the frame size of the video, and the result video is stored as an AVI file.
"""
n_frames = 250  # Number of frames based on tEnd/dt
img_template = "tmp/img_{:04d}.png"  # where to look for the images
output_video = "video.avi"  # output name and filetype

# Read first frame to get size
frame = cv2.imread(img_template.format(0))
height, width, layers = frame.shape

# Define video writer
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
video = cv2.VideoWriter(output_video, fourcc, 15, (width, height))

# Iterate through frames and write them to the video if they exist
for i in range(n_frames):
    img = cv2.imread(img_template.format(i))
    if img is None:
        raise RuntimeError(f"Missing frame {i}")
    video.write(img)

video.release()
cv2.destroyAllWindows()

print(f"Video saved as {output_video}")
