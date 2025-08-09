# skale-watchdog

[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

SKALE Watchdog microservice: exposes health/status info for SKALE/FAIR node components.

## REST API (current)

Base URL: http://\<NODE\_IP>:3009

All endpoints return JSON in format: {"data": <payload>|null, "error": \<string|null>}.

### Common group

```
GET /api/v1/common/hardware
GET /api/v1/common/meta-info
GET /api/v1/common/btrfs
GET /api/v1/common/sgx
GET /api/v1/common/check-report
GET /api/v1/common/endpoint
GET /api/v1/common/containers (query: all=True)
GET /api/v1/common/ssl
```

### SKALE network specific (SKALE\_NETWORK\_TYPE=skale)

```
GET /api/v1/skale/schains
GET /api/v1/skale/ima
GET /api/v1/skale/schain-containers-versions
GET /api/v1/skale/public-ip
GET /api/v1/skale/validator-nodes
GET /api/v1/skale/sm-abi
GET /api/v1/skale/ima-abi
```

### Fair network specific (SKALE\_NETWORK\_TYPE=fair)

```
GET /api/v1/fair/chain-checks
```

Notes:

* Add header/body option {"\_no\_cache": true} (JSON) to force a cold fetch.
* Response time is logged; caching reduces latency.
* Non-200 upstream responses are wrapped with error message in "error" field.

### License

![GitHub](https://img.shields.io/github/license/skalenetwork/skale-watchdog.svg)

All contributions are made under the [GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.en.html). See [LICENSE](LICENSE).
