#
#   This file is part of SKALE Containers Watchdog
#
#   Copyright (C) 2020-Present SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
from pathlib import Path
from typing import Final, Literal

from skale_core.settings import (
    FairBaseSettings,
    FairSettings,
    InternalSettings,
    SkalePassiveSettings,
    SkaleSettings,
    get_internal_settings,
)

_FOLDER = Path(os.getenv('SETTINGS_FOLDER_PATH', '/settings'))

InternalSettings.model_config['toml_file'] = _FOLDER / 'internal.toml'
for _model in (SkaleSettings, SkalePassiveSettings, FairSettings, FairBaseSettings):
    _model.model_config['toml_file'] = _FOLDER / 'node.toml'

_INTERNAL = get_internal_settings()

NODE_GROUP: Final[Literal['skale', 'fair']] = 'skale' if _INTERNAL.node_type == 'skale' else 'fair'
PASSIVE: Final[bool] = _INTERNAL.node_mode == 'passive'

UPSTREAM_PORT: Final[int] = int(os.getenv('UPSTREAM_PORT', '3007'))
UPSTREAM_CONNECT_TIMEOUT: Final[int] = 3
REQUEST_READ_TIMEOUT: Final[int] = 25
REFRESH_READ_TIMEOUT: Final[int] = 60
REFRESH_INTERVAL: Final[int] = int(os.getenv('REFRESH_INTERVAL', '180'))
LOG_LEVEL: Final[str] = os.getenv('LOG_LEVEL', 'INFO')
