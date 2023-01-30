import cv2
import tensorflow as tf

# Load a video using OpenCV's VideoCapture
cap = cv2.VideoCapture('path/to/video.mp4')

# Set the frame interval
frame_interval = 20

# Initialize the frame count and index
frame_count = 0
frame_index = 0

# Loop until the end of the video
while True:
    # Read a frame from the video
    ret, frame = cap.read()
    
    # Break if there is no more frame to read
    if not ret:
        break

    # Increment the frame count
    frame_count += 1

    # If the current frame count is equal to the frame interval
    if frame_count == frame_interval:
        # Reset the frame count
        frame_count = 0

        # Extract the set of frames and convert them to a tensor
        frames = tf.expand_dims(tf.stack([frame[frame_index:frame_index+frame_interval]]), axis=0)

        # Perform inference on the frames and extract the class with the highest probability
        class_idx = tf.argmax(model(frames), axis=-1)

        # Print the class label
        print("Predicted class for frame interval ", frame_index, " to ", frame_index + frame_interval - 1, ": ", class_idx)

        # Increment the frame index
        frame_index += frame_interval

