import array
import asyncio
import gc
from time import time_ns

from library import mpu6050
from library.web_server import MicroPyServer

acc_record_limit = 800
acc_loop_time = 0.1
acc_idle_threshold = 0.2
acc_idle_axis_threshold = 0.2

accel_data_lock = asyncio.Lock()
accel_access_lock = asyncio.Lock()
accel_sensor_data = array.array('i', (0 for _ in range(acc_record_limit)))
accel_time_data = array.array('I', (0 for _ in range(acc_record_limit)))

mpu = mpu6050.MPU6050()


async def read_acc_data():
    print('Wait for start mpu')
    await asyncio.sleep(3)

    mpu.auto_calibrate()

    accel = mpu.read_accel_data()

    old_a_x = accel['x']
    old_a_y = accel['y']
    old_a_z = accel['z']

    print('start measurements')
    while True:
        gc.collect()
        for i in range(acc_record_limit):
            curr_time = time_ns()  # example 184007058000
            # read the accelerometer [ms^-2]. example = 9.97663, 9.97663, 9.97663
            async with accel_access_lock:
                accel = mpu.read_accel_data()
                accel_abs = mpu.read_accel_abs()

            a_x = accel['x']
            a_y = accel['y']
            a_z = accel['z']

            print(f'{a_x=} {a_y=} {a_z=}')

            async with accel_data_lock:
                accel_sensor_data[i] = int((a_x + a_y + a_z) * 10 ** 5)
                accel_time_data[i] = curr_time

            if i % 10 == 0:
                print(f'check idle {a_x=} {a_y=} {a_z=} ; {old_a_x=} {old_a_y=} {old_a_z=} ; {accel_abs=}')

                if accel_abs < acc_idle_threshold:

                    if abs(old_a_x - a_x) < acc_idle_axis_threshold:
                        mpu.accel_x_error += a_x

                    if abs(old_a_y - a_y) < acc_idle_axis_threshold:
                        mpu.accel_y_error += a_y

                    if abs(old_a_z - a_z) < acc_idle_axis_threshold:
                        mpu.accel_z_error += a_z

                    old_a_x = a_x
                    old_a_y = a_y
                    old_a_z = a_z
                else:
                    print('not idle')

            await asyncio.sleep(acc_loop_time)


async def calibrate(request: str, server: MicroPyServer, stream: asyncio.StreamWriter):
    print('Go to realtime calibration')

    async with accel_access_lock:
        mpu.auto_calibrate()

    return 'OK'


async def dump(request: str, server: MicroPyServer, stream: asyncio.StreamWriter):
    def _acc_data_generator():
        """Array to json as generator"""
        yield '['
        for i in range(acc_record_limit):
            result = f'[{accel_time_data[i]},{accel_sensor_data[i]}]'
            if i < acc_record_limit - 1:
                result += ','

            yield result
        yield ']'

    async with accel_data_lock:
        server.write_http_response(
            stream=stream, response_generator=_acc_data_generator, http_code=200
        )

    return None


async def stats(request: str, server: MicroPyServer, stream: asyncio.StreamWriter):
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F + A
    P = '{0:.2f}%'.format(F / T * 100)
    return 'Total:{0} Free:{1} ({2})'.format(T, F, P)


async def main():
    server = MicroPyServer()

    server.add_route('/dump', dump)
    server.add_route('/stats', stats)
    server.add_route('/calibrate', calibrate)

    await server.start_server()

    asyncio.create_task(read_acc_data())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    loop.run_until_complete(main())

    loop.run_forever()
