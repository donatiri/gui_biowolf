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

# change device to read priority
def cp2130_libusb_set_usb_config(handle):
	buf = c_ubyte * 10
	control_buf_out = buf(0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80)
	usbTimeout = 5000

	error_code = libusb1.libusb_control_transfer(handle, 0x40, 0x61, 0xA5F1, 0x000A, control_buf_out, sizeof(control_buf_out), usbTimeout)
	if error_code != sizeof(control_buf_out):
		print('Error in bulk transfer')
		return False
	return True

def set_gpio_chip_select(handle,number,mode):
	buf = c_ubyte * 2
	#GPIO (0-10), MODE 0x00: Specified chip select is disabled 0x01: Specified chip select is enabled during SPI transfers 0x02: Specified chip select is enabled during SPI transfers; allother chip selects are disabled

	control_buf_out = buf(number, mode)
	usbTimeout = 5000

	error_code = libusb1.libusb_control_transfer(handle, 0x40, 0x25, 0x0000, 0x0000, control_buf_out, sizeof(control_buf_out), usbTimeout)
	if error_code != sizeof(control_buf_out):
		print('Error in bulk transfer')
		return False
	return True

def set_gpio_mode_and_level(handle,number,mode,level):
	buf = c_ubyte * 3
	#GPIO (0-10), PINMODE (00 INPUT, 01 OPEN-DRAIN, 02 PUSH PULL), PIN LEVEL (00 LOW, O1 HIGH)
	#control_buf_out = buf(0x05, 0x02, 0x00)
	control_buf_out = buf(number, mode, level)
	usbTimeout = 5000

	error_code = libusb1.libusb_control_transfer(handle, 0x40, 0x23, 0x0000, 0x0000, control_buf_out, sizeof(control_buf_out), usbTimeout)
	if error_code != sizeof(control_buf_out):
		print('Error in bulk transfer')
		return False
	return True

def cp2130_libusb_read(handle,datalen):

	buf = c_ubyte * 8
	read_command_buf = buf(0x00, 0x00,0x00,0x00,datalen, 0x00, 0x00, 0x00)
	bytesWritten = c_int()
	buf= c_ubyte*datalen
	read_input_buf = buf()
	bytesRead = c_int()
	usbTimeout = 0

	error_code = libusb1.libusb_bulk_transfer(handle, 0x02, read_command_buf, sizeof(read_command_buf), byref(bytesWritten), usbTimeout)
	if error_code:
		print('Error in bulk transfer (read command). Error # {}'.format(error_code))
		return False
	if bytesWritten.value != sizeof(read_command_buf):
		print('Error in bulk transfer write size')
		print(bytesWritten.value)
		return False
        
	error_code = libusb1.libusb_bulk_transfer(handle, 0x81, read_input_buf, sizeof(read_input_buf), byref(bytesRead), usbTimeout)
	if error_code:
		print('Error in bulk transfer (read buffer). Error # {}'.format(error_code))
		return False
	if bytesRead.value != sizeof(read_input_buf):
		print('Error in bulk transfer - returned {} out of {} bytes'.format(bytesRead.value, sizeof(read_input_buf)))
		return False
	for i in range(datalen):
		byte = read_input_buf[i]
		bytevalue=ctypes.c_ubyte(byte).value
		print(bytevalue)
	print("end of transfer")
	return read_input_buf

