import os

NODE_DATA_PATH = '/skale_node_data'
SCHAINS_DIR_NAME = 'schains'
SCHAINS_DIR_PATH = os.path.join(NODE_DATA_PATH, SCHAINS_DIR_NAME)
SCHAINS_PREFIX = 'schain_'

LONG_LINE = '=' * 100
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

API_HOST = 'localhost'
API_PORT = '3007'

API_PREFIX = 'api'
CURRENT_API_VERSION = 'v1'
API_VERSION_PREFIX = os.path.join(API_PREFIX, CURRENT_API_VERSION)


def get_api_url(group_name, method_name):
    return os.path.join(API_VERSION_PREFIX, group_name, method_name)


HEALTHCHECKS_ROUTES = {
    'containers': get_api_url('health', 'containers'),
    'sgx': get_api_url('health', 'sgx'),
    'schains': get_api_url('health', 'schains'),
    'hardware': get_api_url('node', 'hardware'),
    'endpoint': get_api_url('node', 'endpoint-info'),
    'meta': get_api_url('node', 'meta-info'),
    'schain_versions': get_api_url('schains', 'container-versions'),
    'btrfs': get_api_url('node', 'btrfs'),
    'ssl': get_api_url('ssl', 'status')
}

API_TIMEOUT = 1000  # in seconds

CRON_SCHEDULE = [-4, -1, -1, -1, -1]  # Every 4 minutes

ENV = os.getenv('ENV')
