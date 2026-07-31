# skale-watchdog

[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

SKALE Watchdog microservice: exposes health/status info for SKALE/FAIR node components.

## REST API

Base URL: `http://<NODE_IP>:3009`

Watchdog proxies the corresponding SKALE Admin routes and wraps every response as:

```json
{
  "data": {},
  "error": null
}
```

On failure, `data` is `null`, `error` contains a message, and the response has a non-2xx HTTP status. The successful responses below are illustrative; values such as versions, addresses, container state, chain names, and check results depend on the node.

### Common endpoints

These endpoints are available on SKALE and FAIR nodes. The SGX endpoint is available only when the node is running in active mode.

#### `GET /api/v1/common/hardware`

```json
{
  "data": {
    "cpu_total_cores": 32,
    "cpu_physical_cores": 16,
    "memory": 67575316480,
    "swap": 8589930496,
    "mem_used": 21498781696,
    "mem_available": 46076534784,
    "system_release": "Linux-6.8.0-52-generic",
    "uname_version": "#53-Ubuntu SMP PREEMPT_DYNAMIC",
    "attached_storage_size": 2147483648000
  },
  "error": null
}
```

Memory and storage values are expressed in bytes.

#### `GET /api/v1/common/meta-info`

```json
{
  "data": {
    "version": "2.9.0",
    "config_stream": "2.9.0-stable.0",
    "docker_lvmpy_stream": "1.1.1"
  },
  "error": null
}
```

#### `GET /api/v1/common/btrfs`

```json
{
  "data": {
    "kernel_module": true
  },
  "error": null
}
```

#### `GET /api/v1/common/sgx`

Active nodes only. Watchdog removes the upstream `sgx_server_url` and `sgx_keyname` fields before returning the response.

```json
{
  "data": {
    "status_zmq": true,
    "status_https": true,
    "sgx_wallet_version": "1.9.0"
  },
  "error": null
}
```

#### `GET /api/v1/common/check-report`

The payload is the complete SKALE Admin check-report object. If no report file exists, it is empty:

```json
{
  "data": {},
  "error": null
}
```

#### `GET /api/v1/common/endpoint`

```json
{
  "data": {
    "block_number": 22438190,
    "trusted": true,
    "client": "Geth/v1.14.12-stable/linux-amd64/go1.23.3",
    "call_speed": 0.0384218692779541,
    "syncing": false
  },
  "error": null
}
```

`syncing` can be `true`, `false`, or `null` when the upstream sync check fails.

#### `GET /api/v1/common/containers`

Watchdog requests all containers from SKALE Admin, including stopped containers. The `state` value is Docker's container state object and may contain additional fields.

```json
{
  "data": [
    {
      "image": "skalenetwork/schain:3.19.0",
      "name": "sk_skaled_example-chain",
      "state": {
        "Status": "running",
        "Running": true,
        "Paused": false,
        "Restarting": false,
        "OOMKilled": false,
        "Dead": false,
        "Pid": 42117,
        "ExitCode": 0,
        "Error": "",
        "StartedAt": "2026-01-15T10:20:30.123456789Z",
        "FinishedAt": "0001-01-01T00:00:00Z"
      },
      "cpu_shares": 0,
      "mem_limit": 8589934592,
      "swap_limit": 8589934592,
      "swappiness": null
    }
  ],
  "error": null
}
```

#### `GET /api/v1/common/ssl`

With an installed certificate:

```json
{
  "data": {
    "issued_to": "node.example.com",
    "expiration_date": "2027-01-15T10:20:30"
  },
  "error": null
}
```

If the SSL certificate directory is empty, `data` is `{"is_empty": true}`.

### SKALE endpoints

The `schains`, `ima`, and `validator-nodes` endpoints are available only in active mode. The other endpoints are also available in passive mode.

#### `GET /api/v1/skale/schains`

```json
{
  "data": [
    {
      "name": "example-chain",
      "healthchecks": {
        "config_dir": true,
        "dkg": true,
        "config": true,
        "volume": true,
        "firewall_rules": true,
        "skaled_container": true,
        "exit_code_ok": true,
        "rpc": true,
        "blocks": true,
        "process": true,
        "ima_container": true
      }
    }
  ],
  "error": null
}
```

#### `GET /api/v1/skale/ima`

```json
{
  "data": [
    {
      "example-chain": {
        "error": null,
        "last_ima_errors": [],
        "error_categories": []
      }
    }
  ],
  "error": null
}
```

#### `GET /api/v1/skale/schain-containers-versions`

```json
{
  "data": {
    "skaled_version": "3.19.0",
    "ima_version": "3.22"
  },
  "error": null
}
```

#### `GET /api/v1/skale/public-ip`

```json
{
  "data": {
    "public_ip": "203.0.113.10"
  },
  "error": null
}
```

#### `GET /api/v1/skale/validator-nodes`

Each item contains the validator node ID, its IP address, and whether its Watchdog port is reachable.

```json
{
  "data": [
    [
      101,
      "203.0.113.11",
      true
    ],
    [
      102,
      "203.0.113.12",
      false
    ]
  ],
  "error": null
}
```

### FAIR endpoints

#### `GET /api/v1/fair/chain-checks`

```json
{
  "data": {
    "config_checks": {
      "config_dir": true,
      "dkg": true,
      "network_scope_firewall_rules": true,
      "upstream_config": true
    },
    "skaled_checks": {
      "blocks": true,
      "committee_scope_firewall_rules": true,
      "config": true,
      "config_updated": true,
      "exit_code_ok": true,
      "exit_zero": false,
      "rotation_id_updated": true,
      "rpc": true,
      "skaled_container": true,
      "upstream_exists": true,
      "volume": true
    }
  },
  "error": null
}
```

`exit_zero` is normally `false` while the skaled container is running; it indicates whether a stopped container exited with code zero.

#### `GET /api/v1/fair/chain-record`

Datetime fields from SKALE Admin are returned as Unix timestamps.

```json
{
  "data": {
    "record": {
      "name": "fair",
      "config_version": "2.9.0-stable.0",
      "sync_config_run": false,
      "first_run": false,
      "backup_run": false,
      "restart_count": 0,
      "failed_rpc_count": 0,
      "monitor_last_seen": 1768472430.0,
      "ssl_change_date": 0.0,
      "repair_date": 0.0,
      "dkg_status": 3,
      "repair_ts": null,
      "snapshot_from": null,
      "restart_ts": null,
      "force_skaled_start": false
    }
  },
  "error": null
}
```

### Cache and errors

* Send a JSON request body of `{"_no_cache": true}` to force a cold fetch.
* Response time is logged; caching reduces latency.
* Non-200 upstream responses are wrapped with the message in `error` and retain the upstream HTTP status.

### License

![GitHub](https://img.shields.io/github/license/skalenetwork/skale-watchdog.svg)

All contributions are made under the [GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.en.html). See [LICENSE](LICENSE).
