from .app_config import config

if config.app.stage == "production":
    from .production import *
else:
    from .development import *
