import os

LONG_LINE = '=' * 100
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

API_HOST = 'localhost'
API_PORT = '3007'

API_PREFIX = '/api'
CURRENT_API_VERSION = 'v1'
API_VERSION_PREFIX = os.path.join(API_PREFIX, CURRENT_API_VERSION)

SKALE_NETWORK_TYPE = os.environ.get('SKALE_NETWORK_TYPE', 'skale')
PASSIVE_NODE = os.getenv('PASSIVE_NODE') == 'True'


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
        'schains': get_api_url('health', 'schains'),
        'ima': get_api_url('health', 'ima'),
        'schain-containers-versions': get_api_url('schains', 'container-versions'),
        'public-ip': get_api_url('node', 'public-ip'),
    },
    'fair': {
        'chain-checks': get_api_url('fair-chain', 'checks'),
        'chain-record': get_api_url('fair-chain', 'record'),
    },
}

if not PASSIVE_NODE:
    HEALTHCHECK_ROUTES['common']['sgx'] = get_api_url('info', 'sgx')

API_TIMEOUT = 1000  # in seconds
DEFAULT_TASK_INTERVAL = 60
SIGNAL_OFFSET = 20
DISABLE_BACKGROUND = bool(os.getenv('DISABLE_BACKGROUND') or False)

ENV = os.getenv('ENV')
ENDPOINT = os.getenv('ENDPOINT')
SGX_SERVER_URL = os.getenv('SGX_SERVER_URL')
