import os
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

BR_TZ = ZoneInfo("America/Sao_Paulo")

logging.basicConfig(level=logging.INFO)


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

db = SQLAlchemy(app, model_class=Base)


def _to_brt(dt):
    """Treat a naive datetime as UTC (because we store everything as UTC),
    then convert to America/Sao_Paulo. Aware datetimes are converted directly."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(BR_TZ)


@app.template_filter("localtime")
def localtime_filter(dt, fmt="%d/%m/%Y %H:%M"):
    """Render a stored UTC datetime in Brazil time (UTC-3, no DST)."""
    local = _to_brt(dt)
    return local.strftime(fmt) if local else ""


@app.template_filter("isoutc")
def isoutc_filter(dt):
    """Emit an unambiguous ISO-8601 UTC string for the browser to localize."""
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

with app.app_context():
    import models  # noqa: F401
    db.create_all()

import routes  # noqa: F401,E402

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
