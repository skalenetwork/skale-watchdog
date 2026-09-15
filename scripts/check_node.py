#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = ["skale-watchdog-client"]
#
# [tool.uv.sources]
# skale-watchdog-client = { path = "../watchdog_client" }
# ///

import argparse

from watchdog_client import (
    ApiResult,
    FairNode,
    FairPassiveNode,
    NodeBase,
    SkaleNode,
    SkalePassiveNode,
)

NODES: dict[str, type[NodeBase]] = {
    'skale': SkaleNode,
    'skale-passive': SkalePassiveNode,
    'fair': FairNode,
    'fair-passive': FairPassiveNode,
}


def describe(result: ApiResult) -> str:
    age = '-' if result.cache_age is None else f'{result.cache_age}s'
    return f'{result.status_code} age {age:>5} {"ok" if result else result.error}'


def main() -> None:
    parser = argparse.ArgumentParser(description='Query every watchdog check, cached and live')
    parser.add_argument('url', help='node host or URL, live checks need loopback (SSH tunnel)')
    parser.add_argument('--type', choices=NODES, default='skale')
    parser.add_argument('--timeout', type=int, default=40)
    args = parser.parse_args()

    node = NODES[args.type](args.url, timeout=args.timeout)
    cached = node.all_checks()
    live: dict[str, ApiResult] = {name: getattr(node, name)(_no_cache='1') for name in cached}

    width = max(map(len, cached))
    column = max(len(describe(result)) for result in cached.values())
    print(f'{"check":<{width}}  {"cached":<{column}}  live')
    for name in cached:
        print(f'{name:<{width}}  {describe(cached[name]):<{column}}  {describe(live[name])}')

    if any(result.cache_age is not None for result in live.values()):
        print('\nlive checks were served from cache: query 127.0.0.1 on the node or via SSH tunnel')
    raise SystemExit(0 if all(cached.values()) and all(live.values()) else 1)


if __name__ == '__main__':
    main()
