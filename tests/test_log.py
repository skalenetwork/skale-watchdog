import logging
import re
from typing import Any
from unittest.mock import MagicMock, patch

import log
from log import HidingFormatter, compose_hiding_patterns

NEK_PATTERN = r'NEK\:\w+'


def settings(**values: Any) -> MagicMock:
    stub = MagicMock()
    for key, value in values.items():
        setattr(stub, key, value)
    return stub


def test_active_skale_hides_both_hosts() -> None:
    stub = settings(sgx_url='http://192.168.1.100:1234', endpoint='http://10.0.0.1:8545')
    with (
        patch.object(log, 'PASSIVE', False),
        patch.object(log, 'NODE_GROUP', 'skale'),
        patch.object(log, 'get_settings', return_value=stub),
    ):
        patterns = compose_hiding_patterns()
    assert patterns[re.escape('192.168.1.100')] == '[SGX_IP]'
    assert patterns[re.escape('10.0.0.1')] == '[ETH_IP]'


def test_passive_skale_skips_sgx() -> None:
    stub = settings(endpoint='http://10.0.0.2:8545')
    with (
        patch.object(log, 'PASSIVE', True),
        patch.object(log, 'NODE_GROUP', 'skale'),
        patch.object(log, 'get_settings', return_value=stub) as get_settings,
    ):
        patterns = compose_hiding_patterns()
    assert patterns[re.escape('10.0.0.2')] == '[ETH_IP]'
    get_settings.assert_called_once()


def test_active_fair_skips_endpoint() -> None:
    stub = settings(sgx_url='http://192.168.1.105:1234')
    with (
        patch.object(log, 'PASSIVE', False),
        patch.object(log, 'NODE_GROUP', 'fair'),
        patch.object(log, 'get_settings', return_value=stub) as get_settings,
    ):
        patterns = compose_hiding_patterns()
    assert patterns[re.escape('192.168.1.105')] == '[SGX_IP]'
    get_settings.assert_called_once()


def test_passive_fair_yields_only_the_key_pattern() -> None:
    with (
        patch.object(log, 'PASSIVE', True),
        patch.object(log, 'NODE_GROUP', 'fair'),
        patch.object(log, 'get_settings') as get_settings,
    ):
        patterns = compose_hiding_patterns()
    assert patterns == {NEK_PATTERN: '[SGX_KEY]'}
    get_settings.assert_not_called()


def test_local_hosts_are_not_hidden() -> None:
    stub = settings(sgx_url='http://127.0.0.1:1026', endpoint='http://localhost:8545')
    with (
        patch.object(log, 'PASSIVE', False),
        patch.object(log, 'NODE_GROUP', 'skale'),
        patch.object(log, 'get_settings', return_value=stub),
    ):
        assert compose_hiding_patterns() == {NEK_PATTERN: '[SGX_KEY]'}


def record(message: str) -> logging.LogRecord:
    return logging.LogRecord('t', logging.INFO, 't.py', 1, message, None, None)


def test_formatter_redacts_hosts_and_keys() -> None:
    patterns = {NEK_PATTERN: '[SGX_KEY]', r'10\.0\.0\.1': '[ETH_IP]'}
    formatter = HidingFormatter('%(message)s', patterns)
    formatted = formatter.format(record('call 10.0.0.1 with NEK:deadbeef'))
    assert formatted == 'call [ETH_IP] with [SGX_KEY]'


def test_formatter_does_not_redact_the_word_none() -> None:
    with (
        patch.object(log, 'PASSIVE', True),
        patch.object(log, 'NODE_GROUP', 'fair'),
        patch.object(log, 'get_settings'),
    ):
        formatter = HidingFormatter('%(message)s', compose_hiding_patterns())
    assert formatter.format(record('sgx_url is None')) == 'sgx_url is None'


def test_hostname_dots_are_escaped() -> None:
    stub = settings(sgx_url='http://10.0.0.1:1234', endpoint='http://10.0.0.2:8545')
    with (
        patch.object(log, 'PASSIVE', False),
        patch.object(log, 'NODE_GROUP', 'skale'),
        patch.object(log, 'get_settings', return_value=stub),
    ):
        formatter = HidingFormatter('%(message)s', compose_hiding_patterns())
    assert formatter.format(record('10x0y0z1 stays')) == '10x0y0z1 stays'
