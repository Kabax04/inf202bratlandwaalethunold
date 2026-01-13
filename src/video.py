import cv2

n_frames = 250
img_template = "tmp/img_{:04d}.png"
output_video = "video.avi"

# Read first frame to get size
frame = cv2.imread(img_template.format(0))
height, width, layers = frame.shape

# Define video writer
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
video = cv2.VideoWriter(output_video, fourcc, 10, (width, height))

for i in range(n_frames):
    img = cv2.imread(img_template.format(i))
    if img is None:
        raise RuntimeError(f"Missing frame {i}")
    video.write(img)

video.release()
cv2.destroyAllWindows()

print(f"Video saved as {output_video}")
