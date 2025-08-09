# re-organized package submodule
from __future__ import annotations

import requests
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ApiResult:
    data: Any
    error: Optional[str]
    status_code: int

    def ok(self) -> bool:
        return self.error in (None, '') and 200 <= self.status_code < 300

    def __bool__(self) -> bool:
        return self.ok()


class NodeBase:
    api_prefix = '/api/v1'
    common_bp = 'common'
    default_port = 3009

    def __init__(
        self,
        base_url: str,
        timeout: int = 10,
        session: Optional[requests.Session] = None,
    ):
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        if not base_url.startswith(('http://', 'https://')):
            base_url = f'http://{base_url}'
        host_part = base_url.split('://', 1)[1]
        if ':' not in host_part:
            base_url = f'{base_url}:{self.default_port}'
        self.base_url = base_url
        self.timeout = timeout
        self.session = session or requests.Session()

    def containers(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.common_bp, 'containers'), params)

    def sgx(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.common_bp, 'sgx'), params)

    def hardware(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.common_bp, 'hardware'), params)

    def endpoint(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.common_bp, 'endpoint'), params)

    def meta_info(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.common_bp, 'meta-info'), params)

    def btrfs(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.common_bp, 'btrfs'), params)

    def ssl(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.common_bp, 'ssl'), params)

    def check_report(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.common_bp, 'check-report'), params)

    def _path(self, bp: str, method: str) -> str:
        return f'{self.api_prefix}/{bp}/{method}'

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> ApiResult:
        url = f'{self.base_url}{path}'
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            try:
                body = resp.json() if resp.content else {}
            except ValueError:
                body = {'data': resp.text, 'error': 'Invalid JSON'}
            if isinstance(body, dict):
                return ApiResult(
                    data=body.get('data'),
                    error=body.get('error'),
                    status_code=resp.status_code,
                )
            return ApiResult(data=body, error=None, status_code=resp.status_code)
        except requests.RequestException as exc:
            return ApiResult(data=None, error=str(exc), status_code=0)


class SkaleNode(NodeBase):
    bp = 'skale'

    def schains(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.bp, 'schains'), params)

    def ima(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.bp, 'ima'), params)

    def schain_containers_versions(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.bp, 'schain-containers-versions'), params)

    def public_ip(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.bp, 'public-ip'), params)

    def validator_nodes(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.bp, 'validator-nodes'), params)

    def sm_abi_hash(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.bp, 'sm-abi'), params)

    def ima_abi_hash(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.bp, 'ima-abi'), params)


class FairNode(NodeBase):
    bp = 'fair'

    def chain_checks(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.bp, 'chain-checks'), params)


__all__ = ['ApiResult', 'NodeBase', 'SkaleNode', 'FairNode']
