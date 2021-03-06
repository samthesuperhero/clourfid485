"""
Python 2.7.12 (default, Dec  4 2017, 14:50:18)
[GCC 5.4.0 20160609] on linux2
"""

from crcmod import mkCrcFun
from time import strftime, gmtime, sleep, clock, time
from json import load, loads, dumps, dump
from collections import deque
import serial

global_logging_level = 0
global_log_list = list()

"""
--- Frame ---
|0xAA|control word|Serial device address|Data length|Data|Calibration code|
|0xAA|2byte|1byte|2byte(U16)|Nbyte|2byte|
"""

RS485_USED = 1      # for RS485
RS485_NOT_USED = 0  # if other interface used
INIT_BY_READER = 1  # initiated by reader
INIT_BY_USER = 0    # initiated by user PC or other device
TYPE_ERR_WARN = 0           # 0, Reader error or warning message
TYPE_CONF_MANAGE = 1        # 1, Reader configuration and management message
TYPE_CONF_OPERATE = 2       # 2, RFID Configuration and operation message
TYPE_LOG = 3                # 3, Reader log message
TYPE_APP_UPGRADE = 4        # 4, Reader app processor software / baseband software upgrade message
TYPE_TEST = 5               # 5, Testing command

# Error types
ERR_NUMBER = 0
ERR_CRC = 1
ERR_WROND_MID = 2
ERR_PROTOCOL_CONTROL_WORD = 3
ERR_CANT_EXECUTE_IN_CURR_STATUS = 4
ERR_COMMAND_LIST_FULL = 5
ERR_MESS_PARAMS_INCOMPLETE = 6
ERR_FRAME_LEN_EXCEED_LIMIT = 7 # data len <= 1024 bytes
ERR_OTHER = 8

# Reader statuses
STATUS_IDLE = 0
STATUS_EXECUTION = 1
STATUS_ERROR = 2

# MIDs for TYPE_ERR_WARN
ERR_MID = 0x00 # reader initiated

# MIDs for TYPE_CONF_MANAGE
MAN_QUERY_INFO = 0x00
MAN_QUERY_BASEBAND = 0x01
MAN_CONF_RS232 = 0x02
MAN_QUERY_RS232_CONF = 0x03
MAN_IP_CONF = 0x04
MAN_QUERY_IP = 0x05
MAN_QUERY_MAC = 0x06
MAN_CONF_CLI_SRV_MODE = 0x07
MAN_QUERY_CLI_SRV_MODE = 0x08
MAN_CONF_GPO = 0x09
MAN_QUERY_GPI_STATUS = 0x0A
MAN_CONF_GPI_TRIG = 0x0B
MAN_QUERY_GPI_TRIG = 0x0C
MAN_CONF_WIEGAND = 0x0D
MAN_QUERY_WIEGAND = 0x0E
MAN_RESTART = 0x0F
MAN_CONF_TIME = 0x10
MAN_QUERY_TIME = 0x11
MAN_CONN_CONFIRM = 0x12
MAN_CONF_MAC = 0x13
MAN_RESTORE_DEFAULT = 0x14
MAN_CONF_RS485_ADR = 0x15
MAN_QUERY_RS485_ADR = 0x16
MAN_TAG_DATA_RESPONSE = 0x1D
MAN_BUZZ_CONTROL = 0x1F

# Reply or initiated by reader
MAN_READER_TRIG_START_MESS = 0x00 # reader initiated
MAN_READER_TRIG_STOP_MESS = 0x01 # reader initiated
MAN_READER_CONN_CONFIRM = 0x12 # reader initiated

# MIDs for TYPE_CONF_OPERATE
OP_QUERY_RFID_ABILITY = 0x00
OP_CONF_POWER = 0x01
OP_QUERY_POWER = 0x02
OP_CONF_RF_BAND = 0x03
OP_QUERY_RF_BAND = 0x04
OP_CONF_FREQ = 0x05
OP_QUERY_FREQ = 0x06
OP_CONF_ANT = 0x07
OP_QUERY_ANT = 0x08
OP_CONF_TAG_UPLOAD = 0x09
OP_QUERY_TAG_UPLOAD = 0x0A
OP_CONF_EPC_BASEBAND = 0x0B
OP_QUERY_EPC_BASEBAND = 0x0C
OP_CONF_AUTO_IDLE = 0x0D
OP_QUERY_AUTO_IDLE = 0xE
OP_READ_EPC_TAG = 0x10
OP_WRITE_EPC_TAG = 0x11
OP_LOCK_TAG = 0x12
OP_KILL_TAG = 0x13
OP_READ_6B_TAG = 0x40
OP_QRITE_6B_TAG = 0x41
OP_LOCK_6B_TAG = 0x42
OP_QUERY_6B_TAG_LOCKING = 0x43
OP_STOP = 0xFF

# Reply or initiated by reader
OP_READER_EPC_DATA_UPLOAD = 0x00 # reader initiated
OP_READER_EPC_READ_FINISH = 0x01 # reader initiated
OP_READER_6B_DATA_UPLOAD = 0x02 # reader initiated
OP_READER_6B_READ_QUIT = 0x03 # reader initiated

DECODE_ERROR_TYPE = {
    0: "0 error type",
    1: "CRC calibration error",
    2: 'wrong MID',
    3: 'protocol control word other error',
    4: 'current status can not execute the command',
    5: 'command list full',
    6: 'message parameter incomplete',
    7: 'frame length exceed limitation',
    8: 'other error'
    }

DECODE_READER_STATUS = {
    0: 'Idle status',
    1: 'Execution status',
    2: 'Error status'
    }

FRAME_DIRECTION = ('SEND', 'RECEIVE')

PARAM_HEADER_INIT = {
    'INIT_BY_READER': INIT_BY_READER,
    'INIT_BY_USER': INIT_BY_USER,
    'NULL': 0x00
    }
DECODE_PARAM_HEADER_INIT = dict()
for keys_tmp in PARAM_HEADER_INIT.keys():
    if keys_tmp != 'NULL':
        DECODE_PARAM_HEADER_INIT[(PARAM_HEADER_INIT[keys_tmp])] = keys_tmp
del(keys_tmp)

PARAM_HEADER_RS485 = {
    'RS485_USED': RS485_USED,
    'RS485_NOT_USED': RS485_NOT_USED,
    'NULL': 0x00
    }
DECODE_PARAM_HEADER_RS485 = dict()
for keys_tmp in PARAM_HEADER_RS485.keys():
    if keys_tmp != 'NULL':
        DECODE_PARAM_HEADER_RS485[(PARAM_HEADER_RS485[keys_tmp])] = keys_tmp
