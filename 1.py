import cv2
import face_recognition
 
# Get a reference to webcam
video_capture = cv2.VideoCapture(0)
image =  face_recognition.load_image_file("loh.png")
# Initialize variables
face_locations = []
 
while True:
	
# Grab a single frame of video
	
    ret, frame = video_capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	
# Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
	
    rgb_frame = frame[:, :, ::-1]
 
	
# Find all the faces in the current frame of video
	
    face_locations = face_recognition.face_locations(rgb_frame)
    # print(face_locations)
    if face_locations:
        cv2.imwrite('loh2.png', frame)
        biden_encoding = face_recognition.face_encodings(frame)[0]
        unknown_encoding = face_recognition.face_encodings(image)[0]
        results = face_recognition.compare_faces([biden_encoding], unknown_encoding)
        print(results)
        break
       

# Display the results
	
    # for top, right, bottom, left in face_locations:
    	
    # # # Draw a box around the face
            
    #     cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 192), 2)
    print(frame)
    
        
    # Display the resulting image
        
    cv2.imshow('Video', frame)
    
        
    # Hit 'q' on the keyboard to quit!
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
       
        break
 
# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()