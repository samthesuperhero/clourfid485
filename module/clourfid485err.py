ERRNAME = {
    -1001: "send: serial.write exception",
    -1002: "send: bytes sent not equal bytes requested to send",
    -1003: "send_general_MID: connection_context is not SerialConnectionContext() object",
    -2001: "read_general: connection_context is not SerialConnectionContext() object",
    -2002: "read_general: serial.read exception",
    -11: "conn_open: port name is not str() type",
    -12: "conn_open: port name is empty",
    -13: "conn_open: serial.Serial exception",
    -14: "conn_open: connection_context is not SerialConnectionContext() object",
    -21: "conn_close: connection_context is not SerialConnectionContext() object",
    -24: "conn_close: serial.close exception",
    -31: "send_stop: connection_context is not SerialConnectionContext() object",
    -35: "send_stop: timeout = int or float",
    -36: "send_stop: serial port descriptor connection_context.device_fd empty"
    }