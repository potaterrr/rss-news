# AI Tech & Automation Hub - RSS News Automation

An automated news curation pipeline built for the **AI Tech & Automation Hub** Facebook page. This project fetches high-signal updates from major AI labs, developer tools, open-source agent repos, and GitHub trending streams, then passes them securely to Make.com for AI post generation and automated social publishing.

## 🚀 Tech Stack
* **GitHub Actions**: Automated cron scheduling & execution environment.
* **Python**: Core parsing script leveraging `feedparser`.
* **Make.com**: Workflow orchestration (Webhook trigger -> Google Gemini post drafting -> Google Imagen graphic -> Facebook Pages publishing).

## 📡 Curated Feeds Tracked
* **GitHub Trending Pulse** (Daily/Weekly developer repositories via RSSHub)
* **Core AI Labs**: OpenAI Blog, Google DeepMind, Google AI Blog
* **AI Tools & Open Source**: Hugging Face Blog, OpenClaw Releases
* **AI Coding & Agent Tooling**: OpenAI Codex, Claude Code, and Gemini CLI releases (.atom)
* **Core Ecosystem**: Python Insider official blog

## ⚙️ Automation Schedule
Runs automatically **every other day** via GitHub Actions cron, or can be triggered manually on-demand via the GitHub Actions tab.
