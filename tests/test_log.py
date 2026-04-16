from unittest.mock import MagicMock, patch

from utils.log import compose_hiding_patterns


def test_compose_hiding_patterns_active_skale():
    with patch('utils.log.INTERNAL_ST') as mock_internal_st, \
         patch('utils.log.get_settings') as mock_get_settings:
        mock_internal_st.node_mode = 'active'
        mock_internal_st.node_type = 'skale'
        mock_settings = MagicMock()
        mock_settings.sgx_url = 'http://192.168.1.100:1234'
        mock_settings.endpoint = 'http://10.0.0.1:8545'
        mock_get_settings.return_value = mock_settings
        patterns = compose_hiding_patterns()
        assert patterns.get('192.168.1.100') == '[SGX_IP]'
        assert patterns.get('10.0.0.1') == '[ETH_IP]'


def test_compose_hiding_patterns_passive_skale():
    with patch('utils.log.INTERNAL_ST') as mock_internal_st, \
         patch('utils.log.get_settings') as mock_get_settings:
        mock_internal_st.node_mode = 'passive'
        mock_internal_st.node_type = 'skale'
        mock_settings = MagicMock()
        mock_settings.endpoint = 'http://10.0.0.2:8545'
        mock_get_settings.return_value = mock_settings
        patterns = compose_hiding_patterns()
        assert '[SGX_IP]' not in patterns.values()
        assert patterns.get('10.0.0.2') == '[ETH_IP]'


def test_compose_hiding_patterns_active_fair():
    with patch('utils.log.INTERNAL_ST') as mock_internal_st, \
         patch('utils.log.get_settings') as mock_get_settings:
        mock_internal_st.node_mode = 'active'
        mock_internal_st.node_type = 'fair'
        mock_settings = MagicMock()
        mock_settings.sgx_url = 'http://192.168.1.105:1234'
        mock_get_settings.return_value = mock_settings
        patterns = compose_hiding_patterns()
        assert patterns.get('192.168.1.105') == '[SGX_IP]'
        assert '[ETH_IP]' not in patterns.values()


def test_compose_hiding_patterns_passive_fair():
    with patch('utils.log.INTERNAL_ST') as mock_internal_st, \
         patch('utils.log.get_settings') as mock_get_settings:
        mock_internal_st.node_mode = 'passive'
        mock_internal_st.node_type = 'fair'
        mock_get_settings.return_value = MagicMock()
        patterns = compose_hiding_patterns()
        assert '[SGX_IP]' not in patterns.values()
        assert '[ETH_IP]' not in patterns.values()
