"""Thin GitHub API client.

Read operations are free; write operations must be called only after
Agency Gate approval. Tokens are never logged or stored by this module.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from anne_core.github.auth import AuthResult, GitHubAuth


class GitHubClient:
    """Minimal GitHub REST client for the installer."""

    API = "https://api.github.com"

    def __init__(self, token: str | None = None) -> None:
        self._token = token
        self._auth = GitHubAuth()

    def ensure_authenticated(self) -> AuthResult:
        if self._token:
            return AuthResult(success=True, token=self._token, method="provided")
        result = self._auth.authenticate(interactive=False)
        if result.success and result.token:
            self._token = result.token
        return result

    def _headers(self) -> dict[str, str]:
        h = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "anne-core-installer",
        }
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.API}{path}"
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=self._headers(), method=method)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            raise RuntimeError(f"GitHub API {exc.code}: {detail}") from exc

    def list_repositories(self, per_page: int = 30) -> list[dict[str, Any]]:
        auth = self.ensure_authenticated()
        if not auth.success:
            raise PermissionError(auth.error or "GitHub authentication required.")
        data = self._request("GET", f"/user/repos?per_page={per_page}&sort=updated")
        return data if isinstance(data, list) else []

    def inspect_repository(self, owner: str, repo: str) -> dict[str, Any]:
        auth = self.ensure_authenticated()
        if not auth.success:
            raise PermissionError(auth.error or "GitHub authentication required.")
        return self._request("GET", f"/repos/{owner}/{repo}")

    def get_file_contents(
        self, owner: str, repo: str, path: str, ref: str = "main"
    ) -> dict[str, Any] | None:
        auth = self.ensure_authenticated()
        if not auth.success:
            raise PermissionError(auth.error or "GitHub authentication required.")
        try:
            return self._request("GET", f"/repos/{owner}/{repo}/contents/{path}?ref={ref}")
        except RuntimeError as exc:
            if "404" in str(exc):
                return None
            raise

    def create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str = "main",
        sha: str | None = None,
    ) -> dict[str, Any]:
        """Write a file. Caller MUST have obtained Agency Gate approval."""
        import base64

        auth = self.ensure_authenticated()
        if not auth.success:
            raise PermissionError(auth.error or "GitHub authentication required.")
        body: dict[str, Any] = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": branch,
        }
        if sha:
            body["sha"] = sha
        return self._request("PUT", f"/repos/{owner}/{repo}/contents/{path}", body)
