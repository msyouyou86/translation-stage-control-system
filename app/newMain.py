# import os.path
import sys
import os.path
import time

from PyQt5.QtWidgets import *
# from PyQt5.QtGui import *
from PyQt5.QtCore import *
from newGUI import *
# from main_GUI import *
from serCom import *
from datetime import datetime
from queue import Queue

motor_port = "/dev/ttyUSB2"
motor_band = 57600
hft_port = "/dev/ttyUSB1"
hft_band = 9600

hft_x_cmd_ab = '01 03 00 02 00 02 65 CB'
hft_y_cmd_ab = '02 03 00 02 00 02 65 F8'

hft_x_cmd_re = '01 03 00 01 00 01 0D 0A'
hft_y_cmd_re = '02 03 00 01 00 01 0D 0A'

hft_xset0_cmd = '01 06 00 10 00 00 88 0F'
hft_yset0_cmd = '02 06 00 10 00 00 88 3C'

X0 = None
Y0 = None

loading = False
motor_com_error = False


def save2logfile(item0, item1, item2):
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = 'log_' + date_str + '.txt'
    file_path = filename
    f = open(file_path, 'a')
    f.write(item0 + '\t' + item1 + '\t' + item2 + '\n')
    f.close()


def save2pos(content):
    filename = 'InitPos.txt'
    f = open(filename, 'r')
    file_content = f.read()
    index = file_content.find('Y')
    if content.find('X') >= 0:
        y_string = file_content[index:]
        new_string = content + y_string
    else:
        x_string = file_content[:index]
        new_string = x_string + content

    f = open(filename, 'w')
    f.write(new_string)
    f.close()


def read_file(file_path):
    f = open(file_path, 'r')
    content = f.read()
    index = content.find('Y')
    x_str = content[:index]
    # print('x str is ', x_str)
    y_str = content[index:]
    # print('y str is ', y_str)
    global X0
    global Y0
    X0 = x_str[2:]
    Y0 = y_str[2:]
    # print("In read_file func, X0 = %s, Y0 = %s" % (X0, Y0))


def init_xy(filepath):
    if not os.path.exists(filepath):
        content = 'X=0Y=0'
        f = open(filepath, 'w')
        f.write(content)
        f.close()
    else:
        f = open(filepath, 'r')
        content = f.read()
        if content.find('X') < 0:
            content = 'X=0' + content
        if content.find('Y') < 0:
            content = content + 'Y=0'
        f = open(filepath, 'w')
        f.write(content)
        f.close()


