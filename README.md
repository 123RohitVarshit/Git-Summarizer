# Git-Summarizer CLI

AI-powered Git progress reports and commit message generator running inside CLI.

## Installation

```bash
pip install -e .
```

## Setup

### Option 1: OpenRouter API (Recommended - Free!)

1. Get a free API key at https://openrouter.ai/keys
2. Set the environment variable:
   ```powershell
   $env:OPENROUTER_API_KEY="your-api-key-here"
   ```

### Option 2: Gemini API

1. Get an API key at https://aistudio.google.com/apikey
2. Set the environment variable:
   ```powershell
   $env:GEMINI_API_KEY="your-api-key-here"
   ```

Or create a `.env` file (copy from `.env.example`).

## Quick Start

**Wizard Mode** - Just run without arguments:
```bash
git-summarizer
```

## Commands

| Command | Short | Description |
|---------|-------|-------------|
| `git-summarizer status` | `git-summarizer s` | Summarize uncommitted changes |
| `git-summarizer commit` | `git-summarizer c` | Generate commit message |
| `git-summarizer report` | `git-summarizer r` | Generate progress report |

### Examples

```bash
# Quick status with diff preview
git-summarizer s -d

# Generate progress report for last 7 days
git-summarizer r -d 7

# Save report as Markdown
git-summarizer r -d 7 -s report.md

# Send report to Slack
git-summarizer r -d 7 --slack

# Interactive mode
git-summarizer r -i
```

## Features

- 🧙 **Wizard Mode**: Run without arguments for guided experience
- 📊 **Status Summary**: AI-generated summary of uncommitted changes
- 💡 **Commit Messages**: Generate conventional commit messages
- 📈 **Progress Reports**: See accomplishments over the last N days
- 🎨 **Beautiful Output**: Rich terminal with colors, trees, and spinners
- 📁 **File Tree View**: Visual tree of changed files
- 💾 **Save Reports**: Export as Markdown files
- 📤 **Slack Integration**: Send reports directly to Slack
- 🔌 **Multi-Provider**: OpenRouter (free) or Gemini API

## Slack Setup (Optional)

1. Go to https://api.slack.com/apps
2. Create app → Incoming Webhooks → Add webhook
3. Set `SLACK_WEBHOOK_URL` in your `.env`

## License

MIT
