import cv2
import face_recognition
 
def face_capture():
    # Get a reference to webcam
    video_capture = cv2.VideoCapture(0)
    # Initialize variables
    face_locations = []
     
    while True:
            
    # Grab a single frame of video
            
        ret, frame = video_capture.read()
        if ret is False:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            
        rgb_frame = frame[:, :, ::-1]
     
            
    # Find all the faces in the current frame of video
            
        face_locations = face_recognition.face_locations(rgb_frame)
        # print(face_locations)
        if face_locations:
            return frame
