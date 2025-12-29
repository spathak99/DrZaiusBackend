from __future__ import annotations

from typing import Tuple
from backend.core.constants import Pagination as PaginationConsts


def clamp_limit_offset(limit: int, offset: int, *, max_limit: int = 100) -> Tuple[int, int]:
	"""Clamp pagination values to sane bounds."""
	if limit is None:
		limit = PaginationConsts.DEFAULT_LIMIT
	limit = max(1, min(limit, max_limit))
	if offset is None:
		offset = PaginationConsts.DEFAULT_OFFSET
	offset = max(0, offset)
	return limit, offset


