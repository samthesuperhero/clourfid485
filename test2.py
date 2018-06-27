import clourfid485

reder_inst_1 = clourfid485.SerialConnectionContext()
reder_inst_2 = clourfid485.SerialConnectionContext()

clourfid485.log_enable()

print("1 o ", reder_inst_1.conn_open("/dev/ttyUSB1", 115200, timeout = 1))

print("2 o ", reder_inst_2.conn_open("/dev/ttyUSB1", 115200, timeout = 1))

# print(clourfid485.send_stop(sr_cont, 42))

print("2 c ", reder_inst_2.conn_close())

print("1 c ", reder_inst_1.conn_close())


print(clourfid485.get_log())

print("\nSuccess!\n")
