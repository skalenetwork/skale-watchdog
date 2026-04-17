from unittest.mock import MagicMock, patch

from utils.log import compose_hiding_patterns


def test_compose_hiding_patterns_active_skale():
    with patch('utils.log.is_passive', return_value=False), \
         patch('utils.log.is_fair', return_value=False), \
         patch('utils.log.get_settings') as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.sgx_url = 'http://192.168.1.100:1234'
        mock_settings.endpoint = 'http://10.0.0.1:8545'
        mock_get_settings.return_value = mock_settings
        patterns = compose_hiding_patterns()
        assert patterns.get('192.168.1.100') == '[SGX_IP]'
        assert patterns.get('10.0.0.1') == '[ETH_IP]'


def test_compose_hiding_patterns_passive_skale():
    with patch('utils.log.is_passive', return_value=True), \
         patch('utils.log.is_fair', return_value=False), \
         patch('utils.log.get_settings') as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.endpoint = 'http://10.0.0.2:8545'
        mock_get_settings.return_value = mock_settings
        patterns = compose_hiding_patterns()
        assert 'sgx_url' not in str(mock_get_settings.call_args_list[0])
        assert patterns.get('10.0.0.2') == '[ETH_IP]'
        mock_get_settings.assert_called_once()


def test_compose_hiding_patterns_active_fair():
    with patch('utils.log.is_passive', return_value=False), \
         patch('utils.log.is_fair', return_value=True), \
         patch('utils.log.get_settings') as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.sgx_url = 'http://192.168.1.105:1234'
        mock_get_settings.return_value = mock_settings
        patterns = compose_hiding_patterns()
        assert patterns.get('192.168.1.105') == '[SGX_IP]'
        mock_get_settings.assert_called_once()

