from time import sleep

import network
import ntptime

import config

network_server = network.WLAN(network.AP_IF)
network_client = network.WLAN(network.STA_IF)

network_server.active(False)
network_client.active(False)

if config.AP_MODE:
    network_server.active(True)
    print('Start as wifi server')
    host_ip = network_server.ifconfig()[0]
    network_server.config(ssid=config.AP_NAME + host_ip, password=config.AP_PASSWORD)


else:

    network_client.active(True)
    print('Start as wifi client')

    network_client.connect(config.NETWORK_NAME, config.NETWORK_PASSWORD)

    while not network_client.isconnected():
        pass

    print('sync time on start')
    for _ in range(60):
        try:
            ntptime.settime()
            break
        except Exception as exc:
            print(f'Error in time sync {str(exc)}')
            sleep(1)
    else:
        print('time not synced')

    board_config = network_client.ifconfig()

    print(f'Connected. {board_config}=')
