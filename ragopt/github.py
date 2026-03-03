from __future__ import annotations

import json
import os
import re
import urllib.request


def _pr_number_from_ref(ref: str | None) -> int | None:
    if not ref:
        return None
    m = re.match(r"refs/pull/(\d+)/", ref)
    if not m:
        return None
    return int(m.group(1))


def post_pr_comment(markdown: str) -> bool:
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    pr_num = _pr_number_from_ref(os.getenv("GITHUB_REF"))
    api_url = os.getenv("GITHUB_API_URL", "https://api.github.com")

    if not token or not repo or not pr_num:
        return False

    url = f"{api_url}/repos/{repo}/issues/{pr_num}/comments"
    payload = json.dumps({"body": markdown}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
            return 200 <= resp.status < 300
    except Exception:
        return False
