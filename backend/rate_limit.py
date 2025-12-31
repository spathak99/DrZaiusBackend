from __future__ import annotations

from typing import Callable
from backend.core.settings import get_settings

# Optional import of slowapi; fall back to no-op if unavailable
try:
	from slowapi import Limiter  # type: ignore
	from slowapi.util import get_remote_address  # type: ignore
	HAS_SLOWAPI = True
except Exception:
	Limiter = None  # type: ignore
	get_remote_address = None  # type: ignore
	HAS_SLOWAPI = False


def _noop_decorator(fn):
	return fn


def _auth_key(request):
	# Fallback to IP if no Authorization header; if slowapi not present, value unused
	auth = request.headers.get("authorization")
	if auth:
		return auth
	# get_remote_address may be None in no-slowapi mode
	return request.client.host if getattr(request, "client", None) else "unknown"


_settings = get_settings()
_enabled = bool(getattr(_settings, "enable_rate_limiting", False) and HAS_SLOWAPI)

if _enabled:
	limiter = Limiter(key_func=get_remote_address)  # type: ignore[arg-type]
	_public_limit = getattr(_settings, "rate_limit_public", "10/minute")
	_mutation_limit = getattr(_settings, "rate_limit_mutation", "30/minute")

	def rl_public() -> Callable:
		return limiter.limit(_public_limit)

	def rl_mutation() -> Callable:
		return limiter.limit(_mutation_limit, key_func=_auth_key)
else:
	class _NoopLimiter:
		def limit(self, *_args, **_kwargs):
			return _noop_decorator
	limiter = _NoopLimiter()

	def rl_public() -> Callable:
		return limiter.limit("")

	def rl_mutation() -> Callable:
		return limiter.limit("")


