import json
import logging
import os

from websocket import create_connection

from configs import HEALTHCHECKS_ROUTES, SCHAINS_DIR_PATH, SCHAINS_PREFIX
from utils.healthchecks import request_healthcheck_from_skale_api
from utils.structures import construct_ok_response

logger = logging.getLogger(__name__)


def request_ima_healthcheck(endpoint):
    ws = None
    try:
        ws = create_connection(endpoint, timeout=5)
        ws.send('{ "id": 1, "method": "get_last_transfer_errors"}')
        result = ws.recv()
    finally:
        if ws and ws.connected:
            ws.close()
    logger.debug(f'Received {result}')
    errs_json = json.loads(result)
    errs = errs_json['last_transfer_errors']
    return errs


def get_schain_config(schain_name):
    config_filepath = get_schain_config_filepath(schain_name)
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


def get_ima_containers():
    response = request_healthcheck_from_skale_api(HEALTHCHECKS_ROUTES['containers'])
    containers = response.data['data']
    ima_containers = [{container['name']: container['state']['Status']} for container in containers]
    return ima_containers


def get_ima_healthchecks():
    ima_containers = get_ima_containers()
    ima_healthchecks = []
    for schain_name in os.listdir(SCHAINS_DIR_PATH):
        error_text = None
        ima_healthcheck = []
        container_name = f'skale_ima_{schain_name}'

        cont_data = next((item for item in ima_containers if item["name"] == container_name), None)
        if cont_data is None:
            continue
        elif cont_data['state'] != 'running':
            error_text = 'IMA docker container is not running'
        else:
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
                    logger.info(f'Error occurred while checking IMA state on {endpoint}')
                    logger.exception(err)
                    error_text = repr(err)
        ima_healthchecks.append({schain_name: {'error': error_text,
                                               'last_ima_errors': ima_healthcheck}})
    return construct_ok_response(ima_healthchecks)