class MainGUI(Ui_MainWindow, QMainWindow):
    moveSignal = pyqtSignal(str)

    def __init__(self):
        super(MainGUI, self).__init__()
        self.setupUi(self)

        self.control_queue = Queue()

        init_xy('InitPos.txt')
        read_file('InitPos.txt')
        self.load_log()

        self.hft = HftMonitor(hft_port, hft_band, self.moveSignal)
        self.hft.update_hft.connect(self.update_hft)
        self.hft.log_signal.connect(self.log_handle)
        self.hft.start()

        self.motor = MotorMonitor(motor_port, motor_band, self.control_queue)
        self.motor.update_motor.connect(self.update_motor)
        self.motor.motor_stop.connect(self.motor_0_stop)
        self.motor.log_signal.connect(self.log_handle)
        # self.motor.motor_error.connect(self.motor_error_handle)
        self.motor.start()

        # self.disable_buttons()
        # self.motorControl = MotorControl(motor_port, motor_band, self.moveSignal)
        # self.motorControl.start()
        # self.control = MotorControl()
        # self.control.start()

        self.pushButton.clicked.connect(lambda: self.motor_move(self.pushButton.text(), self.lineEdit.text()))
        self.pushButton_2.clicked.connect(lambda: self.motor_move(self.pushButton_2.text(), self.lineEdit.text()))
        self.pushButton_4.clicked.connect(lambda: self.motor_move(self.pushButton_4.text(), self.lineEdit_4.text()))
        self.pushButton_5.clicked.connect(lambda: self.motor_move(self.pushButton_5.text(), self.lineEdit_4.text()))
        self.pushButton_3.clicked.connect(lambda: self.motor2(self.pushButton_3.text(), self.lineEdit.text(),
                                                              self.lineEdit_7.text()))
        self.pushButton_6.clicked.connect(lambda: self.motor2(self.pushButton_6.text(), self.lineEdit_4.text(),
                                                              self.lineEdit_8.text()))
        self.pushButton_7.clicked.connect(lambda: self.motor_0(self.pushButton_7.text()))
        self.pushButton_8.clicked.connect(lambda: self.motor_0(self.pushButton_8.text()))

        self.pushButton_11.clicked.connect(lambda: self.hft_move(self.pushButton_11.text(), self.lineEdit.text()))
        self.pushButton_12.clicked.connect(lambda: self.hft_move(self.pushButton_12.text(), self.lineEdit_4.text()))

        self.pushButton_9.clicked.connect(self.motor_stop)
        self.pushButton_10.clicked.connect(self.motor_stop)

    @pyqtSlot(str, str, str, str)
    def update_hft(self, hft_x, hft_y, hft_x_1, hft_y_1):
        self.lineEdit_3.setText(hft_x)
        self.lineEdit_5.setText(hft_y)
        self.lineEdit_2.setText(hft_x_1)
        self.lineEdit_6.setText(hft_y_1)

    @pyqtSlot(str, str)
    def update_motor(self, x, cmd):
        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if cmd.find('X') >= 0:
            try:
                x1 = int(x) - int(X0)
            except Exception as e:
                self.log(time_str, 'warning', e)
            else:
                self.lineEdit_7.setText(str(x1))
        elif cmd.find('Y') >= 0:
            try:
                y1 = int(x) - int(Y0)
            except Exception as e:
                self.log(time_str, 'warning', e)
            else:
                self.lineEdit_8.setText(str(y1))

    @pyqtSlot(str)
    def motor_0_stop(self, cmd):
        self.moveSignal.emit(cmd)

    # @pyqtSlot()
    # def motor_error_handle(self):
    #     global motor_com_error
    #     if not motor_com_error:
    #         time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #         self.log(time_str, 'error', 'Motor communication failure, please check motor controller.')
    #         motor_com_error = True

    @pyqtSlot(str, str)
    def log_handle(self, log_type, detail):
        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log(time_str, log_type, detail)

        if detail.find('0') >= 0:
            if detail.find('X') >= 0:
                global X0
                X0 = self.lineEdit_7.text()
                detail = 'X=' + X0
            else:
                global Y0
                Y0 = self.lineEdit_8.text()
                detail = 'Y=' + Y0

            save2pos(detail)
            self.log(time_str, log_type, detail)

    def disable_buttons(self):
        button_list = self.all_button_list
        for i in button_list:
            i.setEnabled(False)

    def hft_move(self, button, pos):
        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if pos == '':
            detail = "Before move, please input pulse first!"
            self.log(time_str, 'warning', detail)
        else:
            if button.find('X') >= 0:
                index = button.find('X')
                current_pos = self.lineEdit_3.text()
            else:
                index = button.find('Y')
                current_pos = self.lineEdit_5.text()

            move_sub = (int(pos) - int(current_pos)) * 1600 // 4096
            if move_sub >= 0:
                cmd = '#+' + button[index] + ' ' + str(move_sub) + '#'
            else:
                cmd = '#-' + button[index] + ' ' + str(abs(move_sub)) + '#'

            self.control_queue.put(cmd)

            detail = 'User send move cmd ' + ' ' + '\'' + cmd + '\''
            self.log(time_str, 'event', detail)

    def motor_move(self, button, pulse):
        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if pulse == '':
            detail = "Before move, please input pulse first!"
            self.log(time_str, 'warning', detail)
        else:
            cmd = '#' + button + ' ' + pulse + '#'
            # print("cmd is ", cmd)
            # self.moveSignal.emit(cmd)
            self.control_queue.put(cmd)
            # write log info

            detail = 'User send move cmd ' + ' ' + '\'' + cmd + '\''
            self.log(time_str, 'event', detail)

    def motor2(self, button, pulse, pos):
        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if pulse == '':
            detail = "Before move, please input pulse first!"
            self.log(time_str, 'warning', detail)
        elif pos != 'None' and pos != '':
            move = int(pulse) - int(pos)
            if move > 0:
                cmd = '#+' + button + ' ' + str(move) + '#'
            else:
                move = abs(move)
                cmd = '#-' + button + ' ' + str(move) + '#'
            # print('cmd is ', cmd)
            # self.moveSignal.emit(cmd)
            self.control_queue.put(cmd)

        if pulse != '':
            # write log info
            true_cmd = '#' + button + ' ' + str(pulse) + '#'
            detail = 'User send move cmd ' + ' ' + '\'' + true_cmd + '\''
            self.log(time_str, 'event', detail)

    def motor_0(self, button):
        if button.find('X') >= 0:
            cmd0 = '#+X 1000#'
            cmd = '#HX#'
        else:
            cmd0 = '#+Y 1000#'
            cmd = '#HY#'

        self.control_queue.put(cmd)

        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        detail = 'User send reset cmd ' + ' ' + '\'' + cmd + '\''
        self.log(time_str, 'event', detail)

    def load_log(self):
        global loading
        loading = True
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = 'log_' + date_str + '.txt'
        filepath = filename
        if os.path.exists(filepath):
            # read lines to table
            f = open(filepath)
            while True:
                line = f.readline()
                if line:
                    line_list = line.split('\t')
                    if len(line_list) == 3:
                        self.log(line_list[0], line_list[1], line_list[2])
                else:
                    break
        loading = False

    # def waiting_stop(self, button):
    #     if button.find('X') >= 0:
    #         hft_x = int(self.lineEdit_3.text())
    #         pos_x = int(self.lineEdit_7.text())
    #         num = 0
    #         time.sleep(0.5)
    #         while True:
    #             new_hft = int(self.lineEdit_3.text())
    #             new_pos = int(self.lineEdit_7.text())
    #             print("hft = %d , new_hft = %d " % (hft_x, new_hft))
    #             if -5 < new_hft - hft_x < 5 or -5 < new_pos - pos_x < 5 or num > 10:
    #                 break
    #             else:
    #                 hft_x = new_hft
    #                 pos_x = new_pos
    #                 num += 1
    #                 time.sleep(0.5)
    #         print("In waiting X stop func, num=", num)
    #     else:
    #         hft_y = int(self.lineEdit_5.text())
    #         pos_y = int(self.lineEdit_8.text())
    #         num = 0
    #         time.sleep(0.5)
    #         while True:
    #             new_hft = int(self.lineEdit_5.text())
    #             new_pos = int(self.lineEdit_8.text())
    #             print("hft = %d , new_hft = %d " % (hft_y, new_hft))
    #             if -5 < new_hft - hft_y < 5 or  -5 < new_pos - pos_y < 5 or num > 10:
    #                 break
    #             else:
    #                 hft_y = new_hft
    #                 pos_y = new_pos
    #                 num += 1
    #                 time.sleep(0.5)
    #         print("In waiting Y stop func, num=", num)

    def motor_stop(self):
        cmd = "$sss"
        # print("cmd is ", cmd)
        # self.moveSignal.emit(cmd)
        self.control_queue.put(cmd)

        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        detail = 'User send stop cmd ' + ' ' + '\'' + cmd + '\''
        self.log(time_str, 'event', detail)

    def log(self, time_str, log_type, detail):
        date_info = time_str.split(' ')[0]
        # print('new data info is ', date_info)
        row_pos = self.tableWidget.rowCount()
        if row_pos > 0:
            last_date = self.tableWidget.item(0, 0).text().split(' ')[0]
            # print('last data info is ', last_date)
            if last_date != date_info:
                # clear yesterday log
                self.tableWidget.setRowCount(0)
            row_pos = 0

        self.tableWidget.insertRow(row_pos)
        item_0 = QtWidgets.QTableWidgetItem(time_str)
        item_1 = QtWidgets.QTableWidgetItem(log_type)
        item_2 = QtWidgets.QTableWidgetItem(detail)
        self.tableWidget.setItem(row_pos, 0, item_0)
        self.tableWidget.setItem(row_pos, 1, item_1)
        self.tableWidget.setItem(row_pos, 2, item_2)

        if log_type == 'warning':
            self.tableWidget.item(row_pos, 1).setBackground(QtGui.QColor(237, 249, 91))
        elif log_type == 'error':
            self.tableWidget.item(row_pos, 1).setBackground(QtGui.QColor(244, 66, 66))

        if not loading:
            save2logfile(time_str, log_type, detail)

    # pulse = self.lineEdit.text()
    # if button == '+X' or button == '-X' or button == '+Y' or button == '-Y' or button == 'X' or button == 'Y':
    #     motor_move(motor_port, motor_band, hft_port, hft_band, button, pulse)
    # elif button == "Reset X" or button == "Reset Y":
    #     motor_0(motor_port, motor_band, hft_port, hft_band, button)


