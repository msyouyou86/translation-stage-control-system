import time
import sys
from serial_comm import Communication


# hft_ser = Communication("COM4", 9600)
# controller_ser = Communication("COM1", 57600)
# print("hft serial status is", hft_ser.status)

# hft_xset0_cmd = '01 06 00 10 00 00 88 0F'
# hft_yset0_cmd = '02 06 00 10 00 00 88 3C'
# controller_xpos = '#?X#'
# controller_ypos = '#?Y#'
# controller_set_x = '#+X 40#'


def test():
    ser = Communication("COM1", 57600)
    ser.open_serial()
    if ser.check_status():
        res = ser.send_cmd("#XF")
        print(" X speed = ", res)
        ser.close_serial()
    # hft_ser.set_hft_0(hft_xset0_cmd)
    # hft_ser.set_hft_0(hft_yset0_cmd)
    # count = 0
    # while hft_ser.status and count < 10:
    #     x = hft_ser.read_hft_ab_pos(hft_ab_xpos_cmd)
    #     y = hft_ser.read_hft_ab_pos(hft_ab_ypos_cmd)
    #     print("Xpos=%d Ypos=%d" % (x, y))
    #     time.sleep(1)
    #     count += 1


def hft_read(hft_port, hft_bandrate, axis):
    hft_ab = hft_position(hft_port, hft_bandrate, axis, 0)
    hft_re = hft_position(hft_port, hft_bandrate, axis, 1)
    print("HFT_AB = %d, HFT_RE = %d" % (hft_ab, hft_re))


def hft_ab_position(axis):
    hft_ab_xpos_cmd = '01 03 00 02 00 02 65 CB'
    hft_ab_ypos_cmd = '02 03 00 02 00 02 65 F8'
    ser = Communication('COM4', 9600)
    ser.open_serial()
    data = None
    if ser.check_status():
        if axis.find('X') >= 0:
            data = ser.read_hft_ab_pos(hft_ab_xpos_cmd)
        elif axis.find('Y') >= 0:
            data = ser.read_hft_ab_pos(hft_ab_ypos_cmd)
        ser.close_serial()
    else:
        print("Please check connection!")
    return data


def hft_position(port, bandrate, axis, flag):
    if flag == 0:
        hft_x_cmd = '01 03 00 02 00 02 65 CB'
        hft_y_cmd = '02 03 00 02 00 02 65 F8'
        # print("Read absolutely hft position...")
    else:
        hft_x_cmd = '01 03 00 01 00 01 0D 0A'
        hft_y_cmd = '02 03 00 01 00 01 0D 0A'
        # print("Read relative hft position...")
    ser = Communication(port, bandrate)
    ser.open_serial()

    data2 = None
    if ser.check_status():
        if axis.find('X') >= 0:
            cmd = hft_x_cmd
        elif axis.find('Y') >= 0:
            cmd = hft_y_cmd
        data = ser.read_hft(cmd, flag)
        # now add while check data change
        num = 0
        while True:
            data2 = ser.read_hft(cmd, flag)
            # print("data = %d, data2 = %d" % (data, data2))
            if -5 <= data2 - data <= 5 or num > 9:
                break
            else:
                data = data2
                time.sleep(0.5)
                num += 1
        ser.close_serial()
    else:
        print("Please check connection!")
    # print("num=", num)
    return data2


def hft_re_position(axis):
    hft_re_xpos_cmd = '01 03 00 01 00 01 0D 0A'
    hft_re_ypos_cmd = '02 03 00 01 00 01 0D 0A'
    ser = Communication('COM4', 9600)
    ser.open_serial()
    if ser.check_status():
        if axis.find('X') >= 0:
            value = ser.read_hft_re_pos(hft_re_xpos_cmd)
        elif axis.find('Y') >= 0:
            value = ser.read_hft_re_pos(hft_re_ypos_cmd)
        else:
            value = None
        ser.close_serial()
        # print("HFT_RE = ", value)
        return value
    else:
        print("Please check connection!")
        return None


def hft_0(axis):
    hft_xset0_cmd = '01 06 00 10 00 00 88 0F'
    hft_yset0_cmd = '02 06 00 10 00 00 88 3C'
    ser = Communication('COM4', 9600)
    ser.open_serial()
    if ser.check_status():
        if axis.find('X') >= 0:
            ser.set_hft_0(hft_xset0_cmd)
        elif axis.find('Y') >= 0:
            ser.set_hft_0(hft_yset0_cmd)
        ser.close_serial()
    else:
        print("Please check connection!")


