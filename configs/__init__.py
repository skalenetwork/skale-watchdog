import os


LONG_LINE = '=' * 100
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

API_HOST = 'api'
API_PORT = '3007'

API_PREFIX = 'api'
CURRENT_API_VERSION = 'v1'
API_VERSION_PREFIX = os.path.join(API_PREFIX, CURRENT_API_VERSION)


def get_api_url(group_name, method_name):
    return os.path.join(API_VERSION_PREFIX, group_name, method_name)


HEALTHCHECKS_ROUTES = {
    'containers': get_api_url('health', 'containers?all=True'),
    'sgx': get_api_url('health', 'sgx'),
    'schains': get_api_url('health', 'schains'),
    'ima': get_api_url('health', 'ima'),
    'hardware': get_api_url('node', 'hardware'),
    'endpoint': get_api_url('node', 'endpoint-info'),
    'meta': get_api_url('node', 'meta-info'),
    'schain_versions': get_api_url('schains', 'container-versions'),
    'btrfs': get_api_url('node', 'btrfs-info'),
    'ssl': get_api_url('ssl', 'status'),
    'public-ip': get_api_url('node', 'public-ip'),
    'validator-nodes': get_api_url('node', 'validator-nodes'),
    'check-report': get_api_url('health', 'check-report')
}

API_TIMEOUT = 1000  # in seconds
DEFAULT_TASK_INTERVAL = 60
SIGNAL_OFFSET = 20
DISABLE_BACKGROUND = bool(os.getenv('DISABLE_BACKGROUND') or False)

ENV = os.getenv('ENV')