#read only if GPIO3 (default) is asserted
def cp2130_libusb_readRTR(handle, datalen):
	
	buf = c_ubyte * 8
	read_command_buf = buf(0x00, 0x00,0x04,0x00,datalen, 0x00, 0x00, 0x00)
	bytesWritten = c_int()
	buf= c_ubyte*datalen
	read_input_buf = buf()
	bytesRead = c_int()
	usbTimeout = 0

	error_code = libusb1.libusb_bulk_transfer(handle, 0x02, read_command_buf, sizeof(read_command_buf), byref(bytesWritten), usbTimeout)
	if error_code:
		print('Error in bulk transfer (read command). Error # {}'.format(error_code))
		return False
	if bytesWritten.value != sizeof(read_command_buf):
		print('Error in bulk transfer write size')
		print(bytesWritten.value)
		return False
        
	error_code = libusb1.libusb_bulk_transfer(handle, 0x81, read_input_buf, sizeof(read_input_buf), byref(bytesRead), usbTimeout)
	if error_code:
		print('Error in bulk transfer (read buffer). Error # {}'.format(error_code))
		return False
	if bytesRead.value != sizeof(read_input_buf):
		print('Error in bulk transfer - returned {} out of {} bytes'.format(bytesRead.value, sizeof(read_input_buf)))
		return False
	for i in range(datalen):
		byte = read_input_buf[i]
		bytevalue=ctypes.c_ubyte(byte).value
		print(bytevalue)
	print("end of transfer")
	return read_input_buf

def cp2130_libusb_set_spi_word(handle,ch,word):
    buf = c_ubyte * 2
    control_buf_out = buf(ch, word)
    usbTimeout = 500

    error_code = libusb1.libusb_control_transfer(handle, 0x40, 0x31, 0x0000, 0x0000, control_buf_out, sizeof(control_buf_out), usbTimeout)
    if error_code != sizeof(control_buf_out):
        print('Error in bulk transfer')
        return False
    
    return True

def cp2130_libusb_get_spi_word(handle):
    buf = c_ubyte * 11
    control_buf_out = buf()
    usbTimeout = 500

    error_code = libusb1.libusb_control_transfer(handle, 0xC0, 0x30, 0x0000, 0x0000, control_buf_out, sizeof(control_buf_out), usbTimeout)
    if error_code != sizeof(control_buf_out):
        print('Error in bulk transfer')
        return False
    
    return control_buf_out




context = libusb1.libusb_context_p()	
deviceList = libusb1.libusb_device_p_p()
deviceCount = 0
deviceDescriptor = libusb1.libusb_device_descriptor()
device = libusb1.libusb_device_p()
cp2130Handle = libusb1.libusb_device_handle_p()
kernelAttached = 0
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

print("Connected")

#set high-priority read
cp2130_libusb_set_usb_config(cp2130Handle)

#get channel configurations for all channels
spi_word = cp2130_libusb_get_spi_word(cp2130Handle)
for i in range(11):
	byte = spi_word[i]
	bytevalue=ctypes.c_ubyte(byte).value
	print(bytevalue)
	#print(byte)

#set spi configuration for CH1
ch_number = 1
spi_word_0 = 8 #PHA=0, POL=0, CS MODE=PUSH-PULL, SCK F=12 MHz
cp2130_libusb_set_spi_word(cp2130Handle,ch_number,spi_word_0)

#SET GPIO1 as CS
gpio_cs=1
set_gpio_chip_select(cp2130Handle,gpio_cs,1)

#set GPIO2 as input 
#gpio_dataready=3
#gpio_mode = 1
#gpio_level = 0
#set_gpio_mode_and_level(cp2130Handle,gpio_dataready,gpio_mode,gpio_level)

#set GPI07 as output 
gpio_number=7
gpio_mode = 2
gpio_level = 0
set_gpio_mode_and_level(cp2130Handle,gpio_number,gpio_mode,gpio_level)


bytesnum = 200
'''
while 1:
	start=time.time()
	read_bytes = cp2130_libusb_read(cp2130Handle, bytesnum)
	read_bytes = cp2130_libusb_read(cp2130Handle, bytesnum)
	end = time.time()
	print(end-start)
	time.sleep(0.01)
#read_bytes = cp2130_libusb_read(cp2130Handle, bytesnum)

'''
released = libusb1.libusb_release_interface(cp2130Handle, 0)
if released:
	print('Not released successfully')
