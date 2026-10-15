from __future__ import annotations

import ipaddress
import os
import re
import socket
from pathlib import Path
from typing import Callable, Iterable
from urllib.parse import urlsplit


_CONTROL = re.compile(r"[\x00-\x1f\x7f]")
_SAFE_FILENAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._ -]{0,119}$")


class SecurityValidationError(ValueError):
    pass


def redact_text(text: str, extra_secrets: Iterable[str] = ()) -> str:
    """Best-effort redaction for anything that may reach logs or error messages."""
    out = str(text)
    secrets = [os.environ.get("OPENAI_API_KEY", ""), *list(extra_secrets)]
    for secret in secrets:
        if secret:
            out = out.replace(secret, "[REDACTED]")
    out = re.sub(r"(?i)(authorization\s*:\s*bearer\s+)[^\s,;]+", r"\1[REDACTED]", out)
    out = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._~+\-/=]{12,}", r"\1[REDACTED]", out)
    out = re.sub(r"\bsk-[A-Za-z0-9_-]{8,}\b", "[REDACTED]", out)
    return out


def validate_public_http_url(
    url: str,
    *,
    resolve_dns: bool = False,
    resolver: Callable[..., list[tuple]] = socket.getaddrinfo,
) -> str:
    """Validate a build-time source URL and reject local/private-network targets.

    DNS resolution is optional so unit tests with injected offline openers do not perform network
    calls. Real SourceFetcher calls enable it before making a request and on every redirect.
    """
    if not isinstance(url, str) or not url or _CONTROL.search(url):
        raise SecurityValidationError("source URL is empty or contains control characters")
    p = urlsplit(url)
    if p.scheme.lower() not in {"http", "https"}:
        raise SecurityValidationError("source URL must use http or https")
    if not p.hostname:
        raise SecurityValidationError("source URL is missing a hostname")
    if p.username or p.password:
        raise SecurityValidationError("source URL may not contain credentials")
    host = p.hostname.rstrip(".").lower()
    if host == "localhost" or host.endswith(".localhost"):
        raise SecurityValidationError("source URL may not target localhost")

    def reject_ip(value: str) -> None:
        try:
            ip = ipaddress.ip_address(value)
        except ValueError:
            return
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise SecurityValidationError("source URL resolves to a non-public address")

    reject_ip(host.strip("[]"))
    if resolve_dns:
        try:
            infos = resolver(host, p.port or (443 if p.scheme.lower() == "https" else 80), type=socket.SOCK_STREAM)
        except OSError as exc:
            raise SecurityValidationError(f"source hostname could not be resolved: {type(exc).__name__}") from exc
        if not infos:
            raise SecurityValidationError("source hostname resolved to no addresses")
        for info in infos:
            reject_ip(str(info[4][0]))
    return url


def validate_external_link(url: str) -> str:
    """Validate a visitor-facing source link without DNS/network access."""
    return validate_public_http_url(url, resolve_dns=False)


def validate_media_filename(filename: str) -> str:
    """Only allow a single local basename; never let manifest data become a path."""
    if not filename:
        return filename
    if _CONTROL.search(filename) or not _SAFE_FILENAME.fullmatch(filename):
        raise SecurityValidationError("media filename contains unsafe characters")
    if filename in {".", ".."} or "/" in filename or "\\" in filename:
        raise SecurityValidationError("media filename must be a basename only")
    if Path(filename).name != filename:
        raise SecurityValidationError("media filename must not contain a path")
    return filename


def ensure_profile_output(repo_root: Path, out_dir: Path, expected_slug: str | None = None) -> Path:
    """Require exactly repo/profiles/<slug>, with no nesting or symlink escape."""
    repo = Path(repo_root).resolve()
    profiles = (repo / "profiles").resolve()
    out = Path(out_dir).resolve()
    if out.parent != profiles:
        raise SecurityValidationError(f"output must be exactly {profiles}/<slug>; got {out}")
    if expected_slug is not None and out.name != expected_slug:
        raise SecurityValidationError(f"output directory name must match slug '{expected_slug}'")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", out.name):
        raise SecurityValidationError("profile slug contains unsupported characters")
    return out


def ensure_media_path(profile_dir: Path, filename: str) -> Path:
    validate_media_filename(filename)
    media_root = (Path(profile_dir).resolve() / "media").resolve()
    target = (media_root / filename).resolve()
    if target.parent != media_root:
        raise SecurityValidationError("media path escaped the profile media directory")
    return target