def cmd_exec(cmd, port, bandrate):
    ser = Communication(port, bandrate)
    ser.open_serial()
    res = None
    if ser.check_status():
        res = ser.send_cmd(cmd)
        ser.close_serial()
    else:
        print("Please check connection!")
    return res


def read_exec(cmd, port, bandrate):
    ser = Communication(port, bandrate)
    ser.open_serial()
    if ser.check_status():
        response = ser.read_pos(cmd)
        ser.close_serial()
        return response
    else:
        print("Please check connection!")
        return None


def decode_res(res):
    index = res.rfind(':')
    res = res[index+1:]
    return int(res)


def argv_help():
    print("Parameter detail as follows...")
    print("+X/+Y pulses   Send go forward pulses cmd to motor controller.")
    print("               For example: +X 100, response is X current position =  X original position + 100")
    print("-X/-Y pulses   Send go backward pulses cmd to motor controller.")
    print("               For example: -X 100, response is X current position =  X original position - 100")
    print("X/Y  pulses    Send go forward to pulses cmd to motor controller.")
    print("               For example:  Y 100, response is Y current position = 100")
    print("?X/?Y          Send query cmd to motor controller to get X or Y position.")
    print("               For example:  ?Y, response is Y current position")
    print("X0/Y0          Send return to zero cmd to motor controller")
    print("               For example:  X, response is X>:0")
    print("!S             Send stop command to motor controller to stop all motors.")
    print("?HX/?HY        Send query HFT position command to HFT.")
    print("+HX/+HY        Send go forward HFT position command to HFT.")
    print("               For example: +HX 100, response is HFT current position =  HFT original position + 100")
    print("-HX/-HY        Send back forward HFT position command to HFT.")
    print("               For example: -HX 100, response is HFT current position =  HFT original position - 100")
    print("HX/HY          Send go forward to HFT position command to HFT.")
    print("               For example: HX 100, response is HFT current position =  100")


def motor_0(port, bandrate, hft_port, hft_bandrate, axis):
    if axis.find('X') >= 0:
        axis = 'X'
    else:
        axis = 'Y'
    # move out a short drift
    axis1 = '+' + axis
    motor_move(port, bandrate, hft_port, hft_bandrate,  axis1, '2000')

    # pos = motor_position(port, bandrate, axis)
    # print("Current %s pos is %d" % (axis, pos))

    # send check 0 to motor
    cmd = "#H" + axis + '#'
    # print("Send return to zero cmd '{}' ".format(str(cmd)))
    cmd_exec(cmd, port, bandrate)

    # check motor move or not
    # last_pos = 0
    # while True:
    #     current_pos = hft_ab_position(axis)
    #     if -5 < current_pos - last_pos < 5:
    #         break
    #     else:
    #         last_pos = current_pos
    #         time.sleep(0.5)
    hft = hft_position(hft_port, hft_bandrate, axis, 0)
    print("HFT_AB=", hft)
    motor_stop(port, bandrate)
    print("Axis %s can not move any more! Controller is stopped now!" % axis)
    pos = motor_position(port, bandrate, axis)
    print("Current %s pos is %d" % (axis, pos))
    hft = hft_position(hft_port, hft_bandrate, axis, 1)
    # set hft = 0
    pulse = (4096 - hft)*1600//4096
    print("pulse=", pulse)
    motor_move(port, bandrate, hft_port, hft_bandrate, axis1, str(pulse))
    motor_position(port, bandrate, axis)
    hft_read(hft_port, hft_bandrate, axis)
    # hft_re = hft_re_position(axis)
    # hft_ab = hft_ab_position(axis)
    # print("HFT_RE = %d, HFT_AB = %d" % (hft_re, hft_ab))
    hft_0(axis)
    # hft_ab = hft_position(hft_port, hft_bandrate, axis, 0)
    # print("HFT_AB = ", hft_ab)
    hft_read(hft_port, hft_bandrate, axis)


