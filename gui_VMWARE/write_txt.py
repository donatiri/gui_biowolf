from ctypes import byref, create_string_buffer, c_int, sizeof, POINTER, \
    cast, c_uint8, c_uint16, c_ubyte, string_at, c_void_p, cdll, addressof, \
    c_char

import datetime

n_bytes = 17
buf = c_ubyte * n_bytes
write_command_buf = buf(0x00, 0x00,0x01,0x00,0x06, 0x00, 0x00, 0x00,0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08)


#open file in append mode
file1=open(r"prova1.txt","a+")

file1.write('\nACQUISITION DATE & TIME: %s \n\n' % datetime.datetime.now())
for i in range(n_bytes):
	byte = write_command_buf[i]
	file1.write(' %d ' % byte)
	file1.write('\n')
print("success")
file1.close()