class HftMonitor(QThread):
    update_hft = pyqtSignal(str, str, str, str)
    log_signal = pyqtSignal(str, str)

    def __init__(self, port, band, sig):
        super(HftMonitor, self).__init__()
        self.ser = Communication(port, band)
        self.sig = sig
        self.cmd = None
        self.sig.connect(self.move)

    def run(self):
        print("Hft Monitor thread started...")
        self.ser.open_serial()
        if self.ser.check_status():
            while True:
                if self.cmd is None:
                    hft_x = self.ser.read_hft(hft_x_cmd_ab, 0)
                    if hft_x is None:
                        self.update_hft.emit(str(hft_x), str(hft_x), str(hft_x), str(hft_x))
                        self.log_signal.emit('error', 'Hft communication failure, please check serial cable')
                        time.sleep(2)
                    else:
                        hft_x_1 = self.ser.read_hft(hft_x_cmd_re, 1)
                        hft_y = self.ser.read_hft(hft_y_cmd_ab, 0)
                        hft_y_1 = self.ser.read_hft(hft_y_cmd_re, 1)
                        self.update_hft.emit(str(hft_x), str(hft_y), str(hft_x_1), str(hft_y_1))
                        time.sleep(1)
                else:
                    res = self.ser.set_hft_0(self.cmd)
                    if self.cmd == hft_xset0_cmd:
                        axis = 'X'
                    else:
                        axis = 'Y'
                    detail = 'Hft ' + axis + ' set to 0.'
                    if res:
                        self.log_signal.emit('info', detail)
                    self.cmd = None
        else:
            self.log_signal.emit('error', 'Open hft serial failure.')

    @pyqtSlot(str)
    def move(self, button):
        if button.find('X') >= 0:
            self.cmd = hft_xset0_cmd
        else:
            self.cmd = hft_yset0_cmd


