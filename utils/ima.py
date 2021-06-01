from websocket import create_connection
import json
from datetime import datetime
import os
from configs import SCHAINS_DIR_PATH, SCHAINS_PREFIX


def request_ima_healthcheck(endpoint):
    ws = create_connection(endpoint, timeout=5)
    ws.send('{ "id": 1, "method": "get_last_transfer_errors"}')
    result = ws.recv()
    print("Received '%s'" % result)
    print(type(result))
    errs_json = json.loads(result)
    errs = errs_json['last_transfer_errors']
    print(f'Num = {len(errs)} >>> ERS={errs}')
    for err in errs:
        print(datetime.utcfromtimestamp(err['ts']))
    ws.close()
    return errs


def get_schain_config(schain_name):
    config_filepath = get_schain_config_filepath(schain_name)
    print(config_filepath)
    if os.path.exists(config_filepath):
        with open(config_filepath) as f:
            schain_config = json.load(f)
        return schain_config
    else:
        return None


def get_schain_config_filepath(schain_name):
    return os.path.join(SCHAINS_DIR_PATH, schain_name, get_schain_config_file_name(schain_name))


def get_ima_monitoring_port(schain_name):
    schain_config = get_schain_config(schain_name)
    if schain_config:
        node_info = schain_config["skaleConfig"]["nodeInfo"]
        return int(node_info["imaMonitoringPort"])
    else:
        return None


def get_schain_config_file_name(schain_name):
    return f'{SCHAINS_PREFIX}{schain_name}.json'


def get_ima_healthchecks():
    ima_healthchecks = []
    for schain_name in os.listdir(SCHAINS_DIR_PATH):
        print(schain_name)
        port = get_ima_monitoring_port(schain_name)
        if port:
            endpoint = f'ws://localhost:{port}'
            ima_health_check = request_ima_healthcheck(endpoint)
            ima_healthchecks.append({schain_name: ima_health_check})
    print(f'healthchecks = {ima_healthchecks}')

    return ima_healthchecks


get_ima_healthchecks()


# def get_ima_healthchecks():
#     ima_healthchecks = []
#     endpoints = get_ima_enpoints()
#     for endpoint in endpoints:
#         ima_err = request_ima_healthcheck(endpoint)
#         ima_healthchecks.append()
#     # endpoint = 'ws://192.168.2.38:13000'
#
#     print(f'IMA ERRORS: {ima_errs}')
#     print('THE END')



