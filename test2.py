import clourfid485

clourfid485.logging_level_set(1)

reader_inst_1 = clourfid485.ClouRFIDReader(42)

print("reader_inst_1 opened = ", reader_inst_1.conn_open("/dev/ttyUSB1", 115200, timeout = 1))
print("reader_inst_1.send_stop(): ", reader_inst_1.send_stop())
print("reader_inst_1.send_scan_once(): ", reader_inst_1.send_scan_once(1))
print(reader_inst_1._json_output)
print("reader_inst_1 closed = ", reader_inst_1.conn_close())

log_sheet = clourfid485.get_log()
i = 0
for i in range(len(log_sheet)):
    print(log_sheet[i] + "\n")

print("\nSuccess!\n")
