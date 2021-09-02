from PyQt4.QtCore import *
from PyQt4 import QtGui
import struct
import time
import datetime
import tables
from tables import *
from enum import Enum
from queue import Queue
import libusb1

import usb1
import ctypes 
from ctypes import byref, create_string_buffer, c_int, sizeof, POINTER, \
    cast, c_uint8, c_uint16, c_ubyte, string_at, c_void_p, cdll, addressof, \
    c_char
import os



 
datalen = 200
context = libusb1.libusb_context_p()
deviceList = libusb1.libusb_device_p_p()
deviceCount = 0
deviceDescriptor = libusb1.libusb_device_descriptor()
device = libusb1.libusb_device_p()
cp2130Handle = libusb1.libusb_device_handle_p()
kernelAttached = 0
print("stampato");
dev_list = []

if libusb1.libusb_init(byref(context)) != 0:
	print('Could not initialize libusb!')


deviceCount = libusb1.libusb_get_device_list(context, byref(deviceList))
if deviceCount <= 0:
	print('No devices found!')
for i in range(0, deviceCount):
	if libusb1.libusb_get_device_descriptor(deviceList[i], byref(deviceDescriptor)) == 0:
		if (deviceDescriptor.idVendor == 0x10C4) and (deviceDescriptor.idProduct == 0x87A0):
			dev_list.append(deviceList[i])
			device = deviceList[i]
			print('entro')


if libusb1.libusb_open(device, byref(cp2130Handle)) != 0:
	print('Could not open device!')
	


print(deviceCount)
print("fine");

if libusb1.libusb_kernel_driver_active(cp2130Handle, 0) != 0:
	libusb1.libusb_detach_kernel_driver(cp2130Handle, 0)
	self.kernelAttached = 1
	print('return')

if libusb1.libusb_claim_interface(cp2130Handle, 0) != 0:
	print('Could not claim interface!')
	print('return2')

print("Connected to")


buf = c_ubyte * 8
input_buf = c_ubyte * 8
#read_input_buf = input_buf(0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00)
read_input_buf=(c_ubyte *56)(*[0x00])
read_command_buf = buf(0x00, 0x00,0x00,0x00,0x38, 0x00, 0x00, 0x00)
    # read 6 bytes, little-endian
bytesWritten = c_int()
bytesRead = c_int()
usbTimeout = 500
while 1:

	error_code_write = libusb1.libusb_bulk_transfer(cp2130Handle, 0x02, read_command_buf, sizeof(read_command_buf), byref(bytesWritten), 0)

 
	if error_code_write:
		print('Error in bulk transfer (write command)! Error # {}'.format(error_code_write))
		print(libusb1.libusb_strerror(error_code_write))
		print(libusb1.libusb_error_name(error_code_write))

	#if bytesWritten != sizeof(read_command_buf):
		#print("Error in bulk transfer write size")

	error_code_read = libusb1.libusb_bulk_transfer(cp2130Handle, 0x81, read_input_buf, sizeof(read_input_buf), byref(bytesRead), 0)
	

	error_code_write = libusb1.libusb_bulk_transfer(cp2130Handle, 0x02, read_command_buf, sizeof(read_command_buf), byref(bytesWritten), 0)
	error_code_read = libusb1.libusb_bulk_transfer(cp2130Handle, 0x81, read_input_buf, sizeof(read_input_buf), byref(bytesRead), 0)

	if error_code_read:
		print('Error in bulk transfer (read command)! Error # {}'.format(error_code_read))
		print(libusb1.libusb_strerror(error_code_read))
		print(libusb1.libusb_error_name(error_code_read))

	print('Successfully read from SPI MISO, number of bytes read = {}'.format(bytesRead))

		
	#print(read_input_buf)
	for i in range(56):
 		#print(sizeof(read_input_buf))
		byte = read_input_buf[i]
		bytevalue=ctypes.c_ubyte(byte).value
		print(bytevalue)
		#print(byte)
	time.sleep(0.05)
		

released = libusb1.libusb_release_interface(cp2130Handle, 0)
if released:
	print('Not released successfully')
