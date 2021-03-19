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
    'schain_containers_versions': 'schain-containers-versions',
    'meta_info': 'meta-info'
}

API_CONT_HEALTH_URL = 'healthchecks/containers'
API_SGX_HEALTH_URL = 'api/sgx/info'
API_SCHAINS_HEALTH_URL = 'api/schains/healthchecks'
API_HARDWARE_INFO_URL = 'hardware'
API_ENDPOINT_INFO_URL = 'endpoint-info'
API_SCHAIN_CONTAINERS_VERSIONS_URL = 'schain-containers-versions'
API_META_INFO_URL = 'meta-info'

API_TIMEOUT = 1000  # in seconds
