import clourfid485

clourfid485.logging_level_set(1)

reader_inst_1 = clourfid485.SerialConnectionContext(42)
reader_inst_2 = clourfid485.SerialConnectionContext(42)

print("reader_inst_1 opened = ", reader_inst_1.conn_open("/dev/ttyUSB1", 115200, timeout = 1))
print("reader_inst_2 opened = ", reader_inst_2.conn_open("/dev/ttyUSB1", 115200, timeout = 1))

print("reader_inst_1.send_stop(): ", reader_inst_1.send_stop())
print("reader_inst_2.send_stop(): ", reader_inst_2.send_stop())

print("reader_inst_2 closed = ", reader_inst_2.conn_close())
print("reader_inst_1 closed = ", reader_inst_1.conn_close())

for log_line in clourfid485.get_log():
    print(log_line, "\n")

print("\nSuccess!\n")
