import serial
import binascii
import time
import ctypes

X_ab_pos = '01 03 00 02 00 02 65 CB'
Y_ab_pos = '02 03 00 02 00 02 65 F8'


class Communication:

    def __init__(self, port, bandrate):
        self.ser = None
        self.port = port
        self.bandrate = int(bandrate)
        self.status = False

    def open_serial(self):
        try:
            self.ser = serial.Serial(self.port, self.bandrate)
        except Exception as e:
            print("Error:", e)
        else:
            if self.ser.isOpen():
                self.status = True

    def close_serial(self):
        if self.status:
            self.ser.close()
            self.status = False

    def check_status(self):
        # print("Serial status is", self.status)
        return self.status

    def read_hft_ab_pos(self, cmd_str):
        cmd = bytes.fromhex(cmd_str)
        self.ser.write(cmd)
        time.sleep(1)
        count = self.ser.inWaiting()
        data = None
        if count == 0:
            print('No response...')
            return data
        if count > 0:
            data = self.ser.read(count)
            if data != b'':
                # get 32 bit hex
                ba = binascii.b2a_hex(data)[6:14]
                # hex data to unsigned int 32
                ba_int = int(ba, 16)
                # convert unsigned int to int
                a = ctypes.c_int32(ba_int).value
                # print(a)
                self.ser.flushInput()
                return a
            else:
                self.ser.flushInput()
                return data

    def read_hft(self, cmd_str, flag):
        # flag=0 is 32bit decode, flag=1 is 16bit decode.
        self.ser.flushInput()
        self.ser.flushOutput()

        cmd = bytes.fromhex(cmd_str)
        self.ser.write(cmd)
        count = self.ser.inWaiting()
        num = 0
        while num < 5:
            count = self.ser.inWaiting()
            if count > 0:
                break
            else:
                time.sleep(0.5)
                num += 1
        res = None
        if count > 0:
            data = self.ser.read(count)
            if data != b'':
                if flag == 0:
                    # get 32 bit hex
                    ba = binascii.b2a_hex(data)[6:14]
                    # hex data to unsigned int 32
                    ba_int = int(ba, 16)
                    # convert unsigned int to int
                    res = ctypes.c_int32(ba_int).value
                    # print(a)
                else:
                    ba = binascii.b2a_hex(data)[6:10]
                    # hex data to unsigned int 32
                    ba_int = int(ba, 16)
                    # convert unsigned int to int
                    res = ctypes.c_int16(ba_int).value
        return res

    def read_hft_re_pos(self, cmd_str):
        cmd = bytes.fromhex(cmd_str)
        self.ser.write(cmd)
        time.sleep(1)
        count = self.ser.inWaiting()
        data = None
        if count == 0:
            print('No response...')
            return data
        if count > 0:
            data = self.ser.read(count)
            if data != b'':
                # print("hft_re_pos is", data)
                # get 32 bit hex
                ba = binascii.b2a_hex(data)[6:10]
                # hex data to unsigned int 32
                ba_int = int(ba, 16)
                # convert unsigned int to int
                a = ctypes.c_int16(ba_int).value
                # print(a)
                self.ser.flushInput()
                return a
            else:
                self.ser.flushInput()
                return data

    def set_hft_0(self, cmd_str):
        self.ser.flushInput()
        self.ser.flushOutput()
        cmd = bytes.fromhex(cmd_str)
        # print("Send set cmd is ", cmd)
        self.ser.write(cmd)
        time.sleep(1)
        count = self.ser.inWaiting()
        if count == 0:
            print('No response...')
        if count > 0:
            data = self.ser.read(count)
            if data == cmd:
                print("Set hft 0 success!")
                return True
        return False

    def send_cmd(self, cmd_str):
        self.ser.flushInput()
        self.ser.flushOutput()

        cmd = cmd_str + '\r\n'
        self.ser.write(cmd.encode())
        # print("Send cmd '{}' ".format(str(cmd_str)))
        num = 0
        while num < 10:
            count = self.ser.inWaiting()
            if count > 0:
                break
            else:
                time.sleep(0.5)
                num += 1
        data = None
        if count > 0:
            data = self.ser.read(count)
            if data != b'':
                data = data.decode().replace('\r\n', '')
        # print("Send cmd return", data)
        return data

    def read_pos(self, cmd_str):
        # print("In read pos function!")
        self.ser.flushInput()
        cmd = cmd_str + '\r\n'
        self.ser.write(cmd.encode())
        # time.sleep(2)
        num = 0
        while num < 10:
            count = self.ser.inWaiting()
            if count > 0:
                break
            else:
                time.sleep(1)
                num += 1
        data = None
        if count == 0:
            print('Try %s times but still no response...' % str(num))
        else:
            data = self.ser.read(count)
            if data != b'':
                data = data.decode().replace('\r\n', '')
            else:
                data = None
        # print("read pos function return ", data)
        return data



# eng = Communication("COM4", 9600)
# eng.open_serial()
# print("Serial %s-%s is opened and status is %s" % (eng.port, eng.bandrate, eng.check_status()))
#
# eng.get_hft_ab_pos(X_ab_pos)
# eng.get_hft_ab_pos(Y_ab_pos)
#
# eng.close_serial()
# print("Serial %s-%s is closed and status is %s" % (eng.port, eng.bandrate, eng.check_status()))
