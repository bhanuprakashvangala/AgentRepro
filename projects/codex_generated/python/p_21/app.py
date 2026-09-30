#!/usr/bin/env python3
"""Flask-based URL shortener with analytics, custom aliases, and expiration."""

from __future__ import annotations

import os
import random
import re
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from flask import Flask, abort, jsonify, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "shortener.db"

app = Flask(__name__)
app.config.setdefault("SQLALCHEMY_DATABASE_URI", f"sqlite:///{DATABASE_PATH}")
app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
app.config.setdefault("SHORT_CODE_LENGTH", 6)
app.config.setdefault("MAX_SHORT_CODE_LENGTH", 32)
app.config.setdefault("ALLOWED_ALIAS_PATTERN", r"^[A-Za-z0-9_-]+$")


db = SQLAlchemy(app)


class ShortURL(db.Model):  # type: ignore[misc]
    __tablename__ = "short_urls"

    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.Text, nullable=False)
    short_code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    click_count = db.Column(db.Integer, nullable=False, default=0)
    last_clicked_at = db.Column(db.DateTime, nullable=True)

    def is_expired(self) -> bool:
        return bool(self.expires_at and self.expires_at < datetime.utcnow())


with app.app_context():
    db.create_all()


def _generate_random_code(length: int) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choices(alphabet, k=length))


def _validate_alias(alias: str) -> None:
    max_len = app.config["MAX_SHORT_CODE_LENGTH"]
    pattern = re.compile(app.config["ALLOWED_ALIAS_PATTERN"])
    if len(alias) > max_len:
        abort(400, description=f"Alias too long (>{max_len} characters)")
    if not pattern.match(alias):
        abort(400, description="Alias must be alphanumeric with optional '-' or '_' characters")


def _resolve_expiration(expires_in_days: Optional[int], expires_at: Optional[str]) -> Optional[datetime]:
    if expires_at:
        try:
            return datetime.fromisoformat(expires_at)
        except ValueError:
            abort(400, description="expires_at must be ISO 8601 datetime string")
    if expires_in_days is not None:
        try:
            days = int(expires_in_days)
        except (TypeError, ValueError):
            abort(400, description="expires_in_days must be an integer")
        if days <= 0:
            abort(400, description="expires_in_days must be positive")
        return datetime.utcnow() + timedelta(days=days)
    return None


def _normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        abort(400, description="URL must not be empty")
    if not re.match(r"^(http|https)://", url, re.IGNORECASE):
        abort(400, description="URL must start with http:// or https://")
    return url


def _build_short_url(code: str) -> str:
    host = request.host_url.rstrip("/")
    return f"{host}/{code}"


def _generate_unique_code(length: int) -> str:
    while True:
        code = _generate_random_code(length)
        if not ShortURL.query.filter_by(short_code=code).first():
            return code


@app.route("/api/shorten", methods=["POST"])
def create_short_url():
    payload = request.get_json(silent=True) or {}
    original_url = payload.get("url") or payload.get("original_url")
    if not original_url:
        abort(400, description="Field 'url' is required")
    original_url = _normalize_url(str(original_url))

    alias = payload.get("alias") or payload.get("short_code")
    short_code_length = app.config["SHORT_CODE_LENGTH"]

    if alias:
        alias = str(alias).strip()
        _validate_alias(alias)
        short_code = alias
    else:
        short_code = _generate_unique_code(short_code_length)

    expires_in = payload.get("expires_in_days")
    expires_at = payload.get("expires_at")
    expiration = _resolve_expiration(expires_in, expires_at)

    entry = ShortURL(
        original_url=original_url,
        short_code=short_code,
        expires_at=expiration,
    )
    db.session.add(entry)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(409, description="Alias already exists. Choose a different alias")

    response = {
        "original_url": original_url,
        "short_code": short_code,
        "short_url": _build_short_url(short_code),
        "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
        "stats_url": url_for("get_stats", code=short_code, _external=True),
    }
    return jsonify(response), 201


@app.route("/<code>")
def resolve_short_url(code: str):
    record = ShortURL.query.filter_by(short_code=code).first()
    if not record:
        abort(404, description="Short URL not found")
    if record.is_expired():
        abort(410, description="Short URL has expired")

    record.click_count += 1
    record.last_clicked_at = datetime.utcnow()
    db.session.commit()
    return redirect(record.original_url, code=302)


@app.route("/api/stats/<code>")
def get_stats(code: str):
    record = ShortURL.query.filter_by(short_code=code).first()
    if not record:
        abort(404, description="Short URL not found")
    data = {
        "original_url": record.original_url,
        "short_code": record.short_code,
        "created_at": record.created_at.isoformat(),
        "expires_at": record.expires_at.isoformat() if record.expires_at else None,
        "click_count": record.click_count,
        "last_clicked_at": record.last_clicked_at.isoformat() if record.last_clicked_at else None,
        "is_expired": record.is_expired(),
        "short_url": _build_short_url(record.short_code),
    }
    return jsonify(data)


@app.route("/api/list")
def list_urls():
    records = ShortURL.query.order_by(ShortURL.created_at.desc()).limit(100).all()
    payload = [
        {
            "short_code": rec.short_code,
            "original_url": rec.original_url,
            "created_at": rec.created_at.isoformat(),
            "expires_at": rec.expires_at.isoformat() if rec.expires_at else None,
            "click_count": rec.click_count,
            "short_url": _build_short_url(rec.short_code),
        }
        for rec in records
    ]
    return jsonify(payload)


@app.route("/health")
def health_check():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


if __name__ == "__main__":
    debug = bool(os.getenv("FLASK_DEBUG"))
    app.run(host="0.0.0.0", port=5000, debug=debug)
