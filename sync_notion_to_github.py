"""
sync_notion_to_github.py
Fetches last 7 days of #1000DaysOfLearning entries from Notion
and pushes one markdown file per day to a GitHub repository.

Required environment variables:
  NOTION_API_KEY        — Notion internal integration secret
  NOTION_DATABASE_ID    — ID of your #1000DaysOfLearning database
  GITHUB_TOKEN          — GitHub personal access token (repo scope)
  GITHUB_REPO           — e.g. "divyansh-sharma/1000-days-of-learning"
"""

import os
import json
import base64
import requests
from datetime import datetime, timedelta, timezone

# ── Config ────────────────────────────────────────────────────────────────────

NOTION_API_KEY       = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID   = os.environ["NOTION_DATABASE_ID"]
GITHUB_TOKEN         = os.environ["GITHUB_TOKEN"]
GITHUB_REPO          = os.environ["GITHUB_REPO"]          # "owner/repo"
GITHUB_BRANCH        = os.environ.get("GITHUB_BRANCH", "main")
LOGS_FOLDER          = "logs"

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

GITHUB_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

# ── Notion: Query DB for last 7 days ─────────────────────────────────────────

def get_last_7_days_entries():
    """Return all database pages whose Date property falls in the last 7 days."""
    since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    url   = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"

    payload = {
        "filter": {
            "property": "Date",
            "date": {"on_or_after": since}
        },
        "sorts": [{"property": "Date", "direction": "ascending"}]
    }

    pages = []
    while True:
        resp = requests.post(url, headers=NOTION_HEADERS, json=payload)
        resp.raise_for_status()
        data = resp.json()
        pages.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]

    return pages

# ── Notion: Fetch page body (blocks) ─────────────────────────────────────────

def get_page_blocks(page_id):
    """Recursively fetch all blocks of a page."""
    url    = f"https://api.notion.com/v1/blocks/{page_id}/children"
    blocks = []
    params = {}

    while True:
        resp = requests.get(url, headers=NOTION_HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        blocks.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        params["start_cursor"] = data["next_cursor"]

    return blocks

# ── Notion: Convert blocks → Markdown ────────────────────────────────────────

def rich_text_to_str(rich_text_list):
    """Flatten a Notion rich_text array into a plain string."""
    return "".join(rt.get("plain_text", "") for rt in rich_text_list)

def blocks_to_markdown(blocks, depth=0):
    """Convert a list of Notion block objects to a Markdown string."""
    lines = []
    indent = "  " * depth

    for block in blocks:
        btype = block.get("type")
        content = block.get(btype, {})
        text = rich_text_to_str(content.get("rich_text", []))

        if btype == "paragraph":
            lines.append(f"{indent}{text}" if text else "")

        elif btype == "heading_1":
            lines.append(f"{indent}# {text}")

        elif btype == "heading_2":
            lines.append(f"{indent}## {text}")

        elif btype == "heading_3":
            lines.append(f"{indent}### {text}")

        elif btype == "bulleted_list_item":
            lines.append(f"{indent}- {text}")

        elif btype == "numbered_list_item":
            lines.append(f"{indent}1. {text}")

        elif btype == "to_do":
            checked = "x" if content.get("checked") else " "
            lines.append(f"{indent}- [{checked}] {text}")

        elif btype == "toggle":
            lines.append(f"{indent}<details><summary>{text}</summary>")

        elif btype == "quote":
            lines.append(f"{indent}> {text}")

        elif btype == "divider":
            lines.append(f"{indent}---")

        elif btype == "code":
            lang    = content.get("language", "")
            code    = rich_text_to_str(content.get("rich_text", []))
            lines.append(f"{indent}```{lang}\n{code}\n{indent}```")

        elif btype == "callout":
            emoji = content.get("icon", {}).get("emoji", "💡")
            lines.append(f"{indent}> {emoji} **{text}**")

        elif btype == "image":
            src = (
                content.get("file", {}).get("url")
                or content.get("external", {}).get("url", "")
            )
            caption = rich_text_to_str(content.get("caption", []))
            alt     = caption or "image"
            lines.append(f"{indent}![{alt}]({src})")

        elif btype == "child_page":
            lines.append(f"{indent}📄 *{content.get('title', 'Subpage')}*")

        # Recurse into children if present
        if block.get("has_children") and btype not in ("child_page",):
            child_blocks = get_page_blocks(block["id"])
            child_md     = blocks_to_markdown(child_blocks, depth=depth + 1)
            if child_md:
                lines.append(child_md)

        # Close toggle
        if btype == "toggle":
            lines.append(f"{indent}</details>")

    return "\n\n".join(line for line in lines if line is not None)

# ── Build Markdown for one day's entry ───────────────────────────────────────

def build_markdown(page):
    """Assemble a full .md string for a single Notion page/entry."""
    props = page.get("properties", {})

    # ── Pull table columns ──
    name_prop  = props.get("Name", {})
    date_prop  = props.get("Date", {})
    topic_prop = props.get("Topic", {})
    time_prop  = props.get("Time Spent (in hrs)", {})

    # Name (title property)
    title = rich_text_to_str(name_prop.get("title", []))

    # Date
    date_str = ""
    if date_prop.get("date"):
        date_str = date_prop["date"].get("start", "")

    # Topic (multi-select or select)
    topics = []
    if "multi_select" in topic_prop:
        topics = [t["name"] for t in topic_prop["multi_select"]]
    elif "select" in topic_prop and topic_prop["select"]:
        topics = [topic_prop["select"]["name"]]

    # Time spent (number)
    time_val = time_prop.get("number")
    time_str = f"{time_val} hrs" if time_val is not None else "—"

    # ── Format date nicely ──
    try:
        date_obj     = datetime.strptime(date_str, "%Y-%m-%d")
        date_display = date_obj.strftime("%B %d, %Y")
        date_iso     = date_str
    except Exception:
        date_display = date_str
        date_iso     = date_str

    # ── Page body ──
    blocks  = get_page_blocks(page["id"])
    body_md = blocks_to_markdown(blocks)

    # ── Assemble markdown ──
    lines = [
        f"# {title}",
        "",
        f"| Field         | Value             |",
        f"|---------------|-------------------|",
        f"| 📅 Date       | {date_display}    |",
        f"| 🏷️ Topic      | {', '.join(topics) if topics else '—'} |",
        f"| ⏱️ Time Spent | {time_str}        |",
        "",
    ]

    if body_md.strip():
        lines.append("## Notes")
        lines.append("")
        lines.append(body_md)
    else:
        lines.append("*No notes added for this day.*")

    lines.append("")
    lines.append("---")
    lines.append(f"*Synced automatically from Notion on {datetime.now(timezone.utc).strftime('%Y-%m-%d')} UTC*")

    return "\n".join(lines), date_iso, title

# ── GitHub: Create or update a file ──────────────────────────────────────────

def get_existing_sha(filepath):
    """Return the SHA of a file in GitHub if it exists, else None."""
    url  = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filepath}"
    resp = requests.get(url, headers=GITHUB_HEADERS, params={"ref": GITHUB_BRANCH})
    if resp.status_code == 200:
        return resp.json().get("sha")
    return None

