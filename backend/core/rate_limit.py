"""Application-level rate limiting (slowapi).

Keyed by client IP. This is a per-process limiter (each backend replica keeps
its own counters), which is a solid first line of defence against brute-force
and flooding. For a hard, cluster-wide limit, also configure `limit_req` at the
ingress. Behind a proxy, X-Forwarded-For is honoured by get_remote_address.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address


limiter = Limiter(key_func=get_remote_address, default_limits=[])
