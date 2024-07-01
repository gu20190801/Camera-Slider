import cv2
import numpy as np
import serial
import time
import urllib
import urllib.request

# CONNECT WITH THE ARDUINO BOARD VIA SERIAL PORT
arduinoData=serial.Serial('COM5', 115200)

# DarkNet: https://github.com/AlexeyAB/darknet or https://pjreddie.com/darknet/
# Pre-trained Model from: https://github.com/Asadullah-Dal17/yolov4-opencv-python (CONFIGURATION & WEIGHTS FILES)

###### IP Camera: IP Config ######
url = 'http://192.168.112.127:8080/shot.jpg'
#################################

# LOADING YOLO MODEL WITH YOLO4 CONFIGURATION AND WEIGHTS
net = cv2.dnn.readNetFromDarknet('yolov4.cfg', 'yolov4.weights') # Use absolute path if not working
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

conf_threshold = 0.5
objects = []
tracked_object = None

# LOADING YOLO MODEL's CLASS LABELS
with open('classes.txt', 'r') as f:
    classes = f.read().splitlines()

###### Code for build-in camera ######
# cap = cv2.VideoCapture(0)
######################################

mode = 0

while True:
    ###### Code for IP Camera ######
    # SETTING UP IP CAMERA AND GET THE CURRENT FRAME
    imgResp = urllib.request.urlopen(url)
    imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
    img = cv2.imdecode(imgNp, -1)
    ###############################

    ###### Code for build-in camera ######
    # ret, frame = cap.read()

    #if not ret:
    #    break
    ######################################

    height, width, channels = img.shape

    # PREPROCESSES THE FRAME AND CREATES A BLOB FOR INPUT TO THE NEUTRAL NETWORK
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []

    # PASSES THE BLOB THROUGH THE NETWORK AND OBTAINS THE OUTPUT PREDICTIONS
    # FILTERS THE PREDICTIONS BASED ON CONFIDENCE THRESHOLD AND PERFORMS NON-MAXIMUM SUPPRESSION
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > conf_threshold:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, 0.4)
   
    maxWidth = 0
    resultX = 0

    # DRAW BOUNDING BOXES AND LABELS ON THE DETECTED OBJECTS
    if len(indices) > 0:
        for i in indices.flatten():
            x, y, w, h = boxes[i]
            label = classes[class_ids[i]]
            cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)

            # GET THE CENTER POINT POINT OF THE "SUBJECT" (THE LARGEST BOUNDING BOX) IN THE FRAME
            cv2.line(img, (0, int(y + h / 2)), (width, int(y + h / 2)), (0, 0, 255), 2)
            cv2.line(img, (int(x + w / 2), 0), (int(x + w / 2), height), (0, 0, 255), 2)
            if w > maxWidth:
                maxWidth = w
                resultX = x+w/2

        centerX = int(resultX - width/2)
        result = str(centerX)
        ###### Code for Returning Exact Values ######
        # result = result + '\r'
        # serialOutput = result.encode()
        #############################################
        print(f"Width: {width}, Height: {height}, CenterX: {resultX}, Diff: {centerX}")

       # SENDING COMMANDS TO ARDUINO FOR SUBJECT POSITION IDENTIFICATION
        if (centerX > 0): # If subject is at the right side of the frame
          arduinoData.write(b'1')
        else:   # If subject is at the left side of the frame
          arduinoData.write(b'2')

    cv2.imshow('webcam', img)

    # SLIDER CONTROLS:
    # KEY '7' FOR SLIDING MOVEMENT RIGHT TO LEFT
    # KEY '8' FOR SLIDING MOVEMENT LEFT TO RIGHT
    # KEY '9' FOR STOPPING THE SLIDER
    if cv2.waitKey(1) & 0xFF == ord('7'):
        mode = 1
        arduinoData.write(b'7')  # Send '1' to Arduino to switch mode
        print("Switched to Mode 1: Right to Left")

    if cv2.waitKey(1) & 0xFF == ord('8'):
        mode = -1
        arduinoData.write(b'8')
        print("Switched to Mode 2: Left to Right")
    if cv2.waitKey(1) & 0xFF == ord('9'):
        mode = 0
        arduinoData.write(b'9')
        print("Slider Stopped")

    # QUIT .EXE
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

###### Code for build-in camera ######
# cap.release()
######################################

cv2.destroyAllWindows()