def push_file_to_github(filepath, content_str, commit_message):
    """Create or update a file in the GitHub repo."""
    url     = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filepath}"
    encoded = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
    sha     = get_existing_sha(filepath)

    payload = {
        "message": commit_message,
        "content": encoded,
        "branch":  GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha   # required for updates

    resp = requests.put(url, headers=GITHUB_HEADERS, json=payload)
    resp.raise_for_status()
    action = "Updated" if sha else "Created"
    print(f"  ✅ {action}: {filepath}")

# ── Generate README index ─────────────────────────────────────────────────────

def build_readme(pushed_entries):
    """
    Build a README.md that lists all pushed day files as a table.
    pushed_entries: list of (title, date_iso, filepath)
    """
    lines = [
        "# 🧠 #1000DaysOfLearning",
        "",
        "Daily learning log synced automatically from Notion everyday.",
        "",
        "| Day | Date | Log |",
        "|-----|------|-----|",
    ]
    for title, date_iso, filepath in sorted(pushed_entries, key=lambda x: x[1]):
        lines.append(f"| {title} | {date_iso} | [View]({filepath}) |")

    lines.append("")
    lines.append(f"*Last synced: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC*")
    return "\n".join(lines)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("🔍 Fetching last 7 days from Notion...")
    pages = get_last_7_days_entries()
    print(f"   Found {len(pages)} entries.\n")

    pushed_entries = []

    for page in pages:
        print(f"📄 Processing: {page['id']}")
        try:
            content_md, date_iso, title = build_markdown(page)

            # Filename: day-044-2026-05-03.md
            # Extract day number from title like "Day 44"
            day_num = ""
            for word in title.split():
                if word.isdigit():
                    day_num = word.zfill(3)
                    break
            if not day_num:
                day_num = "000"

            filename = f"day-{day_num}-{date_iso}.md"
            filepath = f"{LOGS_FOLDER}/{filename}"

            push_file_to_github(
                filepath,
                content_md,
                f"sync: {title} ({date_iso})"
            )
            pushed_entries.append((title, date_iso, filepath))

        except Exception as e:
            print(f"  ❌ Error on page {page['id']}: {e}")

    # Push updated README
    if pushed_entries:
        print("\n📋 Updating README.md index...")
        readme_md = build_readme(pushed_entries)
        push_file_to_github("README.md", readme_md, "sync: update README index")

    print(f"\n🎉 Done. {len(pushed_entries)} file(s) synced.")

if __name__ == "__main__":
    main()
