"""Backward-compatible shim.

The schemas used to live in this single module. They now live in domain modules
(see the package __init__). This re-export keeps every existing
``from schemas.schemas import X`` import working unchanged.
"""

from schemas import *  # noqa: F401,F403
