# 🧠 #OpenLearning — Public Learning Log
A fully automated system that syncs my daily learning logs from Notion to GitHub — every day at 4 AM IST, without me touching a single thing.

---

## Why I Built This

I started #OpenLearning to document my journey from a first-year CS student to someone who can actually build things in Data Science and ML.

But there was a problem — my logs lived in Notion, private and invisible. Nobody could see the work. And in tech, if it's not on GitHub, it didn't happen.

So I built a pipeline that makes my learning public, timestamped, and permanent. Every day I write in Notion. Every morning GitHub has a new commit.

No manual exports. No copy-pasting. Just writing and building.

---

## What This Repo Contains

Every day I log:
- **What I studied** — topic, concept, or project worked on
- **How long I spent** — hours invested
- **Detailed notes** — what I actually did, links to notebooks, LinkedIn posts, GitHub repos

Each day becomes its own Markdown file in the `logs/` folder.

---

## Repo Structure
OpenLearningLog/
│
├── logs/
│   ├── day-044-2026-05-03.md
│   ├── day-045-2026-05-04.md
│   └── ...
│
├── sync_notion_to_github.py   ← core automation script
├── .github/
│   └── workflows/
│       └── sync.yml           ← GitHub Actions schedule
└── README.md

---

## How the Automation Works
Every day at 4 AM IST
↓
GitHub Actions triggers the Python script
↓
Script queries Notion API for yesterday's entry
↓
Fetches the full page — table properties + body content
↓
Converts blocks to Markdown (bullets, headings, links, code)
↓
Pushes a new .md file to this repo via GitHub API

No server. No paid tools. Just GitHub Actions running on a cron schedule for free.

---

## Tech Behind It

| Component | What it does |
|-----------|-------------|
| **Notion API** | Reads my database entries and page content |
| **GitHub REST API** | Creates/updates files directly in this repo |
| **GitHub Actions** | Runs the script automatically every day at 4 AM IST |
| **Python** | Glues everything together — API calls, block parsing, markdown generation |

The hardest part was converting Notion's block-based content (paragraphs, bullets, toggles, code blocks, images) into clean Markdown. The script handles all block types recursively, including nested children.

---

## What Each Day's File Looks Like

```markdown
# Day 44

| Field         | Value        |
|---------------|--------------|
| 📅 Date       | May 03, 2026 |
| 🏷️ Topic      | Data Science |
| ⏱️ Time Spent | 5 hrs        |

## Notes

- Created Dataset on Kaggle

Spent hours practicing EDA seriously for the first time
and made a notebook: Social Media & Teen Mental Health (EDA)

https://kaggle.com/code/unfazed007/social-media-teen-mental-health-eda

- LinkedIn Post Link:
https://linkedin.com/posts/...
```

---

## How It Helps Me

**Consistency is easy to claim. Commits don't lie.**

- Every day's work is version-controlled and timestamped
- My learning journey is visible to anyone — recruiters, peers, collaborators
- Links to real work (Kaggle notebooks, GitHub repos, LinkedIn posts) are all in one place
- 6 months from now, this repo will be a complete record of how I grew

It also keeps me accountable. When you know it's going public at 4 AM, you write better notes.

---

## Topics Covered So Far

`Data Science` · `EDA` · `Machine Learning` · `DSA` · `SQL` · `Python` · `Visualization`

*(updates as the journey progresses)*

---

## Connect

- 🔗 [LinkedIn](https://www.linkedin.com/in/divyansh-sharma-5546b3223) — daily posts from this same journey
- 📊 [Kaggle](https://www.kaggle.com/unfazed007) — notebooks and datasets
- 💻 [GitHub](https://github.com/unfazed-07) — all projects

---

*Synced automatically from Notion every day at 4 AM IST via GitHub Actions*
