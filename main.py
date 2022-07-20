import socket
import cv2
import sys
import numpy
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap


IP = "127.0.0.1"
PORT = 9000
login_id = ""
picture = False

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((IP, PORT))

def check_rcv():  # 서버에서 받아오기
    while True:
        ck = sock.recv(1024)
        ck = ck.decode()
        print(ck)
        if sys.getsizeof(ck) >= 1:
            break
    return ck


class Thread(QThread):
    changePixmap = pyqtSignal(QImage)
    
    def run(self):
        global picture
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

            if picture:
                #추출한 이미지를 String 형태로 변환(인코딩)시키는 과정
                encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
                result, imgencode = cv2.imencode('.jpg', frame, encode_param)
                data = numpy.array(imgencode)
                stringData = data.tostring()

                #String 형태로 변환한 이미지를 socket을 통해서 전송
                sock.send( str(len(stringData)).encode());
                sock.send(stringData);
                picture = False
                
            if not ret:
                cap.release()
                


class Login(QDialog):
    global login_id
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("login.ui", self)
        self.login_btn.clicked.connect(self.try_login)
        self.label.hide()
        self.loginid.hide()
        self.stu.hide()
        self.check_btn.hide()


    def try_login(self):
        id = self.id_txt.text()
        pw = self.pw_txt.text()
        login_info = "login/" + id + "/" + pw
        login_id = id
        
        sock.send(login_info.encode())
        login_pass = check_rcv()
        if(login_pass == "PASS"):
            self.id_label.hide()
            self.pw_label.hide()
            self.login_btn.hide()
            self.signup_btn.hide()
            self.id_txt.hide()
            self.pw_txt.hide()
            self.initUI(login_id)
        else:
            QMessageBox().information(self, "", "ID/PW 불일치") 
        


    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def initUI(self, login_id):
        self.setWindowTitle("main_window")
    
        self.resize(700, 500)

        
        self.label.show()
        self.loginid.setText(login_id)
        self.loginid.show()
        self.stu.show()
        self.check_btn.show()
        self.check_btn.clicked.connect(self.check)

        self.label.move(30, 30)
        self.label.resize(640, 480)
        self.th = Thread(self)
        self.th.changePixmap.connect(self.setImage)
        
        self.th.start()
        self.show()


    def check(self):
        global picture
        sock.send("check".encode())
        picture = True
        msg = check_rcv()
        if(msg == "OK"):
            QMessageBox().information(self, "", "출석 인정")
        else:
            QMessageBox().information(self, "", "얼굴 인식 부정확")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = Login()
    a.show()
    
    app.exec_()