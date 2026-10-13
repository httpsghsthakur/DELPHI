"""DELPHI API entrypoint module.

Provides the ASGI application instance `app` as expected by uvicorn,
Makefile, and documentation (e.g. `uvicorn delphi.api.main:app`).
"""

from delphi.api.app import app, create_app

__all__ = ["app", "create_app"]
