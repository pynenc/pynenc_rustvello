# ruff: noqa: F403
# mypy: ignore-errors
"""Re-run the standard pynenc app_id_isolation tests against container backends.

The ``app_instance`` fixture is overridden in this package's conftest.py
to build apps backed by Docker containers (postgres, redis, mongo, mongo3).
Importing from ``all_tests`` pulls in every app_id_isolation test so they
execute against the container backends.
"""

from pynenc_tests.integration.app_id_isolation.all_tests import *  # noqa: F401
