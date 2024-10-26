from time import sleep_ms

from library.mpu6050 import MPU6050

mpu = MPU6050()

x_acc = 0
y_acc = 0
z_acc = 0

while True:
    accel = mpu.read_accel_data()
    aX = accel['x']
    aY = accel['y']
    aZ = accel['z']

    sleep_ms(100)
