from websocket import create_connection, WebSocketException
import json
from datetime import datetime
import os
from configs import SCHAINS_DIR_PATH, SCHAINS_PREFIX
import logging
from utils.structures import construct_ok_response

logger = logging.getLogger(__name__)


def request_ima_healthcheck(endpoint):
    try:
        ws = create_connection(endpoint, timeout=5)
        ws.send('{ "id": 1, "method": "get_last_transfer_errors"}')
        result = ws.recv()
    except WebSocketException as err:
        logger.exception(err)
        return []
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
        error_text = None
        ima_healthcheck = []

        try:
            ima_port = get_ima_monitoring_port(schain_name)
        except KeyError as err:
            logger.exception(err)
            error_text = repr(err)
        else:
            if ima_port is None:
                continue
            endpoint = f'ws://localhost:{ima_port}'
            try:
                ima_healthcheck = request_ima_healthcheck(endpoint)
            except Exception as err:
                logger.exception(err)
                error_text = repr(err)
        ima_healthchecks.append({schain_name: {'error': error_text,
                                               'last_ima_errors': ima_healthcheck}})
    return construct_ok_response(ima_healthchecks)




