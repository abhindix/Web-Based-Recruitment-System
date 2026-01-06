"""Compatibility layer.

The project originally had auth/database dependencies under app.core.deps.
The canonical implementation now lives in app.api.deps.
"""

from app.api.deps import (  # noqa: F401
    get_db,
    get_current_user,
    require_roles,
)

# Backwards-compatible alias
require_role = require_roles