del(keys_tmp)

PARAM_HEADER_TYPE = {
    'TYPE_ERR_WARN': TYPE_ERR_WARN,
    'TYPE_CONF_MANAGE': TYPE_CONF_MANAGE,
    'TYPE_CONF_OPERATE': TYPE_CONF_OPERATE,
    'TYPE_LOG': TYPE_LOG,
    'TYPE_APP_UPGRADE': TYPE_APP_UPGRADE,
    'TYPE_TEST': TYPE_TEST,
    'NULL': 0x00
    }
DECODE_PARAM_HEADER_TYPE = dict()
for keys_tmp in PARAM_HEADER_TYPE.keys():
    if keys_tmp != 'NULL':
        DECODE_PARAM_HEADER_TYPE[(PARAM_HEADER_TYPE[keys_tmp])] = keys_tmp
del(keys_tmp)

MID_ERR = {
    'ERR_MID': 0x00,
    'NULL': 0x00
    }
DECODE_MID_ERR = {0x00: 'ERR_MID'}

MID_MAN_USER_INIT = {
    'MAN_QUERY_INFO': 0x00,
    'MAN_QUERY_BASEBAND': 0x01,
    'MAN_CONF_RS232': 0x02,
    'MAN_QUERY_RS232_CONF': 0x03,
    'MAN_IP_CONF': 0x04,
    'MAN_QUERY_IP': 0x05,
    'MAN_QUERY_MAC': 0x06,
    'MAN_CONF_CLI_SRV_MODE': 0x07,
    'MAN_QUERY_CLI_SRV_MODE': 0x08,
    'MAN_CONF_GPO': 0x09,
    'MAN_QUERY_GPI_STATUS': 0x0A,
    'MAN_CONF_GPI_TRIG': 0x0B,
    'MAN_QUERY_GPI_TRIG': 0x0C,
    'MAN_CONF_WIEGAND': 0x0D,
    'MAN_QUERY_WIEGAND': 0x0E,
    'MAN_RESTART': 0x0F,
    'MAN_CONF_TIME': 0x10,
    'MAN_QUERY_TIME': 0x11,
    'MAN_CONN_CONFIRM': 0x12,
    'MAN_CONF_MAC': 0x13,
    'MAN_RESTORE_DEFAULT': 0x14,
    'MAN_CONF_RS485_ADR': 0x15,
    'MAN_QUERY_RS485_ADR': 0x16,
    'MAN_TAG_DATA_RESPONSE': 0x1D,
    'MAN_BUZZ_CONTROL': 0x1F,
    'NULL': 0x00
    }
DECODE_MID_MAN_USER_INIT = dict()
for keys_tmp in MID_MAN_USER_INIT.keys():
    if keys_tmp != 'NULL':
        DECODE_MID_MAN_USER_INIT[(MID_MAN_USER_INIT[keys_tmp])] = keys_tmp
del(keys_tmp)

MID_MAN_READER_INIT = {
    'MAN_READER_TRIG_START_MESS': 0x00,
    'MAN_READER_TRIG_STOP_MESS': 0x01,
    'MAN_READER_CONN_CONFIRM': 0x12,
    'NULL': 0x00
    }
DECODE_MID_MAN_READER_INIT = dict()
for keys_tmp in MID_MAN_READER_INIT.keys():
    if keys_tmp != 'NULL':
        DECODE_MID_MAN_READER_INIT[(MID_MAN_READER_INIT[keys_tmp])] = keys_tmp
del(keys_tmp)

MID_OP_USER_INIT = {
    'OP_QUERY_RFID_ABILITY': 0x00,
    'OP_CONF_POWER': 0x01,
    'OP_QUERY_POWER': 0x02,
    'OP_CONF_RF_BAND': 0x03,
    'OP_QUERY_RF_BAND': 0x04,
    'OP_CONF_FREQ': 0x05,
    'OP_QUERY_FREQ': 0x06,
    'OP_CONF_ANT': 0x07,
    'OP_QUERY_ANT': 0x08,
    'OP_CONF_TAG_UPLOAD': 0x09,
    'OP_QUERY_TAG_UPLOAD': 0x0A,
    'OP_CONF_EPC_BASEBAND': 0x0B,
    'OP_QUERY_EPC_BASEBAND': 0x0C,
    'OP_CONF_AUTO_IDLE': 0x0D,
    'OP_QUERY_AUTO_IDLE': 0xE,
    'OP_READ_EPC_TAG': 0x10,
    'OP_WRITE_EPC_TAG': 0x11,
    'OP_LOCK_TAG': 0x12,
    'OP_KILL_TAG': 0x13,
    'OP_READ_6B_TAG': 0x40,
    'OP_QRITE_6B_TAG': 0x41,
    'OP_LOCK_6B_TAG': 0x42,
    'OP_QUERY_6B_TAG_LOCKING': 0x43,
    'OP_STOP': 0xFF,
    'NULL': 0x00
    }
DECODE_MID_OP_USER_INIT = dict()
for keys_tmp in MID_OP_USER_INIT.keys():
    if keys_tmp != 'NULL':
        DECODE_MID_OP_USER_INIT[(MID_OP_USER_INIT[keys_tmp])] = keys_tmp
del(keys_tmp)

MID_OP_READER_INIT = {
    'OP_READER_EPC_DATA_UPLOAD': 0x00,
    'OP_READER_EPC_READ_FINISH': 0x01,
    'OP_READER_6B_DATA_UPLOAD': 0x02,
    'OP_READER_6B_READ_QUIT': 0x03,
    'NULL': 0x00
    }
DECODE_MID_OP_READER_INIT = dict()
for keys_tmp in MID_OP_READER_INIT.keys():
    if keys_tmp != 'NULL':
        DECODE_MID_OP_READER_INIT[(MID_OP_READER_INIT[keys_tmp])] = keys_tmp
del(keys_tmp)

MID = [[{'NULL': 0x00}, MID_ERR], [MID_MAN_USER_INIT, MID_MAN_READER_INIT], [MID_OP_USER_INIT, MID_OP_READER_INIT]]
DECODE_MID = [[{0x00: 'NULL'}, DECODE_MID_ERR], [DECODE_MID_MAN_USER_INIT, DECODE_MID_MAN_READER_INIT], [DECODE_MID_OP_USER_INIT, DECODE_MID_OP_READER_INIT]]

DECODE_FRAME_ERRORS = {
    0: 'OK',
    1: 'No 0xAA frame header symbol',
    2: 'CRC error',
    3: 'Frame len < 7 bytes',
    4: 'Message type > 5',
    5: 'Reserved bits in control word are not 0',
    6: 'Wrong MID number for control word',
    7: 'RS485 not supported',
    8: 'Frame data len parameter not match frame data len'
    }

