from machine import I2C, Pin
import time
import math

# Classe di gestione PCA9685
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

# configurazioni cinematica inversa
L1 = 5.46
L2 = 7

STEP_HEIGHT = 2.0
CIRCLE_OFFSET = 2

def reachable(x, y):
  r = math.sqrt(x*x + y*y)
  return (abs(L1 - L2) <= r <= (L1 + L2))

def ik(x, y, z, elbow_sign=+1):
  # distanza radiale orizzontale
  R = math.sqrt(x**2 + y**2)
  r2 = R*R + z*z                # distanza^2 nel piano della spalla
  # law of cosines per c2
  denom = 2.0 * L1 * L2
  c2 = (r2 - L1*L1 - L2*L2) / denom
  if c2 < -1.0 or c2 > 1.0:
    return None  # fuori portata

  s2 = elbow_sign * math.sqrt(max(0.0, 1.0 - c2*c2))
  theta3 = math.atan2(s2, c2)   # angolo dell'articolazione "elbow"

  # Kahan-style shoulder angle (stabile numericamente)
  k1 = L1 + L2 * c2
  k2 = L2 * s2
  theta2 = math.atan2(z, R) - math.atan2(k2, k1)

  # base angle: uso atan2(x, y) per mantenere la tua convenzione dove 0° è sull'asse Y
  theta1 = math.atan2(x, y)

  return (math.degrees(theta1), math.degrees(theta2), math.degrees(theta3))


def map_joint_to_servo_ik(joint_deg, home_deg, direction, min_deg, max_deg):
  servo = 90.0 + direction * (joint_deg - home_deg)
  return max(min_deg, min(max_deg, servo))

def map_joint_to_servo(joint_deg, home_deg, direction, min_deg, max_deg):
  servo = direction * (joint_deg - home_deg)
  return max(min_deg, min(max_deg, servo))

# Parametri
cal = [
  {},  # zampa 0
  {  # zampa 1
    "base":   dict(home_deg=1.0,   direction=-1, min_deg=45.0, max_deg=135.0),
    "should": dict(home_deg=-5.0,   direction=-1, min_deg=0.0, max_deg=180.0),
    "elbow":  dict(home_deg=58.0,   direction=+1, min_deg=0.0, max_deg=180.0),
  },
  {  # zampa 2
    "base":   dict(home_deg=7.0,   direction=-1, min_deg=45.0, max_deg=135.0),
    "should": dict(home_deg=0.0,   direction=-1, min_deg=0.0, max_deg=180.0),
    "elbow":  dict(home_deg=62.0,   direction=+1, min_deg=0.0, max_deg=180.0),
  },
  {  # zampa 3
    "base":   dict(home_deg=10.0,   direction=-1, min_deg=45.0, max_deg=135.0),
    "should": dict(home_deg=0.0,   direction=-1, min_deg=0.0, max_deg=180.0),
    "elbow":  dict(home_deg=60.0,   direction=+1, min_deg=0.0, max_deg=180.0),
  },
  {  # zampa 4
    "base":   dict(home_deg=5.0,   direction=-1, min_deg=45.0, max_deg=135.0),
    "should": dict(home_deg=0.0,   direction=-1, min_deg=0.0, max_deg=180.0),
    "elbow":  dict(home_deg=62.0,   direction=+1, min_deg=0.0, max_deg=180.0),
  },
  {  # zampa 5
    "base":   dict(home_deg=-5.0,   direction=-1, min_deg=45.0, max_deg=135.0),
    "should": dict(home_deg=0.0,   direction=-1, min_deg=0.0, max_deg=180.0),
    "elbow":  dict(home_deg=70.0,   direction=+1, min_deg=0.0, max_deg=180.0),
  }
]

servo_pins = [
  [-1, -1, -1], # 0
  [1, 2, 3], # 1
  [4, 5, 6], # 2
  [13, 14, 15], # 3
  [10, 11, 12], # 4
  [7, 8, 9],  # 5
]

def set_angles(leg_id, t1, t2, t3):
  pca.set_servo_angle(servo_pins[leg_id][0], t1)
  pca.set_servo_angle(servo_pins[leg_id][1], t2)
  pca.set_servo_angle(servo_pins[leg_id][2], t3)

def angles_to_servo(leg_id, t1, t2, t3):
  s1 = map_joint_to_servo(t1, cal[leg_id]["base"]["home_deg"],   cal[leg_id]["base"]["direction"],   cal[leg_id]["base"]["min_deg"],   cal[leg_id]["base"]["max_deg"])
  s2 = map_joint_to_servo(t2, cal[leg_id]["should"]["home_deg"], cal[leg_id]["should"]["direction"], cal[leg_id]["should"]["min_deg"], cal[leg_id]["should"]["max_deg"])
  s3 = map_joint_to_servo(t3, cal[leg_id]["elbow"]["home_deg"],  cal[leg_id]["elbow"]["direction"],  cal[leg_id]["elbow"]["min_deg"],  cal[leg_id]["elbow"]["max_deg"])
  return (s1, s2, s3)

