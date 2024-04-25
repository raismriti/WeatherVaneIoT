#! /usr/bin/python
# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import board
import csv
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
# Import bme280 script
from adafruit_bme280 import basic as adafruit_bme280
i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)
# create the mcp object
mcp = MCP.MCP3008(spi, cs)
# create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)
print("chan= ", chan) 

#Initialize 'currentname' to trigger only when a new person is identified.
currentname = "unknown"
#Determine faces from encodings.pickle file model created from train_model.py
encodingsP = "encodings.pickle"

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
print("[INFO] loading 2 factor authorization...")
print("Prepare for Face Scan")
data = pickle.loads(open(encodingsP, "rb").read())
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

# start the FPS counter
fps = FPS().start()

# loop over frames from the video file stream
while True:
    # grab the frame from the threaded video stream and resize it
    # to 500px (to speedup processing)
    frame = vs.read()
    frame = imutils.resize(frame, width=500)
    # Detect the fce boxes
    boxes = face_recognition.face_locations(frame)
    # compute the facial embeddings for each face bounding box
    encodings = face_recognition.face_encodings(frame, boxes)
    names = []

    # loop over the facial embeddings
    for encoding in encodings:
        # attempt to match each face in the input image to our known
        # encodings
        matches = face_recognition.compare_faces(data["encodings"],
            encoding)
        name = "Unknown" #if face is not recognized, then print Unknown

        # check to see if we have found a match
        if True in matches:
            # find the indexes of all matched faces then initialize a
            # dictionary to count the total number of times each face
            # was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            # loop over the matched indexes and maintain a count for
            # each recognized face face
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            # determine the recognized face with the largest number
            # of votes (note: in the event of an unlikely tie Python
            # will select first entry in the dictionary)
            name = max(counts, key=counts.get)

            #If someone in your dataset is identified, print their name on the screen
            if currentname != name:
                currentname = name
                print(currentname)
                print("Authorized")
#Take and Upload pic to AWS                 
                print("Welcome " + currentname)
                time.sleep(3)
                while True:     
                    # Read BME280 Readings
                    bme280.sea_level_pressure = 1015.91
                    filename = "Weather_Records.csv"
                    with open(filename, 'w', newline= '') as csvfile:
                        csvwriter = csv.writer(csvfile)
                        while True:
                            wind_speed = "{:.2f}".format((chan.value - 125) * 0.0648 + 8.1)
                            temperatureF = "{:.2f}".format((bme280.temperature * 9/5) + 32)
                            pressure = "{:.2f}".format((bme280.pressure * 0.02953))
                            humidity = "{:.2f}".format(bme280.relative_humidity)
                            altitude = "{:.2f}".format(bme280.altitude)
                            print("chan= ", chan.value)
                            rows = ['Temperature(F): ' ,temperatureF,
                                    'Humidity(%)', humidity,'Pressure(Hg)', pressure, 'Altitude(m)', altitude,'Wind Speed(m/s)', wind_speed]
                               
                            # writing the data rows  
                            csvwriter.writerows([rows])
                            csvfile.flush()  # Flush the buffer to ensure immediate writing
                        
                            print("\nTemperature: "  ,temperatureF)
                            print("Humidity: " ,bme280.relative_humidity)
                            print("Pressure: inHg" ,pressure)
                            print("Altitude = ", bme280.altitude)
                            print("Wind Speed: " +str(wind_speed) + " meter/second" )
                            time.sleep(3)
                        # Wait

                                
                        time.sleep(2)
        # update the list of names
        names.append(name)

    # loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # draw the predicted face name on the image - color is in BGR
        cv2.rectangle(frame, (left, top), (right, bottom),
            (0, 255, 225), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
            .8, (0, 255, 255), 2)

    # display the image to our screen
    cv2.imshow("Facial Recognition is Running", frame)
    key = cv2.waitKey(1) & 0xFF

    # quit when 'q' key is pressed
    if key == ord("q"):
        break

    # update the FPS counter
    fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()