def motor_move(port, bandrate, hft_port, hft_bandrate, axis, pulse):
    if axis == '+X' or axis == '+Y' or axis == '-X' or axis == '-Y':
        cmd = '#' + axis + ' ' + pulse + '#'
        # print("Send add pulses cmd '{}' ".format(str(cmd)))
        cmd_exec(cmd, port, bandrate)
        # keep safe
        hft_position(hft_port, hft_bandrate, axis, 0)
        motor_stop(port, bandrate)
    elif axis == 'X' or axis == 'Y':
        # cmd0 = '#?' + axis + '#'
        # res = cmd_exec(cmd0, port, bandrate)
        res = motor_position(port, bandrate, axis)
        if res is not None:
            if int(pulse) >= res:
                add_pos = int(pulse) - res
                cmd = '#+' + axis + ' ' + str(add_pos) + '#'
            elif int(pulse) < res:
                add_pos = res - int(pulse)
                cmd = '#-' + axis + ' ' + str(add_pos) + '#'
            # print("Send add pulses cmd '{}' ".format(str(cmd)))
            cmd_exec(cmd, port, bandrate)
            # keep safe
            hft_position(hft_port, hft_bandrate, axis, 0)
            motor_stop(port, bandrate)
        else:
            print("No response, please check connection!")


def motor_position(port, bandrate, axis):
    if axis.find('X') >= 0:
        cmd = '#?X#'
    else:
        cmd = '#?Y#'
    new_res = None
    # print("Send query cmd '{}' ".format(str(cmd)))
    res = cmd_exec(cmd, port, bandrate)
    # print("Response is '{}' ".format(str(res)))
    if res is not None:
        res = decode_res(res)
        num = 0
        while True:
            new_res = cmd_exec(cmd, port, bandrate)
            if new_res is not None:
                new_res = decode_res(new_res)
                # print("res = %d, new_res = %d" % (res, new_res))
                if -10 < new_res - res < 10 or num > 9:
                    break
                else:
                    res = new_res
                    time.sleep(0.5)
                    num += 1
    return new_res

    # if res is not None:
    #     return int(res[3:])
    # else:
    #     return None


def motor_stop(port, bandrate):
    cmd = '$sss'
    cmd_exec(cmd, port, bandrate)


def argv_test():
    controller_port = '/dev/ttyUSB2'
    controller_bandrate = 57600
    hft_port = '/dev/ttyUSB1'
    hft_bandrate = 9600
    para_counts = len(sys.argv)
    if para_counts < 2:
        argv_help()
    elif para_counts == 2:
        axis = sys.argv[1]
        if axis == '?X' or axis == '?Y':
            res = motor_position(controller_port, controller_bandrate, axis)
            print("%s = %s" % (axis[1], str(res)))
            hft_ab = hft_position(hft_port, hft_bandrate, axis, 0)
            # hft_re = hft_position(hft_port, hft_bandrate, axis, 1)
            print("HFT_AB = ", hft_ab)
        elif axis == 'X0' or axis == 'Y0':
            motor_0(controller_port, controller_bandrate, hft_port, hft_bandrate, axis)
        elif axis == '!S':
            motor_stop(controller_port, controller_bandrate)
        elif axis == '?HX' or axis == '?HY':
            hft_read(hft_port, hft_bandrate, axis)
        else:
            argv_help()
    else:
        axis = sys.argv[1]
        pulse = sys.argv[2]
        if axis.find('+H') >= 0 or axis.find('-H') >= 0:
            # HFT operation:
            axis = axis.replace('H', '')
            pulse = str(int(pulse)*1600//4096)
        elif axis.find('H') >= 0:
            print("Here!")
            pos = hft_position(hft_port, hft_bandrate, axis, 0)
            print("Old HFT_AB = ", pos)
            if pos is not None:
                sub = int(pulse) - pos
                if sub >= 0:
                    axis = axis.replace('H', '+')
                else:
                    axis = axis.replace('H', '-')
                    sub = abs(sub)
                pulse = str(sub*1600//4096)
        print("axis = %s, Pulse = %s" % (axis, pulse))
        motor_move(controller_port, controller_bandrate, hft_port, hft_bandrate, axis, pulse)
        pos = motor_position(controller_port, controller_bandrate, axis)
        print("Position = ", pos)
        hft_read(hft_port, hft_bandrate, axis)


argv_test()
# test()



