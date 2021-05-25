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
    'meta': 'meta-info',
    'btrfs': 'btrfs-info',
    'ssl': 'api/ssl/status',
    'public_ip': '/api/v1/node/public-ip'
}

API_TIMEOUT = 1000  # in seconds

JOB_INTERVAL = int(os.getenv('JOB_INTERVAL', 480))

CRON_SCHEDULE = [
    -(JOB_INTERVAL // 60),
    -1,
    -1,
    -1,
    -1
]  # Every 8 minutes by default

ENV = os.getenv('ENV')
