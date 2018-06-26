import clourfid485

sr_cont = clourfid485.SerialConnectionContext()

clourfid485.log_enable()

clourfid485.conn_open(sr_cont, "/dev/ttyUSB1", 115200, timeout = 1)

print(clourfid485.send_stop(sr_cont, 42))

clourfid485.conn_close(sr_cont)

print(clourfid485.get_log())

print("\nSuccess!\n")
