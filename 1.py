import cv2
import face_recognition
from PIL import Image
import math
from functools import reduce
import operator
import os
import json as simplejson
import pickle

# Get a reference to webcam
video_capture = cv2.VideoCapture(0)
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
    print(face_locations)
    if face_locations:
        cv2.imwrite('loh2.png', frame)
        unknown_image = face_recognition.load_image_file("loh2.png")
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        known_image = face_recognition.load_image_file("pics/loh.png")
        biden_encoding = face_recognition.face_encodings(known_image)[0]
        #f = open('output.txt', 'wb')
        with open("txt.txt","wb") as fp:
            pickle.dump(unknown_encoding, fp)
        with open("test.txt", "rb") as fp:
            b = pickle.load(fp)
        #print(unknown_encoding, file=f)
        # f.close()
        # f = open('output.txt', 'r')
        # txt = f.read()
        results = face_recognition.compare_faces(b, unknown_encoding)
        print (results)

        #for filename in os.listdir("pics/"):
            #known_image = face_recognition.load_image_file("pics/" + filename)
            #biden_encoding = face_recognition.face_encodings(known_image)[0]
            #print (biden_encoding)
            #simplejson.dump([biden_encoding], f)
            #results = face_recognition.compare_faces([biden_encoding], unknown_encoding)
        #for filename in os.listdir("pics/"):
          #  known_image = face_recognition.load_image_file("pics/" + filename)
           # biden_encoding = face_recognition.face_encodings(known_image)[0]
           # print (biden_encoding)
           # print("\n")
           # results = face_recognition.compare_faces([biden_encoding], unknown_encoding)
        #f.close()
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
