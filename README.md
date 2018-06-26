# clourfid485
A Python module to connect to Clou (Hopeland) RFID readers via RS 485

=== Short description =======================================================================================
First create the connection context object, it will be used in almost all methods, and contains all connection objects, raw data, etc.:

connection_context = clourfid485.SerialConnectionContext()

Do not destroy it until close connection.

Almost all methods return 0 if successful (if not specified otherwise), or other integer if not, see error codes below.

When logging enabled with, for instance with logging_level_set(1), it starts to write logs into the background buffer existing till the end of the process, you can get contents of buffer with get_log()

# Connect method
int = conn_open(connection_context, port_name, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None)

# Set reading timout
int = set_read_timeout(connection_context, timeout_set)

# Close method
int = conn_close(connection_context)

# Send OP_STOP, wait for answer, decode, and return result
int = send_stop(connection_context, command_rs485_id)

# Return logs to the user
list = get_log()

# Flush log list
int = flush_log()

# Enable log writing, 0 (default) no logging, 1 basic logging, 2, 3 for extended logging modes for debugging
int = logging_level_set(global_logging_level_set)

# Get error discriptions for error codes
ERR_NAME_DICT = {
    -11: "conn_open: port name is not str() type",
    -12: "conn_open: port name is empty",
    -13: "conn_open: serial.Serial exception",
    -14: "conn_open: connection_context is not SerialConnectionContext() object",
    -21: "conn_close: connection_context is not SerialConnectionContext() object",
    -24: "conn_close: serial.close exception",
    -31: "send_stop: connection_context is not SerialConnectionContext() object",
    -36: "send_stop: serial port descriptor connection_context.device_fd empty",
    -41: "set_read_timeout: connection_context is not SerialConnectionContext() object",
    -42: "set_read_timeout: timeout_set must be int or float",
    -43: "conn_close: serial.timeout set exception",
    -51: "logging_level_set: global_logging_level_set must be int",
    -52: "logging_level_set: global_logging_level_set availabel values: 0, 1, 2",
    -1001: "send: serial.write exception",
    -1002: "send: bytes sent not equal bytes requested to send",
    -1003: "send_general_MID: connection_context is not SerialConnectionContext() object",
    -2001: "read_general: connection_context is not SerialConnectionContext() object",
    -2002: "read_general: serial.read exception",
    -3001: "split_raw_data_received_buffer: connection_context is not SerialConnectionContext() object"
    }
