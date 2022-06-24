# import the necessary packages
from project.utils import Conf
from imutils.video import VideoStream
from datetime import datetime
from datetime import date
from tinydb import TinyDB
from tinydb import where
import face_recognition
import numpy as np
import argparse
import imutils
import pickle
import time
import cv2
from imutils import face_utils
from twilio.rest import Client
import serial
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

UserName = "epalanisamy4@gmail.com"
UserPassword = "sieora@123"
Server = 'smtp.gmail.com:587'
class_start_time = "20:44:00"
class_end_time = "20:54:00"


def create_msg():
    msg = MIMEMultipart()
    msg['Subject'] = 'Class1'
    msg['From'] = 'epalanisamy4@gmail.com'
    msg['To'] = 'saikalyanbhupathi6@gmail.com'
    text = MIMEText("Class Report")
    msg.attach(text)
    return msg


def SendMail(msg):
    s = smtplib.SMTP(Server)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(UserName, UserPassword)
    s.sendmail("epalanisamy4@gmail.com", "suryakiran827@gmail.com", msg.as_string())
    s.quit()


def attach_file(msg_cont):
    f = open(file_path)
    image = MIMEText(f.read())
    msg_cont.attach(image)
    return msg_cont

ser = serial.Serial('COM3', 9600, timeout=0)

def sendsms(a):
    account_sid = 'ACd9544684e452154d443004131c82212c'
    auth_token = '24333a18c338433d37f2e17da45c934c'
    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
        body="student " + a + " is doing anti spoofing activity",
        from_='+15305136942',
        to='+918639308909'
    )
    print(message.sid)
    print("sms sent")


ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", default="config/config.json",
                help="Path to the input configuration file")
args = vars(ap.parse_args())
conf = Conf(args["conf"])
prevPerson = None
curPerson = None
consecCount = 0
global input_data, final_data
input_data = ""
final_data = []
db = TinyDB(conf["db_path"])
studentTable = db.table("student")
attendanceTable = db.table("attendance")
recognizer = pickle.loads(open(conf["recognizer_path"], "rb").read())
le = pickle.loads(open(conf["le_path"], "rb").read())
print("[INFO] warming up camera...")
vs = VideoStream(src=0).start()
time.sleep(2.0)
prevPerson = None
curPerson = None
file_path = "a.txt"
global student1, student2, student3, student1_flag, student2_flag, student3_flag
student1 = "kalyan"
student2 = "surya"
student3 = "amarnath"
global temp_flag
temp_flag = 0
student1_flag = 0
student2_flag = 0
student3_flag = 0
global value, final_temp
value = 0
final_temp = 0
temp = 0


while True:
    inbuff = ser.inWaiting()
    if (inbuff > 0):
        input_data = str(ser.readline().decode('utf-8'))
        final_temp = int(input_data) + 7
        if (len(input_data) == 2):
            print(final_temp)
            if (final_temp <= 39 and final_temp >= 36):
                print("normal")
                temp_flag = 0
            else:
                # print("abnormal")
                temp_flag = 1

    frame = vs.read()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    if (current_time >= class_start_time and current_time < class_end_time):
        h, w, _ = frame.shape
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (640, 480))
        img_mean = np.array([127, 127, 127])
        img = (img - img_mean) / 128
        img = np.transpose(img, [2, 0, 1])
        img = np.expand_dims(img, axis=0)
        rgb = img.astype(np.float32)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb,model=conf["detection_method"])

        for (top, right, bottom, left) in boxes:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        if len(boxes) > 0:
            value = right - left
            print(value)
            encodings = face_recognition.face_encodings(rgb, boxes)
            preds = recognizer.predict_proba(encodings)[0]
            j = np.argmax(preds)
            curPerson = le.classes_[j]

            if prevPerson == curPerson:
                consecCount += 1
            else:
                consecCount = 0
            prevPerson = curPerson

            if (consecCount > 1):
                name = studentTable.search(where(curPerson))[0][curPerson][0]
                label = "{}, you are now marked as present in {}".format(name, conf["class"])

                if name == "kalyan":
                    if (value >= 100):
                        if (temp_flag == 0):
                            print("student 1 success")
                            student1_flag = 1
                            consecCount = 0
                        else:
                            sendsms("kalyan")
                            # print(" venkateshanti")
                    else:
                        sendsms("kalyan")
                        # print(" venkateshanti")
                elif name == "surya":
                    if (value >= 150):
                        if (temp_flag == 0):
                            print("student 2 success")
                            student2_flag = 1
                            consecCount = 0
                        else:
                            sendsms("surya")
                            # print(" Lingeshwar anti")
                    else:
                        sendsms("surya")
                        # print(" Lingeshwar anti")
                elif name == "amarnath":
                    if (value >= 150):
                        if (temp_flag == 0):
                            print("student 2 success")
                            student3_flag = 1
                            consecCount = 0
                        else:
                            sendsms("amarnath")
                            # print(" Lingeshwar anti")
                    else:
                        sendsms("amarnath")
                        # print(" Lingeshwar anti")
                cv2.putText(frame, label, (5, 175),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            cv2.putText(frame, "class started", (100, 100),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # show the frame
        elif (current_time == class_end_time):
            print("ended")
            f = open("a.txt", "r+")
            f.truncate(0)  # need '0' when using r+
            f = open("a.txt", "a+")
            if student1_flag == 1:
                f.write("\n" + "kalyan" + " " + "is present")
            else:
                f.write("\n" + "kalyan" + " " + "is absent")


            if student2_flag == 1:
                f.write("\n" + "surya" + " " + "is present")
            else:
                f.write("\n" + "surya" + " " + "is absent")

            if student3_flag == 1:
                f.write("\n" + "amarnath" + " " + "is present")
            else:
                f.write("\n" + "amarnath" + " " + "is absent")
            f.close()
            cv2.putText(frame, "class Ended", (100, 100),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            msg_head = create_msg()
            attach = attach_file(msg_head)
            SendMail(attach)
            student1_flag = 0
            student2_flag = 0
            break
        cv2.imshow("Antispoofing System", frame)
        key = cv2.waitKey(1) & 0xFF
        # check if the `q` key was pressed

        if key == ord("q"):
            break
                # # show the frame
                # cv2.imshow("Attendance System", frame)
                # key = cv2.waitKey(1) & 0xFF
                # check if the `q` key was pressed
                # if key == ord("q"):
                # break
print("[INFO] cleaning up...")
vs.stop()
# db.close()
