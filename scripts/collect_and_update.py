import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

REPOS = {
    "A": "ensismoebius/biblioteca_2Mtec_2026_A",
    "B": "ensismoebius/biblioteca_2Mtec_2026_B",
}
ESFORCO_RE = re.compile(r"esforço:\s*(\d+)")

TOKEN = os.environ.get("GITHUB_TOKEN", "")


def curl_json(url):
    headers = ["-H", "Accept: application/vnd.github+json"]
    if TOKEN:
        headers += ["-H", f"Authorization: Bearer {TOKEN}"]
    r = subprocess.run(
        ["curl", "-s", *headers, url],
        capture_output=True, text=True, check=True,
    )
    return json.loads(r.stdout)


def pontos(labels):
    for l in labels:
        m = ESFORCO_RE.match(l["name"])
        if m:
            return int(m.group(1))
    return 0


def todas_issues(repo):
    issues, page = [], 1
    while True:
        pagina = curl_json(f"https://api.github.com/repos/{repo}/issues?state=all&per_page=100&page={page}")
        if not isinstance(pagina, list) or not pagina:
            break
        issues.extend(i for i in pagina if "pull_request" not in i)
        if len(pagina) < 100:
            break
        page += 1
    return issues


def coletar(repo):
    issues = todas_issues(repo)
    milestones = curl_json(f"https://api.github.com/repos/{repo}/milestones?state=all&per_page=100")
    ms_order = {m["title"]: m["number"] for m in milestones}

    por_sprint = {}
    for i in issues:
        ms = (i.get("milestone") or {}).get("title", "Sem sprint")
        pts = pontos(i.get("labels", []))
        entry = por_sprint.setdefault(ms, {"issues_total": 0, "issues_done": 0, "pontos_total": 0, "pontos_done": 0})
        entry["issues_total"] += 1
        entry["pontos_total"] += pts
        if i["state"] == "closed":
            entry["issues_done"] += 1
            entry["pontos_done"] += pts

    total_issues = len(issues)
    total_done = sum(1 for i in issues if i["state"] == "closed")
    total_pts = sum(pontos(i.get("labels", [])) for i in issues)
    done_pts = sum(pontos(i.get("labels", [])) for i in issues if i["state"] == "closed")

    return {
        "repo": repo, "total_issues": total_issues, "total_done": total_done,
        "total_pts": total_pts, "done_pts": done_pts, "sprints": por_sprint,
        "ms_order": ms_order, "assignees": {},
    }


def main():
    out = {"generated_at": datetime.now(timezone.utc).isoformat()}
    for turma, repo in REPOS.items():
        out[turma] = coletar(repo)

    if out["A"]["total_issues"] < 50 or out["B"]["total_issues"] < 50:
        print("Sanity check failed: total_issues too low, aborting without publishing.", file=sys.stderr)
        print(json.dumps(out, indent=2, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    index_path = os.path.join(os.path.dirname(__file__), "..", "index.html")
    with open(index_path, encoding="utf-8") as f:
        html = f.read()

    json_text = json.dumps(out, indent=2, ensure_ascii=False)
    new_html, n = re.subn(r"const DATA = \{.*?\};", "const DATA = " + json_text + ";", html, count=1, flags=re.DOTALL)
    if n != 1:
        print("Could not find exactly one 'const DATA = {...};' block, aborting.", file=sys.stderr)
        sys.exit(1)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
