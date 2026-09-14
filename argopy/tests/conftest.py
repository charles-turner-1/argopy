import sys
import os
import logging
import shutil
import tempfile

import pytest
import argopy

sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))
from mocked_ftp import mocked_ftpserver
from mocked_http import mocked_httpserver


log = logging.getLogger("argopy.tests.conftests")


@pytest.fixture(scope="session", autouse=True)
def _isolate_argopy_cache_per_xdist_worker():
    """Give each pytest-xdist worker its own argopy cache directory.

    Many tests use ``cache=True`` with the default cachedir (~/.cache/argopy).
    Under pytest-xdist that directory is shared across worker processes, so
    concurrent cache reads/writes corrupt the fsspec cache index
    (JSONDecodeError) or race on cache entries (FileNotFoundError). Point each
    worker at a private cachedir. Outside xdist (no worker id) the default is
    left untouched.
    """
    worker = os.environ.get("PYTEST_XDIST_WORKER")
    if not worker:
        yield
        return
    with tempfile.TemporaryDirectory(prefix="argopy_cache_%s_" % worker) as cachedir:
        with argopy.set_options(cachedir=cachedir):
            yield


def pytest_sessionstart(session):
    log.debug("Starting tests session")
    log.debug("Initial session state: %s" % session)
    pass


def pytest_sessionfinish(session, exitstatus):
    try:
        shutil.rmtree(os.getenv('FTP_HOME'))
    except:
        pass
    log.debug("Ending tests session")
    log.debug("Final session state: %s" % session)
    pass