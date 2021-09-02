import cp2130
from cp2130.data import *

# If the vendor or product ids are not the default, use
# the form cp2130.find(vid=0xXXXX, pid=0xXXXX).
chip = cp2130.find() 

#######################################################
# SPI Reads/Writes
#######################################################
slave = chip.channel0

# Print a summary of the channel state
print(slave)

# Write 4 bytes of data to the slave
command = b'\x01\x02\x03\0x04'
slave.write(command)

# Read 8 bytes of data
response = slave.read(8)

# Issue a two-part transaction
part1 = b'\x01\x02'
part2 = b'\x03\x04'
slave.write(part1, cs_hold=True) # Keeps CS asserted
slave.write(part2)

# NOTE: cs_hold is not supported by the CP2130 native chip-select 
# capabilities. To use cs_hold, configure the chip select line as
# a GPIO instead of a chip select. This library will then manually
# manage the chip select state. I.e,:
#   chip.pin_config.gpio0.function = OutputMode.PUSH_PULL # or OutputMode.OPEN_DRAIN
# instead of
#   chip.pin_config.gpio0.function = GPIO0Mode.CS0_n

#######################################################
# GPIO Reads/Writes
#######################################################
signal = chip.gpio0

# Print a summary of the GPIO state
print(signal)

# Get the logic state of the pin
level = signal.value

# Set the logic state of the pin
signal.value = LogicLevel.LOW

#######################################################
# GPIO Configuration
#######################################################
# Set the mode of a GPIO
signal.mode = OutputMode.PUSH_PULL

#######################################################
# Clock Configuration
#######################################################
clock = chip.clock

# Print the clock state
print(clock)

# Set the clock frequency
# Use clock.divider to set the divider register directly
clock.frequency = 6 * 1000 * 1000 # 6 MHz

#######################################################
# Event Counter
#######################################################
counter = chip.event_counter

# Print a summary of the counter state 
print(counter)

# Get count
count = counter.count
(count, overflowed) = counter.count_with_overflow

# Set the count
counter.count = 10

# Configure the counter
counter.mode = EventCounterMode.NEGATIVE_PULSE

#######################################################
# OTP ROM Lock Byte
#######################################################
lock = c.lock

# Print a summary of the lock
print (lock)

# Lock the USB vendor ID
lock.vid = LockState.LOCKED

#######################################################
# OTP ROM USB Configuration
#######################################################
usb = c.usb

# Print a summary of the USB configuration
print(usb)

# Set the product string
usb.product_string = "ACME Widget"
c.usb = usb
print(lock)  # The product_string field is now locked

# Set the power mode
usb.power_mode = PowerMode.BUS_AND_REGULATOR_ON
c.usb = usb
print(lock)  # The power_mode field is now locked

#######################################################
# OTP ROM Pin Configuration
#######################################################
pins = c.pin_config

# Print a summary of the PIN configuration
print(pins)

# Print a summary of the config for one pin
print(pins.gpio1)
print(pins.vpp)

# Print the clock configuration
print(pins.clock)

# NOTE: The entire pin configuration must be set at one
# time.  The following example modifies several of the pins and
# then commit the entire config to the OTP ROM at once.

# Set a pin function
pins.gpio1.function = OutputMode.PUSH_PULL

# Set a pin suspend logic level
pins.miso.suspend_level = LogicLevel.HIGH
pins.miso.suspend_mode  = OutputMode.OPEN_DRAIN

# Set a pin wakeup config
pins.vpp.wakeup_level = LogicLevel.LOW
pins.vpp.wakeup_mask  = True

# Set the initial clock freqeuency
pins.clock.frequency = 6 * 1000 * 1000 # 6 MHz

# Write the config to the ROM
c.pin_config = pins
print(lock) # The pin_config field is now locked