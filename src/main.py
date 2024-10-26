import array
import asyncio
import gc
from time import time_ns

from library.web_server import MicroPyServer
from library import mpu6050

acc_record_limit = 800
acc_loop_time = 0.1

accel_lock = asyncio.Lock()
accel_sensor_data = array.array('i', (0 for _ in range(acc_record_limit)))
accel_time_data = array.array('I', (0 for _ in range(acc_record_limit)))


async def read_acc_data():
    motion = mpu6050.MPU6050()

    print('start measurements')
    while True:
        gc.collect()
        for i in range(acc_record_limit):
            curr_time = time_ns()  # example 184007058000
            accel = motion.read_accel_data()  # read the accelerometer [ms^-2]. example = 9.97663, 9.97663, 9.97663

            a_x = accel["x"]
            a_y = accel["y"]
            a_z = accel["z"]
            async with accel_lock:
                accel_sensor_data[i] = int((a_x + a_y + a_z) * 10 ** 5)
                accel_time_data[i] = curr_time

            await asyncio.sleep(acc_loop_time)


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

    async with accel_lock:
        server.write_http_response(stream=stream, response_generator=_acc_data_generator, http_code=200)

    return None


async def stats(request: str, server: MicroPyServer, stream: asyncio.StreamWriter):
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F + A
    P = '{0:.2f}%'.format(F / T * 100)
    return 'Total:{0} Free:{1} ({2})'.format(T, F, P)


async def main():
    server = MicroPyServer()

    server.add_route("/dump", dump)
    server.add_route("/stats", stats)

    await server.start_server()

    asyncio.create_task(read_acc_data())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    loop.run_until_complete(main())

    loop.run_forever()
