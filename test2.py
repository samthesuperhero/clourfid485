import clourfid485

clourfid485.log_enable()

clourfid485.conn_open("/dev/ttyUSB1", 115200, timeout = 1)

clourfid485.send_stop(42, 1)

clourfid485.conn_close()

print(clourfid485.get_log())

print("\n\nSuccess!\n")
