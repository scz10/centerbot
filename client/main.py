import cv2
import time
import random
import json
from paho.mqtt import client as mqtt_client


broker = 'broker.emqx.io'
port = 1883
topic = "XXXXXXXXX" # fill this with channel name you input on arduino code
client_id = f'python-mqtt-{random.randint(0, 1000)}'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def send_data(x, y):
    if 0 <= x or y <= 180:
        client.publish(topic, json.dumps({'x': x, 'y': y}))
    else:
        return

# Load the cascade

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# To capture video from webcam. 
cap = cv2.VideoCapture(2) # edit this with ur video capture device ID
_, frame = cap.read()
rows, cols, _ = frame.shape
detected_x = 0
detected_y = 0
position_x = 90
position_y = 90
temp_x = 90
temp_y = 90
# To use a video file as input 
# cap = cv2.VideoCapture('filename.mp4')

    

client = connect_mqtt()
client.loop_start()


while True:
    # Read the frame
    _, img = cap.read()
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Detect the faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2,
	minNeighbors=5, minSize=(80, 80),
	flags=cv2.CASCADE_SCALE_IMAGE)
    # Draw the rectangle around each face
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.line(img, (x+w//2, y), (x+w//2, y+h), (0, 0, 255), 2)
        # below circle to denote mid point of center line
        center = (x+w//2, y+h//2)
        radius = 2
        cv2.circle(img, center, radius, (255, 255, 0), 2)
        detected_x = int(x+w//2)
        detected_y = int(y+h//2)
        #time.sleep(2.0)

    # Display
    if detected_x != 0:
        if 320 < detected_x - 50:
            if 0 <= position_x + 5 <= 180:
                position_x += 4
        elif 320 > detected_x + 70:
            if 0 <= position_x - 5 <= 180:
                position_x -= 4

    if detected_y != 0:
        if 265 < detected_y - 80:
            if 0 <= position_y + 5 <= 180:
                position_y += 4
        elif 265 > detected_y + 80:
            if 0 <= position_y - 5 <= 180:
                position_y -= 4

    
    time.sleep(0.2)
    cv2.imshow('img', img)

    if detected_x or detected_y != 0:
        if temp_x != position_x or temp_y != position_y:
            print(rows//2, detected_x, position_x, cols//2, detected_y, position_y)
            send_data(position_x, position_y)
            detected_x, detected_y = 0,0
            temp_x, temp_y = position_x, position_y

    # Stop if escape key is pressed
    k = cv2.waitKey(30) & 0xff
    if k==27:
        break

# Release the VideoCapture object
cap.release()