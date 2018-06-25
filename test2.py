import cloufrid485

cloufrid485.log_enable()

cloufrid485.conn_open("/dev/ttyUSB1", 115200, timeout = 1)

cloufrid485.send_stop(42, 1)

cloufrid485.conn_close()

print(cloufrid485.get_log())

print("\n\nSuccess!\n")
