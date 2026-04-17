from skale_core.settings import get_internal_settings


def is_fair() -> bool:
    node_st = get_internal_settings()
    return node_st.node_type == 'fair'


def is_passive() -> bool:
    node_st = get_internal_settings()
    return node_st.node_mode == 'passive'
