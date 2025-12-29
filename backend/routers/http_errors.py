from __future__ import annotations

from fastapi import status

from backend.core.constants import Errors


def status_for_error(detail: str) -> int:
	"""
	Map domain error codes to HTTP status codes.
	Default: 400 Bad Request for unknown/validation errors.
	"""
	if detail == Errors.FORBIDDEN:
		return status.HTTP_403_FORBIDDEN
	if detail in (
		Errors.USER_NOT_FOUND,
		Errors.RECIPIENT_NOT_FOUND,
		Errors.GROUP_NOT_FOUND,
		Errors.PAYMENT_CODE_NOT_FOUND,
	):
		return status.HTTP_404_NOT_FOUND
	if detail in (
		Errors.PAYMENT_CODE_EXPIRED,
		Errors.PAYMENT_CODE_REDEEMED_ALREADY,
		Errors.RECIPIENT_NOT_REGISTERED,
		Errors.CAREGIVER_NOT_REGISTERED,
	):
		return status.HTTP_409_CONFLICT
	return status.HTTP_400_BAD_REQUEST


