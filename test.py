from machine import I2C, Pin
import time

class PCA9685:
  def __init__(self, i2c, address=0x40):
    self.i2c = i2c
    self.address = address
    self.reset()

  def reset(self):
    self.write_reg(0x00, 0x00)  # MODE1: reset

  def write_reg(self, reg, value):
    self.i2c.writeto_mem(self.address, reg, bytes([value]))

  def read_reg(self, reg):
    return self.i2c.readfrom_mem(self.address, reg, 1)[0]

  def set_pwm_freq(self, freq_hz):
    prescale_val = int(25000000.0 / (4096 * freq_hz) - 1)
    old_mode = self.read_reg(0x00)
    new_mode = (old_mode & 0x7F) | 0x10  # sleep
    self.write_reg(0x00, new_mode)
    self.write_reg(0xFE, prescale_val)   # prescale
    self.write_reg(0x00, old_mode)
    time.sleep_ms(5)
    self.write_reg(0x00, old_mode | 0xa1)  # auto increment

  def set_pwm(self, channel, on, off):
    self.write_reg(0x06 + 4 * channel, on & 0xFF)
    self.write_reg(0x07 + 4 * channel, on >> 8)
    self.write_reg(0x08 + 4 * channel, off & 0xFF)
    self.write_reg(0x09 + 4 * channel, off >> 8)

  def set_servo_angle(self, channel, angle):
    # Calcola duty per angolo (servo standard ~0.5-2.5ms)
    min_pulse = 150  # corrisponde a ~0.5ms
    max_pulse = 600  # corrisponde a ~2.5ms
    pulse = int(min_pulse + (angle / 180.0) * (max_pulse - min_pulse))
    self.set_pwm(channel, 0, pulse)

i2c = I2C(0, scl=Pin(2), sda=Pin(1))

pca = PCA9685(i2c)
pca.set_pwm_freq(50)


while True:
  pca.set_servo_angle(4, 0)
  time.sleep(2)
  pca.set_servo_angle(4, 180)
  time.sleep(2)
  