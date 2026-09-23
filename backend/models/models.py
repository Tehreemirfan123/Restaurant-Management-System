"""Backward-compatible shim.

The models used to live in this single module. They now live in domain modules
(see the package __init__). This re-export keeps every existing
``from models.models import X`` import working unchanged.
"""

from models import *  # noqa: F401,F403
