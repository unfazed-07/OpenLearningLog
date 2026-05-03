# 📓 Notion → GitHub Learning Log Sync

An automated pipeline that syncs my daily learning logs from Notion to GitHub every week — no manual exports, no copy-pasting.

---

## 🔍 What This Does

I track my **#1000DaysOfLearning** journey in a Notion database. Every day I log:
- What I studied (topic)
- How long I spent (hours)
- Detailed notes (inside the Notion page)

This project automatically pulls those entries every week and pushes them to this GitHub repository as clean Markdown files — one file per day.

---

## ⚙️ How It Works

```
Every Sunday at 11:30 PM IST
        ↓
GitHub Actions triggers the Python script
        ↓
Script queries Notion API for last 7 days of entries
        ↓
Fetches page body (notes, headings, code blocks, todos)
        ↓
Converts each entry to a Markdown file
        ↓
Pushes files to this repo via GitHub API
```

---

## 🗂️ Repository Structure

```
1000-days-of-learning/
│
├── logs/
│   ├── day-001-2026-03-21.md
│   ├── day-002-2026-03-22.md
│   └── ...
│
├── sync_notion_to_github.py   ← core sync script
├── .github/
│   └── workflows/
│       └── sync.yml           ← GitHub Actions schedule
└── README.md
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core scripting |
| Notion API | Reading database entries and page content |
| GitHub API | Creating and updating files in this repo |
| GitHub Actions | Weekly automation (cron schedule) |

---

## 📄 What Each Log File Looks Like

```markdown
# Day 44

| Field          | Value          |
|----------------|----------------|
| 📅 Date        | May 03, 2026   |
| 🏷️ Topic       | Data Science   |
| ⏱️ Time Spent  | 5 hrs          |

## Notes

(Full notes from the Notion page — headings, bullet points,
code snippets, to-do items, all converted to Markdown)
```

---

## 🔐 Setup (If You Want to Replicate This)

1. Create a Notion internal integration at [notion.so/my-integrations](https://notion.so/my-integrations) and connect it to your database
2. Get your Notion Database ID from the page URL
3. Generate a GitHub Personal Access Token with `repo` and `workflow` scopes
4. Add these as repository secrets:
   - `NOTION_API_KEY`
   - `NOTION_DATABASE_ID`
   - `SYNC_GITHUB_TOKEN`
5. Push the files — GitHub Actions handles the rest

---

## 🌱 Why I Built This

Consistency is easy to claim, hard to prove. Having every day's log version-controlled on GitHub means my learning journey is transparent, timestamped, and public — not just a streak counter on a social platform.

---

## 📌 Related

- [#1000DaysOfLearning on LinkedIn](https://www.linkedin.com/in/YOUR_PROFILE) — daily posts from this same journey
- Part of my broader goal of building in public while learning Data Science and ML

---

*Synced automatically every Sunday via GitHub Actions*
