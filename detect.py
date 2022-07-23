import numpy as np
import cv2

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
count = 0
for i in range(1, 1532):

    f = 'dataset7/1.%d.jpg' %i
    print(f)
    img = cv2.imread(f)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    #faces = face_cascade.detectMultiScale(gray)

    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        count +=1
        cv2.imwrite("dataset8/2" + '.' + str(count) + ".jpg", gray[y:y+h, x:x+w])
        print(count)



