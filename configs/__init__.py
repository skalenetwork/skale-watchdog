import os


LONG_LINE = '=' * 100
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

API_HOST = 'localhost'
API_PORT = '3007'

HEALTHCHECKS_ROUTES = {
    'containers': 'healthchecks/containers',
    'sgx': 'api/sgx/info',
    'schains': 'api/schains/healthchecks',
    'hardware': 'hardware',
    'endpoint': 'endpoint-info',
    'schain_versions': 'schain-containers-versions',
    'meta': 'meta-info'
}

API_TIMEOUT = 1000  # in seconds

CRON_SCHEDULE = [-4, -1, -1, -1, -1]

ENV = os.getenv('ENV')
