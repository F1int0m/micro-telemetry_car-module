from time import sleep_ms

from library.mpu6050 import MPU6050

mpu = MPU6050()

x_acc = 0
y_acc = 0
z_acc = 0

iterate = 0

while True:
    iterate += 1
    accel = mpu.read_accel_data()
    aX = accel['x']
    aY = accel['y']
    aZ = accel['z']
    print('x: ' + str(aX) + ' y: ' + str(aY) + ' z: ' + str(aZ))

    x_acc += aX
    y_acc += aY
    z_acc += aZ

    x_error = x_acc / iterate
    y_error = y_acc / iterate
    z_error = z_acc / iterate

    print(f'{x_error=}; {y_error=}; {z_error=}; ')

    sleep_ms(100)
