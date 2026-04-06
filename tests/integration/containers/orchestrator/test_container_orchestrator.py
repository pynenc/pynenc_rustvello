# ruff: noqa: F403
# mypy: ignore-errors
"""Re-run the standard pynenc orchestrator tests against container backends.

The ``app_instance`` fixture is overridden in this package's conftest.py
to build apps backed by Docker containers (postgres, redis, mongo, mongo3).
Importing from ``all_tests`` pulls in every orchestrator test so they
execute against the container backends.
"""

from pynenc_tests.integration.orchestrator.all_tests import *  # noqa: F401
