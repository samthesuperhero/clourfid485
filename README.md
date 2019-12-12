# clourfid485
A Python module to connect to Clou (Hopeland) RFID readers via RS 485


First create the reader class instance,
```
your_clou_reader_instance = clourfid485.ClouRFIDReader(int ID of reader on RS485 bus)
```

Almost all methods return 0 if successful (if not specified otherwise), or some other integer (depending) if not, see error codes below.

When logging enabled with, for instance with logging_level_set(1), it starts to write logs into the background buffer existing till the end of the process, you can get contents of buffer with get_log() - THIS TO BE UPDATED also in near future

Connect method
```
int = your_clou_reader_instance.conn_open(port_name,
                                          baudrate=9600,
                                          bytesize=serial.EIGHTBITS,
                                          parity=serial.PARITY_NONE,
                                          stopbits=serial.STOPBITS_ONE,
                                          timeout=None,
                                          xonxoff=False,
                                          rtscts=False,
                                          write_timeout=None,
                                          dsrdtr=False,
                                          inter_byte_timeout=None
                                          )
```

Set reading timout
```
int = your_clou_reader_instance.set_read_timeout(timeout_set)
```

Close method
```
int = your_clou_reader_instance.conn_close()
```

Send OP_STOP, wait for answer, decode, and return result
```
int = your_clou_reader_instance.send_stop()
```

Send OP_READ_EPC_TAG, wait for answer, decode, and return results including tags data
```
int = your_clou_reader_instance.send_scan_once(reader_ant_to_use_set)
```
here int is < 0 if error, and >= 0 indicating how many tags were read, reader_ant_to_use_set is a list() with int values indicating antennas to use, say, [1, 4, 5, 8] if you have 8-antenna reader and want to use four antennas with ids 1, 4, 5 and 8

Get JSON with reading results - call right after receiving > 0 from your_clou_reader_instance.send_scan_once
```
str = your_clou_reader_instance.get_json_output(self)
```

This will be the JSON list:
```
[
{
"decode_error": false,
"EPC_code": "300ED89F3350005FE235FA1E",
"RFU": "0x00",
"num_sys_id_toggle": 0,
"EPC_len": 96,
"ant_id": 1,
"params": {
"1": 106,
"7": 1187963668.824717
},
"XPC_indicator": 0,
"UMI": 0
}
4
public
]
```

where:
**false** – tag data frame decode result, must always be false, ignore those where is true set
**300ED89F3350005FE235FA1E** – tag EPC code
**96** – len of EPC field in bits
**1** – ID of antenna that detected the tag
**106** – RSSI level
**1187963668.824717** – UNIX style timestamp for the time when tag was read, by the embedded clock of reader device

Ignore other parameters in JSON objects in the list.

Return logs to the user
```
list = get_log()
```

Flush log list
```
int = flush_log()
```

Enable log writing, 0 (default) no logging, 1 basic logging, 2, 3 for extended logging modes for debugging
```
int = logging_level_set(global_logging_level_set)
```

Get error discriptions for error codes
```
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
 ```

