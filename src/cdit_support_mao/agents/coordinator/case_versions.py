"""Trusted, process-local synthetic case version fixtures; no database or I/O."""
from __future__ import annotations

import re
from threading import Lock


class FixtureCaseVersions:
    """Atomic expected-version updates within one process only."""
    def __init__(self, *, provisioning_capability: object):
        if provisioning_capability is None or isinstance(provisioning_capability, (str, bytes, int, bool)):
            raise ValueError("provisioning capability must be a private runtime object")
        self._provisioner = provisioning_capability
        self._versions: dict[str, int] = {}
        self._lock = Lock()

    def set_version(self, case_id: str, version: int, *, expected_version: int | None, capability: object) -> None:
        if capability is not self._provisioner:
            raise ValueError("unauthorized fixture provisioning")
        if not isinstance(case_id, str) or re.fullmatch(r"SYN-[A-Z0-9][A-Z0-9-]{0,58}", case_id) is None:
            raise ValueError("case ID must be synthetic")
        if isinstance(version, bool) or not isinstance(version, int) or not 1 <= version <= 2147483647:
            raise ValueError("invalid case version")
        if expected_version is not None and (type(expected_version) is not int or expected_version < 1):
            raise ValueError("invalid expected case version")
        with self._lock:
            current = self._versions.get(case_id)
            if current != expected_version or (current is not None and version <= current):
                raise ValueError("stale or non-increasing case version")
            self._versions[case_id] = version

    def with_version(self, case_id: str, operation):
        """Hold the fixture version steady for a short trusted transition."""
        with self._lock:
            return operation(self._versions.get(case_id))


class FixturePolicyVersions:
    """Atomic active synthetic policy-version fixture; no policy rules or database."""
    def __init__(self, *, provisioning_capability: object, active: frozenset[str]):
        if provisioning_capability is None or isinstance(provisioning_capability, (str, bytes, int, bool)):
            raise ValueError("provisioning capability must be a private runtime object")
        self._validate(active)
        self._provisioner = provisioning_capability
        self._active = frozenset(active)
        self._generation = 1
        self._lock = Lock()

    @staticmethod
    def _validate(active: frozenset[str]) -> None:
        if not isinstance(active, frozenset) or not active or any(
            not isinstance(value, str) or re.fullmatch(r"SYN-[A-Z0-9][A-Z0-9.-]{0,55}", value) is None
            for value in active
        ):
            raise ValueError("active synthetic policy versions are required")

    def replace(self, active: frozenset[str], *, expected_generation: int, capability: object) -> int:
        if capability is not self._provisioner:
            raise ValueError("unauthorized fixture provisioning")
        self._validate(active)
        if type(expected_generation) is not int or expected_generation < 1:
            raise ValueError("invalid policy generation")
        with self._lock:
            if self._generation != expected_generation:
                raise ValueError("stale policy generation")
            self._active = frozenset(active)
            self._generation += 1
            return self._generation

    def with_versions(self, operation):
        """Hold policy versions steady for one short trusted transition."""
        with self._lock:
            return operation(self._active)

    def with_snapshot(self, operation):
        """Hold both active policy versions and their generation steady."""
        with self._lock:
            return operation(self._active, self._generation)