class MotorMonitor(QThread):
    update_motor = pyqtSignal(str, str)
    motor_stop = pyqtSignal(str)
    log_signal = pyqtSignal(str, str)

    # motor_error = pyqtSignal()

    def __init__(self, port, band, control_queue):
        super(MotorMonitor, self).__init__()
        self.ser = Communication(port, band)
        # self.control_cmd = None
        self.control_queue = control_queue
        #

    def run(self):
        print("Motor Control and Monitor thread started...")
        self.ser.open_serial()
        if self.ser.check_status():
            while True:
                # if self.control_cmd is None:
                if self.control_queue.empty():
                    cmd = "#?X#"
                    x = self.ser.send_cmd(cmd)
                    self.motor_resp_decode(x, cmd)
                    cmd = '#?Y#'
                    y = self.ser.send_cmd(cmd)
                    self.motor_resp_decode(y, cmd)
                else:
                    cmd = self.control_queue.get()
                    x = self.ser.send_cmd(cmd)
                    # set hft = 0
                    if cmd.find('HX') >= 0:
                        global X0
                        X0 = 0
                        if self.check_stop(cmd):
                            self.motor_stop.emit(cmd)
                    elif cmd.find('HY') >= 0:
                        global Y0
                        Y0 = 0
                        if self.check_stop(cmd):
                            self.motor_stop.emit(cmd)
                    # else:
                    #     self.motor_resp_decode(x, cmd)
        else:
            self.log_signal.emit('error', 'Open motor serial failure.')

    def check_stop(self, cmd):
        if cmd.find('X') >= 0:
            cmd = '#?X#'
            axis = 'X'
        else:
            cmd = '#?Y#'
            axis = 'Y'
        res = self.ser.send_cmd(cmd)
        pos = self.motor_resp_decode(res, cmd)
        if pos:
            num = 0
            while True:
                res = self.ser.send_cmd(cmd)
                pos_new = self.motor_resp_decode(res, cmd)
                if pos_new:
                    print(" In waiting stop, res = %s , new = %s, num = %d " % (pos, pos_new, num))
                    if pos_new == pos or num > 5:
                        detail = 'Motor ' + axis + ' stopped.'
                        self.log_signal.emit('info', detail)
                        return True
                    else:
                        pos = pos_new
                        num += 1
                else:
                    return False
        else:
            return False

    def motor_resp_decode(self, res, cmd):
        global motor_com_error
        try:
            index = res.rfind(':')
        except Exception as e:
            if not res and not motor_com_error:
                self.log_signal.emit('error', 'Motor communication failure, please check motor controller.')
                motor_com_error = True
                time.sleep(2)
            elif not res:
                time.sleep(2)
            else:
                detail = 'Motor return ' + res + e
                self.log_signal.emit('warning', detail)
        else:
            res = res[index + 1:]
            self.update_motor.emit(res, cmd)
            if motor_com_error:
                self.log_signal.emit('info', 'Motor communication return to normal.')
                motor_com_error = False
            time.sleep(1)
        return res


# class MotorControl(QThread):
#     def __init__(self, port, band, sig):
#         super(MotorControl, self).__init__()
#         self.ser = Communication(port, band)
#         self.cmd = None
#         self.sig = sig
#         self.sig.connect(self.move)
#
#     def run(self):
#         if self.cmd is not None:
#             while True:
#                 try:
#                     self.ser.open_serial()
#                 except Exception as e:
#                     print("Error:", e)
#                     time.sleep(1)
#                 else:
#                     self.ser.send_cmd(self.cmd)
#                     self.ser.close_serial()
#                     self.cmd = None
#                     break
#                 print("In Motor Control thread ", time.time())
#
#     @pyqtSlot(str)
#     def move(self, cmd):
#         self.cmd = cmd
#         print("In Motor Monitor class, move2() is called, cmd is ", self.cmd)


app = QApplication(sys.argv)
my_windows = MainGUI()
my_windows.show()
# my_windows.motor_move()
sys.exit(app.exec_())
