from operator import truediv
import sys
import socket
import cv2
import numpy
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSlot
from PyQt5 import QtCore
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QCoreApplication

IP = "127.0.0.1"
PORT = 9000
login_id = ""

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((IP, PORT))

def check_rcv():  # 서버에서 받아오기
    while True:
        ck = sock.recv(1024)
        ck = ck.decode()
        if sys.getsizeof(ck) >= 1:
            break
    return ck



class Join(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("join.ui", self)
        
        self.idcheck_btn.clicked.connect(self.id_check)
        self.pwcheck_btn.clicked.connect(self.pw_check)
        self.signup_btn.clicked.connect(self.signup)
        self.pw_txt.setEnabled(False)
        self.pw2_txt.setEnabled(False)
        self.name_txt.setEnabled(False)
        self.pwcheck_btn.setEnabled(False)
        self.signup_btn.setEnabled(False)
    
    def id_check(self):
        id = self.id_txt.text()
        sock.send(("idcheck/" + id).encode());
        check = check_rcv()
        if(check == "OK"):
            QMessageBox().information(self, "", "사용가능")
            self.pw_txt.setEnabled(True)
            self.pw2_txt.setEnabled(True)
            self.pwcheck_btn.setEnabled(True)

        else:
            QMessageBox().information(self, "", "ID중복")


    def pw_check(self):
        pw1 = self.pw_txt.text()
        pw2 = self.pw2_txt.text()
        if pw1 == pw2:
            QMessageBox().information(self, "", "비밀번호 일치")
            self.name_txt.setEnabled(True)
            self.signup_btn.setEnabled(True)
        else:
            QMessageBox().information(self, "", "비밀번호 불일치")

    def signup(self):
        id = self.id_txt.text()
        pw = self.pw_txt.text()
        name = self.name_txt.text()
        sock.send(("signup/" + id + "/" + pw + "/" + name +"/").encode())
        QMessageBox().information(self, " ", "회원가입 완료")
        self.close()


class Login(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("login.ui", self)

        self.login_btn.clicked.connect(self.try_login)
        self.signup_btn.clicked.connect(self.signup)

    
    def try_login(self):
        id = self.id_txt.text()
        pw = self.pw_txt.text()
        login_info = "login/" + id + "/" + pw
        login_id = id
        print("id : " + login_id)
        
        sock.send(login_info.encode())
        main_window = Mainwindow(login_id)
        main_window.exec_()

   
    def signup(self):
        signup_window = Join()
        signup_window.exec_()


class Mainwindow(QDialog):
    running = True
    def __init__(self, ID):
        super().__init__()
        
        self.ui = uic.loadUi("main.ui", self)

        self.id_txt.setText(ID)
        self.check_btn.clicked.connect(self.check)
        cap = cv2.VideoCapture(0)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.label.resize(width, height)
        #self.label.setText("여기")
        #while self.running:
        ret, img = cap.read()
        if ret:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, c = img.shape
            qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.label.setPixmap(pixmap)
        else:
            QMessageBox().information(self, "error", "cannot read frame")
        #break
        cap.release()

    def check(self):
        sock.send("check".encode())
        capture = cv2.VideoCapture(0)
        ret, frame = capture.read()

        #추출한 이미지를 String 형태로 변환(인코딩)시키는 과정
        encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        data = numpy.array(imgencode)
        stringData = data.tostring()

        #String 형태로 변환한 이미지를 socket을 통해서 전송
        sock.send( str(len(stringData)).encode());
        print(len(stringData))
        sock.send(stringData);
        self.running = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Login()
    window.show()
    app.exec_()
