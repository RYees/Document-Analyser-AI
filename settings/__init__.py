import importlib
import os
import ssl

from flask_talisman import talisman
from funcy import distinct, remove

from ragbackend.settings.helpers import (
    add_decode_responses_to_redis_url,
    array_from_string,
    cast_int_or_default,
    fix_assets_path,
    int_or_none,
    parse_boolean,
    set_from_string,
)


# # _REDIS_URL is the unchanged REDIS_URL we get from env vars, to be used later with RQ
# _REDIS_URL = os.environ.get("REDASH_REDIS_URL", os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
# # This is the one to use for Redash' own connection:
# REDIS_URL = add_decode_responses_to_redis_url(_REDIS_URL)
PROXIES_COUNT = int(os.environ.get("REDASH_PROXIES_COUNT", "1"))

STATSD_HOST = os.environ.get("REDASH_STATSD_HOST", "127.0.0.1")
STATSD_PORT = int(os.environ.get("REDASH_STATSD_PORT", "8125"))
STATSD_PREFIX = os.environ.get("REDASH_STATSD_PREFIX", "redash")
STATSD_USE_TAGS = parse_boolean(os.environ.get("REDASH_STATSD_USE_TAGS", "false"))
MULTI_ORG = parse_boolean(os.environ.get("REDASH_MULTI_ORG", "false"))

LOG_LEVEL = os.environ.get("REDASH_LOG_LEVEL", "INFO")
LOG_STDOUT = parse_boolean(os.environ.get("REDASH_LOG_STDOUT", "false"))
LOG_PREFIX = os.environ.get("REDASH_LOG_PREFIX", "")
LOG_FORMAT = os.environ.get(
    "REDASH_LOG_FORMAT",
    LOG_PREFIX + "[%(asctime)s][PID:%(process)d][%(levelname)s][%(name)s] %(message)s",
)