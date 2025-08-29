# SKALE Watchdog Client

[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

Minimal Python client for interacting with SKALE Watchdog node APIs (SKALE + FAIR).

## Install

```bash
pip install skale-watchdog-client
```

Supports Python 3.11+.

## Quick Start

```python
from watchdog_client import SkaleNode, FairNode, FairPassiveNode

# Base URL can be domain name or IP address of the node.
skale_node = SkaleNode('my-skale-node.example.com')
fair_node = FairNode('23.56.24.61')
# Use FairPassiveNode for FAIR nodes running in passive mode (no SGX endpoint)
fair_passive = FairPassiveNode('23.56.24.62')

# Call any endpoint – each returns ApiResult (fields: data, error, status_code)
r = skale_node.public_ip()
if r:
	print('Public IP:', r.data)
else:
	print('Error:', r.error)

# Execute every available check on a node
results = skale_node.all_checks()
for name, res in results.items():
	print(name, 'OK' if res else f'ERR: {res.error}')
```

## API

### Common (available on both SkaleNode and FairNode)

* containers
* sgx (not available on FAIR passive nodes; see FairPassiveNode)
* hardware
* endpoint
* meta\_info (maps to /meta-info)
* btrfs
* ssl
* check\_report (maps to /check-report)

### SKALE-specific (`SkaleNode`)

* schains
* ima
* schain\_containers\_versions (maps to /schain-containers-versions)
* public\_ip (maps to /public-ip)
* validator\_nodes (maps to /validator-nodes)
* sm\_abi\_hash (maps to /sm-abi)
* ima\_abi\_hash (maps to /ima-abi)

### FAIR-specific (`FairNode`)

* chain\_checks (maps to /chain-checks)
* chain\_record (maps to /chain-record)

### FAIR Passive (`FairPassiveNode`)

Same as `FairNode`, except:

* sgx — returns an error ApiResult: "SGX check is not available on FAIR passive nodes"

### Batch execution

Call `all_checks()` on any node instance to execute each public check method (no params) and get a dict mapping method name to its ApiResult. One failing check does not stop others.

## Result Object

```python
res = fair.chain_checks()
if res:
	print(res.data)
else:
	raise RuntimeError(res.error)
```

### License

![GitHub](https://img.shields.io/github/license/skalenetwork/skale-watchdog.svg)

All contributions are made under the [GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.en.html). See [LICENSE](LICENSE).