def ik_to_servo(x, y, z, leg_id):
  res = ik(x, y, z)
  if not res:
    return None
  t1, t2, t3 = res
  
  s1 = map_joint_to_servo_ik(t1, cal[leg_id]["base"]["home_deg"],   cal[leg_id]["base"]["direction"],   cal[leg_id]["base"]["min_deg"],   cal[leg_id]["base"]["max_deg"])
  s2 = map_joint_to_servo_ik(t2, cal[leg_id]["should"]["home_deg"], cal[leg_id]["should"]["direction"], cal[leg_id]["should"]["min_deg"], cal[leg_id]["should"]["max_deg"])
  s3 = map_joint_to_servo_ik(t3, cal[leg_id]["elbow"]["home_deg"],  cal[leg_id]["elbow"]["direction"],  cal[leg_id]["elbow"]["min_deg"],  cal[leg_id]["elbow"]["max_deg"])
  
  return (s1, s2, s3)  # angoli servo [°]

def angle_to_cartesian(angle):
  """
  Converte un angolo in coordinate cartesiane sul cerchio unitario.
  """
  angle = math.radians(angle)  # converte in radianti
  
  return (math.cos(angle), math.sin(angle))

def lerp2d(p1, p2, t):
  """
  Linear interpolation tra due punti 2D.
  """
  x = p1[0] + (p2[0] - p1[0]) * t
  y = p1[1] + (p2[1] - p1[1]) * t
  return (x, y)

def lerp3d(p1, p2, t):
  """
  Linear interpolation tra due punti 3D.
  """
  x = p1[0] + (p2[0] - p1[0]) * t
  y = p1[1] + (p2[1] - p1[1]) * t
  z = p1[2] + (p2[2] - p1[2]) * t
  return (x, y, z)

def arch_curve(t):
  """
  Genera una curva ad arco (0→0, 0.5→1, 1→0).
  
  :param t: Valore normalizzato [0, 1]
  :return: Valore dell'arco [0, 1]
  """
  return math.sin(math.pi * t)

def step(direction, height, diameter, t):
  starting_point = angle_to_cartesian(direction)
  ending_point = angle_to_cartesian(direction+180)
  
  starting_point = (starting_point[0] * diameter, starting_point[1] * diameter + diameter + CIRCLE_OFFSET)
  ending_point = (ending_point[0] * diameter, ending_point[1] * diameter + diameter + CIRCLE_OFFSET)
  
  if t <= 0.5:
    result = lerp2d(starting_point, ending_point, t*2)
  else:
    result = lerp2d(ending_point, starting_point, (t-0.5)*2)
    if t < 0.75:
      height -= arch_curve((t-0.5) * 2) * STEP_HEIGHT
    else:
      height = STEP_HEIGHT
    print("height: ", height)
  return result[0], result[1], height

def go_to_position(x, y, z, leg_id):
  if x == 0: x = 0.0001
  if y == 0: y = 0.0001
  if z == 0: z = 0.0001
  
  angles = ik_to_servo(x, y, z, leg_id)
  if angles is not None:
    set_angles(leg_id, *angles)


channel_1, channel_2 = 50, 0

while True:
  # go_to_position(*step(180, 4, 2, channel_1/100), 1)
  # go_to_position(*step(225, 4, 2, channel_2/100), 2)
  # go_to_position(*step(315, 4, 2, channel_1/100), 3)
  # go_to_position(*step(0, 4, 2, channel_2/100), 4)
  # go_to_position(*step(45, 4, 2, channel_1/100), 5)
  
  # channel_1 += 1
  # channel_2 += 1
  # channel_1 %= 100
  # channel_2 %= 100
  
  # go_to_position(0, 4, -6, 1)
  # go_to_position(0, 4, -6, 2)
  # go_to_position(0, 4, -6, 3)
  # go_to_position(0, 4, -6, 4)
  # go_to_position(0, 4, -6, 5)
  
  for i in range(15, 100):
    point = lerp3d((0, 4, 0), (0, 4, 6), i/100)
    go_to_position(*point, 1)
    go_to_position(*point, 2)
    go_to_position(*point, 3)
    go_to_position(*point, 4)
    go_to_position(*point, 5)
    time.sleep(0.01)
  
  for i in range(100, 15, -1):
    point = lerp3d((0, 4, 0), (0, 4, 6), i/100)
    go_to_position(*point, 1)
    go_to_position(*point, 2)
    go_to_position(*point, 3)
    go_to_position(*point, 4)
    go_to_position(*point, 5)
    time.sleep(0.01)
  
  # while True: pass