DECODE_TAG_DATA = {
    0x01: 'RSSI', # RSSI
    0x02: 'DATA_READ_RESULT', # tag data read result
    0x03: 'TID', # Tag TID data
    0x04: 'USER_AREA', # Tag user area data
    0x05: 'RETENTION_AREA', # tag retention area data
    0x06: 'SUB_ANT', # Sub antenna number, 1-16
    0x07: 'TIME', # Tag reading time UTC
    0x08: 'SERIES_NUM', # Tag response package series number
    0x09: 'FREQ', # Current frequency
    0x0A: 'PHASE', # Current tag phase
    0x0B: 'EM_SENSOR_DATA', # EM SensorData
    0x0C: 'ADDITIONAL_DATA'  # Tag EPC data
    }
TAG_DATA = dict()
for keys_tmp in DECODE_TAG_DATA.keys():
    TAG_DATA[(DECODE_TAG_DATA[keys_tmp])] = keys_tmp
del(keys_tmp)

DECODE_AREA_DATA_PARAMETER = {
    0: "Read successful",
    1: "Tag no response",
    2: "CRC error",
    3: "Data area is locked",
    4: "Data area overflow",
    5: "Access password error",
    6: "Other tag error",
    7: "Other reader error"
}


FREQ_BANDS = {
    0: '920~925MHz',
    1: '840~845MHz',
    2: '840~845MHz & 920~925MHz',
    3: 'FCC: 902~928MHz',
    4: 'ETSI: 866~868MHz',
    5: 'JP: 916.8~920.4MHz',
    6: 'TW: 922.25~927.75MHz',
    7: 'ID: 923.125~925.125MHz',
    8: 'RU: 866.6~867.4MHz'
    }

RFID_PROTOCOLS = {
    0: 'ISO18000-6C/EPC C1G2',
    1: 'ISO18000-6B',
    2: 'China standard GB/T 29768-2013',
    3: 'China Military GJB 7383.1-2011'
    }

DECODE_READ_EPC_TAG = {
    0: 'Configure successfully',
    1: 'Antenna port parameter error',
    2: 'Select read parameter error',
    3: 'TID read parameter error',
    4: 'User data area read parameter error',
    5: 'Retention area read parameter error',
    6: 'Other parameter error'
    }

FREQ_AUTO_SETTING = {
    0: 'MANUAL',
    1: 'AUTO'
    }

# Get error discriptions for codes
ERR_NAME_DICT = {
    -11: "conn_open: port name is not str() type",
    -12: "conn_open: port name is empty",
    -13: "conn_open: serial.Serial() exception",
    -24: "conn_close: serial.close() exception",
    -31: "send_stop: response frame from reader decoded with error",
    -32: "send_stop: not received OK from reader",
    -33: "send_stop: reader answered with error",
    -36: "send_stop: serial port descriptor connection_context.device_fd empty",
    -42: "set_read_timeout: timeout_set must be int or float",
    -43: "conn_close: serial.timeout set exception",
    -51: "logging_level_set: global_logging_level_set must be int",
    -52: "logging_level_set: global_logging_level_set availabel values: 0, 1, 2",
    -61: "send_scan_once: serial port descriptor connection_context.device_fd empty",
    -62: "send_scan_once: reader not answered during timeout",
    -64: "send_scan_once: not received OK from reader",
    -65: "send_scan_once: reader answered with error",
    -1001: "send: serial.write() exception",
    -1002: "send: bytes sent not equal bytes requested to send",
    -2002: "read_general: serial.read() exception",
    }

class TagData:              # data structure for RFID tag
    def __init__(self):
        self.EPC_code = bytearray()
        self.PC_value = 0
        self.ant_id = 0
        self.params = dict()    # dictionary for decoding optional parameters DECODE_TAG_DATA[]
        self.decode_error = False
        self.EPC_len = 0
        self.UMI = 0
        self.XPC_indicator = 0
        self.num_sys_id_toggle = 0
        self.RFU = 0
    def encodeInDict(self):
        res_dict = dict()
        res_i = 0
        res_dict["EPC_code"] = str()
        for res_i in range(len(self.EPC_code)):
            res_dict["EPC_code"] += "{0:02X}".format(self.EPC_code[res_i])
        res_dict["ant_id"] = self.ant_id
        res_dict["params"] = dict()
        for tmp_dict_keys in self.params.keys():
            if tmp_dict_keys == 0x02:
                res_dict["params"][tmp_dict_keys] = DECODE_AREA_DATA_PARAMETER[self.params[tmp_dict_keys]]
            elif tmp_dict_keys == 0x03:
                res_i = 0
                res_dict["params"][tmp_dict_keys] = str()
                for res_i in range(len(self.params[tmp_dict_keys])):
                    res_dict["params"][tmp_dict_keys] += "{0:02X}".format(self.params[tmp_dict_keys][res_i])
            elif tmp_dict_keys == 0x08:
                pass
            else:
                res_dict["params"][tmp_dict_keys] = self.params[tmp_dict_keys]
        res_dict["decode_error"] = self.decode_error
        res_dict["EPC_len"] = self.EPC_len * 16
        res_dict["UMI"] = self.UMI
        res_dict["XPC_indicator"] = self.XPC_indicator
        res_dict["num_sys_id_toggle"] = self.num_sys_id_toggle
        res_dict["RFU"] = "0x" + "{0:02X}".format(self.RFU)
        del res_i, tmp_dict_keys
        return res_dict

