import cv2
import os
import time

def capture_image_from_webcam(output_folder):
    # Try to open the webcam
    cap = cv2.VideoCapture(0)
    
    # Check if the webcam is opened successfully
    if not cap.isOpened():
        # print("Error: No webcam available")
        return
    
    # Capture a frame from the webcam
    ret, frame = cap.read()
    
    # Check if the frame is captured successfully
    if ret:
        # Define the path to save the image
        image_path = os.path.join(output_folder, 'captured_image.jpg')
        
        # Save the captured image
        cv2.imwrite(image_path, frame)
        # print(f"Image saved successfully at: {image_path}")
    else:
        # print("Error: Failed to capture image")
        pass
    
    # Release the webcam
    cap.release()

if __name__ == "__main__":
    output_folder = 'captured_images'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    a = time.time()
    capture_image_from_webcam(output_folder)
    print(f"Time: {time.time() - a}")
