from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

import requests


@dataclass
class ApiResult:
    data: Any
    error: str | None
    status_code: int
    cache_age: int | None = None
    stale: bool = False

    def ok(self) -> bool:
        return self.error in (None, '') and 200 <= self.status_code < 300 and not self.stale

    def __bool__(self) -> bool:
        return self.ok()


class NodeBase:
    api_prefix = '/api/v1'
    common_bp = 'common'
    default_http_port = 3009
    default_https_port = 311

    def __init__(
        self,
        base_url: str,
        timeout: int = 10,
        session: requests.Session | None = None,
        max_age: int | None = None,
    ):
        base_url = base_url.rstrip('/')
        if not base_url.startswith(('http://', 'https://')):
            base_url = f'http://{base_url}'
        parsed = urlsplit(base_url)
        if parsed.port is None:
            port = self.default_https_port if parsed.scheme == 'https' else self.default_http_port
            base_url = f'{base_url}:{port}'
        self.base_url = base_url
        self.timeout = timeout
        self.session = session or requests.Session()
        self.max_age = max_age

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

    def all_checks(self) -> dict[str, ApiResult]:
        excluded_names = {'all_checks', 'session', 'base_url', 'timeout'}
        if self.__class__.__name__ == 'FairPassiveNode':
            excluded_names.add('sgx')
        if self.__class__.__name__ == 'SkalePassiveNode':
            excluded_names.update({'sgx', 'schains', 'ima', 'validator_nodes'})
        results: dict[str, ApiResult] = {}
        for name in sorted(dir(self)):
            if name.startswith('_') or name in excluded_names:
                continue
            attr = getattr(self, name)
            if not callable(attr):
                continue
            value = attr()
            results[name] = value
        return results

    def _path(self, bp: str, method: str) -> str:
        return f'{self.api_prefix}/{bp}/{method}'

    def _get(self, path: str, params: dict[str, Any] | None = None) -> ApiResult:
        url = f'{self.base_url}{path}'
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            try:
                body = resp.json() if resp.content else {}
            except ValueError:
                body = {'data': resp.text, 'error': 'Invalid JSON'}
            if not isinstance(body, dict):
                return ApiResult(
                    data=None, error='Unexpected response shape', status_code=resp.status_code
                )
            header = resp.headers.get('X-Cache-Age')
            age = int(header) if header is not None else None
            return ApiResult(
                data=body.get('data'),
                error=body.get('error'),
                status_code=resp.status_code,
                cache_age=age,
                stale=self.max_age is not None and age is not None and age > self.max_age,
            )
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


class SkalePassiveNode(SkaleNode):
    def sgx(self, **params: Any) -> ApiResult:
        return ApiResult(
            data=None,
            error='SGX check is not available on SKALE passive nodes',
            status_code=404,
        )

    def schains(self, **params: Any) -> ApiResult:
        return ApiResult(
            data=None,
            error='schains check is not available on SKALE passive nodes',
            status_code=404,
        )

    def ima(self, **params: Any) -> ApiResult:
        return ApiResult(
            data=None,
            error='IMA check is not available on SKALE passive nodes',
            status_code=404,
        )

    def validator_nodes(self, **params: Any) -> ApiResult:
        return ApiResult(
            data=None,
            error='Validator nodes check is not available on SKALE passive nodes',
            status_code=404,
        )


class FairNode(NodeBase):
    bp = 'fair'

    def chain_checks(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.bp, 'chain-checks'), params)

    def chain_record(self, **params: Any) -> ApiResult:
        return self._get(self._path(self.bp, 'chain-record'), params)


class FairPassiveNode(FairNode):
    def sgx(self, **params: Any) -> ApiResult:
        return ApiResult(
            data=None,
            error='SGX check is not available on FAIR passive nodes',
            status_code=404,
        )


__all__ = ['ApiResult', 'FairNode', 'FairPassiveNode', 'NodeBase', 'SkaleNode', 'SkalePassiveNode']
