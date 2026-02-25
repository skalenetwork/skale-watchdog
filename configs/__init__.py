import os
from pathlib import Path

from skale_core.settings import (
    FairBaseSettings,
    FairSettings,
    InternalSettings,
    SkalePassiveSettings,
    SkaleSettings,
    get_internal_settings,
    get_settings,
)

LONG_LINE = '=' * 100
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

API_HOST = 'localhost'
API_PORT = '3007'

API_PREFIX = '/api'
CURRENT_API_VERSION = 'v1'
API_VERSION_PREFIX = os.path.join(API_PREFIX, CURRENT_API_VERSION)


SETTINGS_FOLDER_PATH = Path(os.getenv('SETTINGS_FOLDER_PATH', '/settings'))
NODE_SETTINGS_PATH: Path = SETTINGS_FOLDER_PATH / 'node.toml'
INTERNAL_SETTINGS_PATH: Path = SETTINGS_FOLDER_PATH / 'internal.toml'

InternalSettings.model_config['toml_file'] = INTERNAL_SETTINGS_PATH
SkaleSettings.model_config['toml_file'] = NODE_SETTINGS_PATH
SkalePassiveSettings.model_config['toml_file'] = NODE_SETTINGS_PATH
FairSettings.model_config['toml_file'] = NODE_SETTINGS_PATH
FairBaseSettings.model_config['toml_file'] = NODE_SETTINGS_PATH

INTERNAL_ST = get_internal_settings()
ST = get_settings()


def get_api_url(blueprint_name, method_name):
    return os.path.join(API_VERSION_PREFIX, blueprint_name, method_name)


HEALTHCHECK_ROUTES = {
    'common': {
        'hardware': get_api_url('info', 'hardware'),
        'meta-info': get_api_url('info', 'meta-info'),
        'btrfs': get_api_url('info', 'btrfs-info'),
        'check-report': get_api_url('info', 'check-report'),
        'endpoint': get_api_url('info', 'endpoint-info'),
        'containers': get_api_url('info', 'containers?all=True'),
        'ssl': get_api_url('ssl', 'status'),
    },
    'skale': {
        'schain-containers-versions': get_api_url('schains', 'container-versions'),
        'public-ip': get_api_url('node', 'public-ip'),
    },
    'fair': {
        'chain-checks': get_api_url('fair-chain', 'checks'),
        'chain-record': get_api_url('fair-chain', 'record'),
    },
}

if not INTERNAL_ST.node_mode == 'passive':
    HEALTHCHECK_ROUTES['common']['sgx'] = get_api_url('info', 'sgx')
    HEALTHCHECK_ROUTES['skale']['schains'] = get_api_url('health', 'schains')
    HEALTHCHECK_ROUTES['skale']['ima'] = get_api_url('health', 'ima')
    HEALTHCHECK_ROUTES['skale']['validator-nodes'] = get_api_url('node', 'validator-nodes')


API_TIMEOUT = int(os.getenv('API_TIMEOUT', '1000'))
DEFAULT_TASK_INTERVAL = int(os.getenv('DEFAULT_TASK_INTERVAL', '180'))
SIGNAL_OFFSET = int(os.getenv('SIGNAL_OFFSET', '20'))