class ClouRFIDFrame:        # Clou RFID reader frame description
    frame_head = 0xAA # frame head, constant
    def __init__(self, message_id_set="NULL", message_type_set=0, init_by_reader_set=0, rs485_mark_set=0, rs485_id_set=0, data_bytes_transmit=bytearray()):
        self.message_id = message_id_set # MID number = 7-0 message ID 0x00~0xFF (MID) differentiate detailed message below same type message
        self.message_type = message_type_set # 11-8 message type number, 0x5~0xF, reserved
        self.init_by_reader = init_by_reader_set # 12 = 0 means message is PC command or reader response to PC command, 1 means reader initiated
        self.rs485_mark = rs485_mark_set # 13 1 means this message is used for RS485 communication, 0 - otherwise
        self.rs485_id = rs485_id_set # ID of reader on RS-485 bus
        self.data_bytes = data_bytes_transmit # data
        self.frame_raw_line = bytearray()
        self.start_data_with_len = True
    reserved_bits = 0x00 # 15-14 Reserved bit = keep 0
    def encodeFrame(self):
        result_data = bytearray()
        result_data.append(self.frame_head)
        result_data.append(self.message_type + (self.init_by_reader << 4) + (self.rs485_mark << 5))
        result_data.append(MID[self.message_type][self.init_by_reader][self.message_id])
        if self.rs485_mark == RS485_USED:
            result_data.append(self.rs485_id)
        len_msb = len(self.data_bytes) // 256
        len_lsb = len(self.data_bytes) % 256
        if self.start_data_with_len:
            result_data.append(len_msb)
            result_data.append(len_lsb)
        i = 0
        for i in range(len(self.data_bytes)):
            result_data.append(self.data_bytes[i])
        crc16_func = mkCrcFun(0x10000+0x8005, initCrc = 0, rev = False)        
        i = 0
        s_tmp = ""
        for i in range(1, len(result_data)):
            s_tmp = s_tmp + chr(result_data[i])
        crc16_value = crc16_func(s_tmp)
        crc16_msb = crc16_value // 256
        crc16_lsb = crc16_value % 256
        result_data.append(crc16_msb)
        result_data.append(crc16_lsb)
        self.frame_raw_line = result_data
        del(len_msb, len_lsb, i, crc16_func, crc16_value, s_tmp, crc16_msb, crc16_lsb, result_data)
        return 0
    def decodeFrame(self):
        if len(self.frame_raw_line) < 7:
            return 3
        if self.frame_raw_line[0] != 0xAA:
            return 1
        crc16_func = mkCrcFun(0x10000+0x8005, initCrc = 0, rev = False)        
        i = 0
        s_tmp = ""
        for i in range(1, len(self.frame_raw_line)-2):
            s_tmp = s_tmp + chr(self.frame_raw_line[i])
        crc16_value = crc16_func(s_tmp)
        crc16_msb = crc16_value // 256
        crc16_lsb = crc16_value % 256
        if ((crc16_msb != self.frame_raw_line[len(self.frame_raw_line)-2]) or (crc16_lsb != self.frame_raw_line[len(self.frame_raw_line)-1])):
            del(crc16_msb, crc16_lsb, crc16_value, crc16_func, s_tmp, i)
            return 2
        control_symb_tmp = self.frame_raw_line[1]
        message_type_tmp = control_symb_tmp % (2**4)
        if (message_type_tmp > 5):
            del(crc16_msb, crc16_lsb, crc16_value, crc16_func, s_tmp, i, control_symb_tmp, message_type_tmp)
            return 4
        init_by_reader_tmp = (control_symb_tmp // (2**4)) % 2
        rs485_mark_tmp = (control_symb_tmp // (2**5)) % 2
        rs485_added_1 = 0
        if rs485_mark_tmp == RS485_USED:
            self.rs485_id = self.frame_raw_line[3]
            rs485_added_1 = 1
        if ((control_symb_tmp // (2**6)) != 0):
            del(crc16_msb, crc16_lsb, crc16_value, crc16_func, s_tmp, i, control_symb_tmp, message_type_tmp)
            del(init_by_reader_tmp, rs485_mark_tmp, rs485_added_1)
            return 5
        MID_tmp = self.frame_raw_line[2]
        try:
            self.message_id = DECODE_MID[message_type_tmp][init_by_reader_tmp][MID_tmp]
        except Exception:
            del(crc16_msb, crc16_lsb, crc16_value, crc16_func, s_tmp, i, MID_tmp, control_symb_tmp, message_type_tmp)
            del(init_by_reader_tmp, rs485_mark_tmp, rs485_added_1)
            return 6
        i = 0
        self.data_bytes = bytearray()
        for i in range(3 + rs485_added_1, len(self.frame_raw_line)-2):
            self.data_bytes.append(self.frame_raw_line[i])
        if (len(self.data_bytes) - 2) != ((256 * self.data_bytes[0]) + self.data_bytes[1]):
            return 8
        self.message_type = message_type_tmp
        self.init_by_reader = init_by_reader_tmp
        self.rs485_mark = rs485_mark_tmp
        del(crc16_msb, crc16_lsb, crc16_value, crc16_func, s_tmp, i, MID_tmp, control_symb_tmp, message_type_tmp)
        del(init_by_reader_tmp, rs485_mark_tmp, rs485_added_1)
        return 0

class ReaderParameters:     # Parameters of reader
    def __init__(self):
        self.processor = str()
        self.name = str()
        self.baseband_v = str()
        self.mac = bytearray((0x00, 0x00, 0x00, 0x00, 0x00, 0x00))
        self.ip = str()
        self.mask = str()
        self.gw = str()
        self.srv_cli_mode = -1
        self.srv_port = 0
        self.cli_ip = str()
        self.cli_port = str()
        self.on_time = 0
        self.min_power = 0
        self.max_power = 0
        self.antenna_qty = 0
        self.freq_band_list = list()
        self.rfid_protocol_list = list()

def post_log_message(message_text, rfid_frame_object = 0, result_resp = 0, put_timestamp = True):
    global global_log_list
    if global_logging_level > 0:
        s_tmp = str()
        if put_timestamp:
            tmp_time_stamp = time()
            tmp_gmtime_stamp = gmtime(tmp_time_stamp)
            s_tmp = s_tmp + strftime("[ %d.%m.%Y %H:%M:%S." + str(tmp_time_stamp - int(tmp_time_stamp))[2:8] + " UTC ] > ", tmp_gmtime_stamp) + message_text
            del tmp_time_stamp, tmp_gmtime_stamp
        else:
            s_tmp = s_tmp + message_text
        if isinstance(rfid_frame_object, ClouRFIDFrame):
            s_tmp = s_tmp + " [ " + DECODE_FRAME_ERRORS[result_resp] + " ] "
            s_tmp = s_tmp + "[ " + rfid_frame_object.message_id + " ] "
            s_tmp = s_tmp + "[ " + DECODE_PARAM_HEADER_INIT[rfid_frame_object.init_by_reader] + " ] "
            s_tmp = s_tmp + "[ " + DECODE_PARAM_HEADER_RS485[rfid_frame_object.rs485_mark] + " ] "
            if rfid_frame_object.rs485_mark == RS485_USED:
                s_tmp = s_tmp + "[ " + str(rfid_frame_object.rs485_id) + " ] "
            s_tmp = s_tmp + "[ " + DECODE_PARAM_HEADER_TYPE[rfid_frame_object.message_type] + " ] "
            s_tmp = s_tmp + "[ DATA LEN = " + "{0:02X}".format(len(rfid_frame_object.data_bytes)) + " ]"
            s_tmp = s_tmp + " [ "
            j = 0
            for j in range(len(rfid_frame_object.data_bytes)):
                s_tmp = s_tmp + "{0:02X}".format(rfid_frame_object.data_bytes[j]) + " "
            s_tmp = s_tmp + "]"
        global_log_list.append(s_tmp)
        del s_tmp

# to transform bytearray() to string for logging
def byte_to_str(in_bytes):
    out_string = str()
    byte_to_str_i = 0
    for byte_to_str_i in range(len(in_bytes)):
        if type(in_bytes) == bytearray:
            out_string += "{0:02X}".format(in_bytes[byte_to_str_i])
        elif type(in_bytes) == str:
            out_string += "{0:02X}".format(ord(in_bytes[byte_to_str_i]))
        if byte_to_str_i != (len(in_bytes) - 1):
            out_string += " "
    return out_string

# to transform string to bytearray()
def str_to_byte(in_str):
    out_bytes = bytearray()
    str_to_byte_i = 0
    for str_to_byte_i in range(len(in_str)):
        out_bytes.append(ord(in_str[str_to_byte_i]))
    return out_bytes

# to transform string line of hexes to bytearray()
def hex_str_to_byte(in_str):
    hex_symb_line_num = "0123456789"
    hex_symb_line_upp = "ABCDEF"
    hex_symb_line_low = "abcdef"
    out_bytes = bytearray()
    in_str_clean = str()
    in_str_clean = in_str.replace(" ", str())
    if (len(in_str_clean) % 2) == 0:
        str_to_byte_i = 0
        for str_to_byte_i in range(len(in_str_clean) // 2):
            tmp_high_byte = 0
            tmp_low_byte = 0
            tmp_s_high = in_str_clean[(str_to_byte_i * 2) + 0]
            if tmp_s_high in hex_symb_line_num:
                tmp_high_byte = ord(tmp_s_high) - ord(hex_symb_line_num[0])
            if tmp_s_high in hex_symb_line_upp:
                tmp_high_byte = ord(tmp_s_high) - ord(hex_symb_line_upp[0]) + 10
            if tmp_s_high in hex_symb_line_low:
                tmp_high_byte = ord(tmp_s_high) - ord(hex_symb_line_low[0]) + 10
            tmp_s_low = in_str_clean[(str_to_byte_i * 2) + 1]
            if tmp_s_low in hex_symb_line_num:
                tmp_low_byte = ord(tmp_s_low) - ord(hex_symb_line_num[0])
            if tmp_s_low in hex_symb_line_upp:
                tmp_low_byte = ord(tmp_s_low) - ord(hex_symb_line_upp[0]) + 10
            if tmp_s_low in hex_symb_line_low:
                tmp_low_byte = ord(tmp_s_low) - ord(hex_symb_line_low[0]) + 10
            out_bytes.append(tmp_high_byte * 16 + tmp_low_byte)
            del tmp_high_byte, tmp_low_byte
    return out_bytes

def send_OP_STOP():
    return bytearray((0x00, 0x00))

def send_MAN_QUERY_INFO():
    return bytearray((0x00, 0x00))

def send_OP_QUERY_RFID_ABILITY():
    return bytearray((0x00, 0x00))

def send_OP_QUERY_FREQ():
    return bytearray((0x00, 0x00))

def send_OP_CONF_RF_BAND(rf_band_set): # RF_FREQUENCY_RANGE
    array_res = bytearray()
    array_res.append(0)
    array_res.append(1)
    array_res.append(rf_band_set)
    return array_res

def send_OP_CONF_ANT(ant_list_set): # list of numbers of antennas to enable, for instance, (1, 6, 3), # from 1 to 8
    if len(ant_list_set) > 8:
        post_log_message("Too many elements in antenna list: send_OP_CONF_ANT(ant_list_set) - " + str(len(ant_list_set)))
        return bytearray()
    tmp_res = 0
    j = 0
    for j in ant_list_set:
        if j <= 8:
            tmp_res = tmp_res + (2**(j-1))
        else:
            post_log_message("Wrong elements (> 8) in antenna list: send_OP_CONF_ANT(ant_list_set)")
            return bytearray()
    if tmp_res > 255:
        post_log_message("Error: can be duplicated elements in antenna list: send_OP_CONF_ANT(ant_list_set)")
        return bytearray()
    array_res = bytearray()
    array_res.append(0)
    array_res.append(1)
    array_res.append(tmp_res)
    del(j, tmp_res)
    return array_res

def send_OP_CONF_POWER(power_per_ant_dict_set):
    # dict() of not more than 4 pairs, key = # of antenna (from 1 to 4)
    # value = power in range 0~36
    if len(power_per_ant_dict_set) > 4:
        post_log_message("Too many elements in dict: send_OP_CONF_POWER(power_per_ant_dict_set) - " + str(len(power_per_ant_dict_set)))
        return bytearray()
    res_len = 0
    tmp_res = bytearray()
    tmp_res.append(0)
    tmp_res.append(0)
    j = 0
    for j in power_per_ant_dict_set.keys():
        if (power_per_ant_dict_set[j] < 0) or (power_per_ant_dict_set[j] > 36):
            post_log_message("Wrong key elements in dict: send_OP_CONF_POWER(power_per_ant_dict_set)")
            return bytearray()
        else:
            tmp_res.append(j)
            tmp_res.append(power_per_ant_dict_set[j])
            res_len = res_len + 2
    tmp_res[1] = res_len
    del(j, res_len)
    return tmp_res

def send_OP_READ_EPC_TAG(ant_list_set, single_read_mode): # list of antennas to use, single read is True, continuous read False
    if len(ant_list_set) > 8:
        post_log_message("Too many elements in antenna list: send_OP_READ_EPC_TAG - " + str(len(ant_list_set)))
        return bytearray()
    tmp_res = 0
    j = 0
    for j in ant_list_set:
        if j <= 8:
            tmp_res = tmp_res + (2**(j-1))
        else:
            post_log_message("Wrong elements (> 8) in antenna list: send_OP_READ_EPC_TAG")
            return bytearray()
    if tmp_res > 255:
        post_log_message("Error: can be duplicated elements in antenna list: send_OP_READ_EPC_TAG")
        return bytearray()
    array_res = bytearray()
    array_res.append(tmp_res)
    if single_read_mode:
        array_res.append(0)
    else:
        array_res.append(1)
    del(j, tmp_res)
    return array_res

def decode_tag_data_frame(response_frame_data): # decoding tag data frame 
    tag_data_res = TagData()
    if type(response_frame_data) != type(bytearray()):
        post_log_message('Error: response_frame_data in decode_tag_data_frame(response_frame_data) is not bytearray()')
        tag_data_res.decode_error = True
        return tag_data_res
    line_index = 2              # start of line index - at 3rd byte just after frame data len
    tmp_epc_len = (256 * response_frame_data[line_index]) + response_frame_data[line_index+1]
    line_index += 2             # shift index to EPC code content
    j_tmp = 0
    for j_tmp in range(tmp_epc_len):
        tag_data_res.EPC_code.append(response_frame_data[line_index+j_tmp])
    line_index += tmp_epc_len   # shift index to next parameter = tag PC value
    tag_data_res.PC_value = (256 * response_frame_data[line_index]) + response_frame_data[line_index+1]
    tmp_PC_val = response_frame_data[line_index]
    (tmp_PC_val, tag_data_res.num_sys_id_toggle) = divmod(tmp_PC_val, 2**1)
    (tmp_PC_val, tag_data_res.XPC_indicator) = divmod(tmp_PC_val, 2**1)
    (tmp_PC_val, tag_data_res.UMI) = divmod(tmp_PC_val, 2**1)
    (tmp_PC_val, tag_data_res.EPC_len) = divmod(tmp_PC_val, 2**5)
    del(tmp_PC_val)
    tag_data_res.RFU = response_frame_data[line_index+1]
    line_index += 2             # shift index to antenna ID
    tag_data_res.ant_id = response_frame_data[line_index]
    line_index += 1             # shift to optional params block
    tmp_exit_flag = False
    while not tmp_exit_flag:
        if line_index == len(response_frame_data):
            tmp_exit_flag = True
        elif line_index < len(response_frame_data):
            tmp_opt_param = response_frame_data[line_index]
            if tmp_opt_param == 0x01:      # ============= RSSI
                line_index += 1     # shift index to optional parameter contents (starting from 2 byte len if variable len param)
                tag_data_res.params[tmp_opt_param] = response_frame_data[line_index]
                line_index += 1     # shift index forward to next opt param id
            elif tmp_opt_param == 0x02:    # ============= read result
                line_index += 1
                tag_data_res.params[tmp_opt_param] = response_frame_data[line_index]
                line_index += 1
            elif (tmp_opt_param == 0x03) or (tmp_opt_param == 0x04) or (tmp_opt_param == 0x05) or (tmp_opt_param == 0x0C):
                tag_data_res.params[tmp_opt_param] = bytearray()
                line_index += 1
                tmp_opt_p_len = (256 * response_frame_data[line_index]) + response_frame_data[line_index+1]
                line_index += 2
                jj_tmp = 0
                for jj_tmp in range(tmp_opt_p_len):
                    tag_data_res.params[tmp_opt_param].append(response_frame_data[line_index+jj_tmp])
                line_index += tmp_opt_p_len
                del(tmp_opt_p_len, jj_tmp)
            elif tmp_opt_param == 0x06:
                pass
            elif tmp_opt_param == 0x07:
                line_index += 1
                tmp_sec  = float()
                tmp_sec += (256**3) * response_frame_data[line_index+0]
                tmp_sec += (256**2) * response_frame_data[line_index+1]
                tmp_sec += (256**1) * response_frame_data[line_index+2]
                tmp_sec += (256**0) * response_frame_data[line_index+3]
                tmp_microsec  = float()
                tmp_microsec += (256**3) * response_frame_data[line_index+4]
                tmp_microsec += (256**2) * response_frame_data[line_index+5]
                tmp_microsec += (256**1) * response_frame_data[line_index+6]
                tmp_microsec += (256**0) * response_frame_data[line_index+7]
                tag_data_res.params[tmp_opt_param] = tmp_sec + (tmp_microsec / 1000000)
                line_index += 8
                del(tmp_microsec, tmp_sec)
            elif tmp_opt_param == 0x08:
                tag_data_res.params[tmp_opt_param] = bytearray()
                line_index += 1
                tag_data_res.params[tmp_opt_param].append(response_frame_data[line_index+0])
                tag_data_res.params[tmp_opt_param].append(response_frame_data[line_index+1])
                tag_data_res.params[tmp_opt_param].append(response_frame_data[line_index+2])
                tag_data_res.params[tmp_opt_param].append(response_frame_data[line_index+3])
                line_index += 4
            elif tmp_opt_param == 0x09:
                pass
            elif tmp_opt_param == 0x0A:
                pass
            elif tmp_opt_param == 0x0B:
                pass
        else:
            post_log_message('Error: wrong optional params detected in decode_tag_data_frame(response_frame_data)')
            tag_data_res.decode_error = True
            return tag_data_res
    # tag_data_res.params[0x03] = tag_data_res.EPC_code # -------- ONLY TESTING -----------
    del(tmp_exit_flag, line_index, j_tmp, tmp_epc_len)
    return tag_data_res

def post_log_tag_data(tag_data_object):
    global global_log_list
    if global_logging_level > 0:
        if type(tag_data_object) != type(TagData()):
            post_log_message('Error: tag_data_object in post_log_tag_data(tag_data_object) is not TagData()')
        ss_tmp =                    "Tag EPC code       = "
        jj = 0
        for jj in range(len(tag_data_object.EPC_code)):
            ss_tmp = ss_tmp + "{0:02X}".format(tag_data_object.EPC_code[jj])
        global_log_list.append(ss_tmp)
        global_log_list.append(        "Tag EPC len        = " + str(tag_data_object.EPC_len * 16) + " bits")
        global_log_list.append(        "Tag UMI            = " + str(tag_data_object.UMI))
        global_log_list.append(        "Tag XPC indicator  = " + str(tag_data_object.XPC_indicator))
        global_log_list.append(        "Tag num system id  = " + str(tag_data_object.num_sys_id_toggle))
        global_log_list.append(        "Tag RFU            = 0x" + "{0:02X}".format(tag_data_object.RFU))
        global_log_list.append(        "Antenna ID         = " + str(tag_data_object.ant_id))
        for op_keys in tag_data_object.params.keys():
            if op_keys == TAG_DATA['RSSI']:
                global_log_list.append("RSSI value         = " + str(tag_data_object.params[op_keys]))
            elif op_keys == TAG_DATA['TIME']:
                global_log_list.append("Tag read clock     = " + strftime("%d.%m.%Y %H:%M:%S",  gmtime(tag_data_object.params[op_keys])))
            elif op_keys == TAG_DATA['SERIES_NUM']:
                ss_tmp =            "Frame serial num   ="
                jj = 0
                for jj in range(len(tag_data_object.params[0x08])):
                    ss_tmp = ss_tmp + " " + "{0:02X}".format(tag_data_object.params[0x08][jj])
                global_log_list.append(ss_tmp)    
        del jj, ss_tmp

# Return logs to the user
def get_log():
    return global_log_list

# Flush log list
def flush_log():
    global global_log_list
    global_log_list = list()

# Enable log writing
def logging_level_set(global_logging_level_set):
    global global_logging_level
    if type(global_logging_level_set) != int:
        return -51
    if (global_logging_level_set < 0) or (global_logging_level_set > 2):
        return -52
    global_logging_level = global_logging_level_set
    return 0

class ClouRFIDReader:
    def __init__(self, clou_reader_id_set, single_read_buffer_set = 2**14):
        if type(clou_reader_id_set) != int:
            return -4001
        self._device_fd = serial.Serial()
        self._raw_data_received_buffer = bytearray()
        self._split_frames_received_list = list()
        self._single_read_buffer = single_read_buffer_set
        self._json_output = str()
        self.clou_reader_id = clou_reader_id_set
    # General send method
    def _send_general_MID(self, command_MID, command_message_type, command_start_data_with_len, command_data_bytes):
        request_frame = ClouRFIDFrame(command_MID, command_message_type, INIT_BY_USER, RS485_USED, self.clou_reader_id, command_data_bytes)
        request_frame.start_data_with_len = command_start_data_with_len
        request_frame.encodeFrame()
        command_data_bytes_sent = 0
        try:
            command_data_bytes_sent = self._device_fd.write(request_frame.frame_raw_line)
        except Exception as send_general_MID_exception:
            post_log_message("_send_general_MID(): " + str(send_general_MID_exception))
            return -1001
        if  command_data_bytes_sent != len(request_frame.frame_raw_line):
            post_log_message('_send_general_MID(): error, sent ' + str(command_data_bytes_sent) + ' bytes, requested ' + str(len(request_frame.frame_raw_line)) + ' bytes: ', request_frame, 0)
            return -1002
        else:
            post_log_message('SENT: ', request_frame, 0)
        del request_frame, command_data_bytes_sent
        return 0
    # Split _raw_data_received_buffer line into list of frames _split_frames_received_list, and cleans it
    def _split_raw_data_received_buffer(self):
        while len(self._raw_data_received_buffer) >= 8:
            response_raw_line_stream = str(self._raw_data_received_buffer)            
            tmp_idx = 0 # if there are more than one 0xAA in a response_raw_line_stream?
            tmp_idx_break_flag = True
            # debug logging ====
            if global_logging_level > 2: post_log_message("response_raw_line_stream = " + byte_to_str(response_raw_line_stream))
            # ==================
            while tmp_idx_break_flag:
                response_raw_line_AA_idx = response_raw_line_stream.find(chr(0xAA), tmp_idx)
                # here check whether there are possibility to have correct packet from reader in a string
                # this below is only if there is a good chance to have
                # the correct message fully collected
                # debug logging ====
                if global_logging_level > 2: post_log_message("response_raw_line_AA_idx = " + str(response_raw_line_AA_idx) + ", tmp_idx = " + str(tmp_idx))
                # ==================
                if (response_raw_line_AA_idx > -1) and ((len(response_raw_line_stream) - response_raw_line_AA_idx) >= 8):
                    tmp_idx = response_raw_line_AA_idx + 1
                    res_cut_line_tmp = str()
                    res_cut_line_tmp += response_raw_line_stream[0 + response_raw_line_AA_idx]
                    res_cut_line_tmp += response_raw_line_stream[1 + response_raw_line_AA_idx]
                    res_cut_line_tmp += response_raw_line_stream[2 + response_raw_line_AA_idx]
                    res_cut_line_tmp += response_raw_line_stream[3 + response_raw_line_AA_idx]
                    res_cut_line_tmp += response_raw_line_stream[4 + response_raw_line_AA_idx]
                    res_cut_line_tmp += response_raw_line_stream[5 + response_raw_line_AA_idx]
                    len_tmp = (256 * ord(response_raw_line_stream[4 + response_raw_line_AA_idx])) + ord(response_raw_line_stream[5 + response_raw_line_AA_idx])
                    if (len_tmp <= 1024) and ((len(response_raw_line_stream) - response_raw_line_AA_idx) >= (8 + len_tmp)):
                        res_cut_line_tmp += response_raw_line_stream[(6 + response_raw_line_AA_idx):(6 + len_tmp + 2 + response_raw_line_AA_idx)]
                        # debug logging ====
                        if global_logging_level > 2: post_log_message("res_cut_line_tmp = " + byte_to_str(res_cut_line_tmp))
                        # ==================
                        crc16_func = mkCrcFun(0x10000+0x8005, initCrc = 0, rev = False)        
                        res_cut_line_tmp_crc = res_cut_line_tmp[1:-2]
                        crc16_value = crc16_func(res_cut_line_tmp_crc)
                        crc16_msb = crc16_value // 256
                        crc16_lsb = crc16_value % 256
                        # ==================
                        if (crc16_msb == ord(res_cut_line_tmp[-2:-1])) and (crc16_lsb == ord(res_cut_line_tmp[-1:])):
                            self._split_frames_received_list.append(res_cut_line_tmp)
                            new_raw_line = str()
                            new_raw_line = response_raw_line_stream[:response_raw_line_AA_idx] + response_raw_line_stream[(len(res_cut_line_tmp) + response_raw_line_AA_idx):]
                            # debug logging ====
                            if global_logging_level > 2: post_log_message("new_raw_line = " + byte_to_str(new_raw_line))
                            # ==================
                            self._raw_data_received_buffer = bytearray(new_raw_line)
                            tmp_idx_break_flag = False
                            del new_raw_line
                        del crc16_msb, crc16_lsb, crc16_value, crc16_func, res_cut_line_tmp_crc
                    del res_cut_line_tmp, len_tmp
                else:
                    tmp_idx_break_flag = False
                del response_raw_line_AA_idx
            del response_raw_line_stream, tmp_idx, tmp_idx_break_flag
    # General read method
    def _read_general(self):
        raw_response_line = bytearray()
        frames_received_cnt = 0
        # First we read from device
        try:
            raw_response_line = self._device_fd.read(self._single_read_buffer)           
        except Exception as read_general_exception:
            post_log_message("_read_general(): " + str(read_general_exception))
            return -2002                    
        tmp_result_bytes = bytearray()
        tmp_result_bytes = self._raw_data_received_buffer + raw_response_line
        self._raw_data_received_buffer = tmp_result_bytes
        del raw_response_line, tmp_result_bytes
        # Here we extracting frames until all recognized are extracted
        # all that is not a frame is left intact in self._raw_data_received_buffer
        prev_split_frames_len = len(self._split_frames_received_list)
        prev_split_len = 0
        after_split_len = -1
        while after_split_len < prev_split_len:
            prev_split_len = len(self._raw_data_received_buffer)
            self._split_raw_data_received_buffer()
            after_split_len = len(self._raw_data_received_buffer)
        del prev_split_len, after_split_len
        frames_received_cnt = len(self._split_frames_received_list) - prev_split_frames_len
        del prev_split_frames_len
        # Return how many frames recognized and added to self._split_frames_received_list
        return frames_received_cnt
    # Connect methods
    def conn_open(self, port_name, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None):
        if type(port_name) != str:
            return -11
        if len(port_name) == 0:
            return -12    
        try:
            self._device_fd = serial.Serial(port_name, baudrate, bytesize, parity, stopbits, timeout, xonxoff, rtscts, write_timeout, dsrdtr, inter_byte_timeout)
        except Exception as conn_open_exception:
            post_log_message("conn_open: " + str(conn_open_exception))
            return -13
        return 0
    # Close method
    def conn_close(self):
        try:
            self._device_fd.close()
        except Exception as conn_close_exception:
            post_log_message("conn_close: " + str(conn_close_exception))
            return -24
        return 0
    # Set reading timout
    def set_read_timeout(self, timeout_to_set):
        if (type(timeout_to_set) != int) and (type(timeout_to_set) != float):
            return -42
        try:
            self._device_fd.timeout = timeout_to_set
        except Exception as set_read_timeout_exception:
            post_log_message("set_read_timeout: " + str(set_read_timeout_exception))
            return -43
        return 0
    # Send OP_STOP, wait for answer, decode, and return result
    def send_stop(self):
        if self._device_fd == serial.Serial():
            return -36
        send_general_MID_res = self._send_general_MID('OP_STOP', TYPE_CONF_OPERATE, True, send_OP_STOP())
        if send_general_MID_res == 0:
            read_frames_cnt = self._read_general()
            if read_frames_cnt == 0:                
                return -32
            else:
                i = 0
                found_OK_frame = False
                temp_split_frames_received_list = self._split_frames_received_list
                self._split_frames_received_list = list()
                for i in range(len(temp_split_frames_received_list)):
                    response_raw_frame = ClouRFIDFrame()
                    response_raw_frame.frame_raw_line = bytearray(temp_split_frames_received_list[i])
                    res_decode_frame = response_raw_frame.decodeFrame()
                    if res_decode_frame == 0:
                        if (response_raw_frame.rs485_id == self.clou_reader_id) and (response_raw_frame.message_id == 'OP_STOP') and (response_raw_frame.init_by_reader == INIT_BY_USER):
                            if response_raw_frame.data_bytes == bytearray((0x00, 0x01, 0x00)):
                                found_OK_frame = True
                                post_log_message("send_stop(): received OK -> ", response_raw_frame, res_decode_frame)
                    else:
                        post_log_message("send_stop(): error decoding frame -> ", response_raw_frame, res_decode_frame)                        
                if not found_OK_frame:
                    del temp_split_frames_received_list                    
                    return -32
                del temp_split_frames_received_list
        else:
            return send_general_MID_res
        del send_general_MID_res
        return 0
    # Send OP_READ_EPC_TAG, wait for answer, decode, and return results including tags data
    def send_scan_once(self, reader_ant_to_use_set):
        if self._device_fd == serial.Serial():
            return -61
        tags_read_cnt = 0
        self._json_output = str()
        send_general_MID_res = self._send_general_MID('OP_READ_EPC_TAG', TYPE_CONF_OPERATE, True, send_OP_READ_EPC_TAG(reader_ant_to_use_set, True))
        if send_general_MID_res == 0:
            read_frames_cnt = self._read_general()
            if read_frames_cnt == 0:                
                return -62
            else:
                i = 0
                found_OK_frame = False
                tag_data_out_list = list()
                read_tags_table_EPC = list()
                temp_split_frames_received_list = self._split_frames_received_list
                self._split_frames_received_list = list()
                for i in range(len(temp_split_frames_received_list)):
                    response_raw_frame = ClouRFIDFrame()
                    response_raw_frame.frame_raw_line = bytearray(temp_split_frames_received_list[i])
                    res_decode_frame = response_raw_frame.decodeFrame()
                    if res_decode_frame == 0:
                        if (response_raw_frame.rs485_id == self.clou_reader_id) and (response_raw_frame.message_id == 'OP_READ_EPC_TAG') and (response_raw_frame.init_by_reader == INIT_BY_USER):
                            if (len(response_raw_frame.data_bytes) == 3) and (response_raw_frame.data_bytes[0:2] == bytearray((0x00, 0x01))):
                                if response_raw_frame.data_bytes[2] == 0:
                                    found_OK_frame = True
                                    post_log_message("send_scan_once(): received OK -> ", response_raw_frame, res_decode_frame)
                                else:
                                    post_log_message("send_scan_once(): error initializing scan: " + DECODE_READ_EPC_TAG[response_raw_frame.data_bytes[2]] + " -> ", response_raw_frame, res_decode_frame)
                                    del temp_split_frames_received_list
                                    return -65
                        if (response_raw_frame.rs485_id == self.clou_reader_id) and (response_raw_frame.message_id == 'OP_READER_EPC_DATA_UPLOAD') and (response_raw_frame.init_by_reader == INIT_BY_READER):
                            res_cut_line_tmp = bytearray(temp_split_frames_received_list[i])
                            epc_data = TagData()
                            epc_data = decode_tag_data_frame(res_cut_line_tmp[4:-2])
                            if epc_data.EPC_code not in read_tags_table_EPC:
                                read_tags_table_EPC.append(epc_data.EPC_code)
                                tag_data_out_list.append(epc_data.encodeInDict())
                            del res_cut_line_tmp, epc_data
                    else:
                        post_log_message("send_scan_once(): error decoding frame -> ", response_raw_frame, res_decode_frame)                        
                del temp_split_frames_received_list
                if found_OK_frame:
                    tags_read_cnt = len(tag_data_out_list)
                    if tags_read_cnt > 0:
                        self._json_output = dumps(tag_data_out_list, skipkeys = True)
                else:
                    return -64
                del tag_data_out_list, read_tags_table_EPC
        else:
            return send_general_MID_res
        del send_general_MID_res
        return tags_read_cnt
    # Get JSON field
    def get_json_output(self):
        return self._json_output
