# 🤖 GitHub Activity Populator

An **autonomous AI agent** that automatically discovers open-source repositories, generates meaningful features using Google Gemini AI, and contributes Pull Requests on your behalf — keeping your GitHub contribution graph active.

---

## ✨ Features

- 🔍 **Smart Repository Discovery** — Searches GitHub for suitable repositories by language, star count, and activity
- 🧠 **AI-Powered Feature Generation** — Uses Google Gemini to generate contextually relevant code contributions
- 🔁 **Self-Correction** — Automatically detects and repairs syntax errors in AI-generated code
- 🎮 **Interactive Mode** — Browse discovered repos, review proposed features, and confirm before pushing
- ⚡ **Fully Automated Mode** — Zero interaction required; discovers, codes, and opens PRs autonomously
- 🎯 **Targeted Contributions** — Point the agent at a specific repository to contribute to
- 💾 **Persistent Config** — All settings are saved to a local `.env` file for reuse across runs
- 🛡️ **Dry-Run Mode** — Test the entire pipeline without making any real GitHub changes
- 📓 **Private Gist Logging** — Activity logs are saved as **private GitHub Gists** (one per day), never committed to the repo — so cloners never see your history

---

## 📋 Requirements

- Python **3.9+**
- Git installed and available on PATH
- A **GitHub Personal Access Token**
- A **Google Gemini API Key**

---

## 🚀 Quick Start (New Users)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/paragdhersarepaisewala/autonomous-coder.git
cd autonomous-coder
```

### Step 2 — Install Dependencies

```bash
pip install -r github_populator/requirements.txt
```

### Step 3 — Get Your API Keys

#### GitHub Personal Access Token
1. Go to [GitHub Settings → Developer Settings → Personal Access Tokens → Tokens (classic)](https://github.com/settings/tokens/new)
2. Create a new token with these scopes:
   - ✅ `repo` (full control of repositories)
   - ✅ `workflow`
   - ✅ `user` (read user info)
3. Copy the token — you'll only see it once!

#### Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **Create API Key**
3. Copy the key

### Step 4 — Run Setup Wizard

```bash
python main.py --setup
```

The setup wizard will prompt you for:

```
--- GitHub Populator Setup ---
GitHub Token [not set]: ghp_your_token_here
GitHub Username [not set]: your_github_username
Target Language [Python]: Python
Activity Logging: Private GitHub Gists (automatic)
Specific Repo to Contribute to (leave blank to search) [none]:

Configuration saved to .env file.
```

> **Note:** The Gemini API Key must be set manually in the `.env` file (see [Configuration](#-configuration)).

### Step 5 — Add Gemini Key to `.env`

Open the created `.env` file and add:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### Step 6 — Run It!

```bash
# Interactive mode (recommended for first run)
python main.py -i

# OR fully automated
python main.py -a
```

---

## 🎮 Usage

### Command Overview

```
python main.py [OPTIONS]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--interactive` | `-i` | Run in interactive mode (browse & confirm each step) |
| `--auto` | `-a` | Run in fully automated mode (no prompts) |
| `--setup` | | Launch the setup wizard to configure credentials |
| `--dry-run` | | Simulate the full pipeline without making real GitHub changes |
| `--repo OWNER/REPO` | | Target a specific repository (e.g. `microsoft/vscode`) |
| `--lang LANGUAGE` | | Override the target programming language |
| `--count N` | | Set how many contributions to make this run |
| `--type TYPE` | | Feature type: `utility`, `feature`, `fix`, `documentation` |
| `--save` | | Save any CLI overrides to `.env` permanently |
| `--help` | `-h` | Show help message |

---

## 📖 Modes in Detail

### 🎮 Interactive Mode (`-i`)

The agent walks you through each step, asking for input:

```bash
python main.py -i
```

**What you'll see:**
```
==================== Cycle 1/3 ====================

Discovered repositories:
 [1] some-user/awesome-tool (142 stars)
     A tool that does something cool
 [2] another-user/cool-lib (89 stars)
     Library for doing useful things
 ...

Select a repository number (or 'q' to quit): 2

Analyzing repository: another-user/cool-lib...
Generating feature ideas for cool-lib...

Proposed Feature: Add Rate Limiter Utility
Description: Thread-safe rate limiter to prevent API overload
Branch: llm-utility-xk92zp

Use this feature idea? (y/n, or 'r' to regenerate): y

Ready to implement and contribute 'Add Rate Limiter Utility' to another-user/cool-lib? (y/n): y

Executing contribution: Add Rate Limiter Utility...

SUCCESS: Contribution made to another-user/cool-lib
```

### ⚡ Automated Mode (`-a`)

Zero interaction — the agent handles everything:

```bash
python main.py -a --count 3
```

### 🛡️ Dry-Run Mode (`--dry-run`)

Safe testing — runs the full pipeline but skips forking, committing, and creating PRs:

```bash
python main.py --auto --dry-run --count 1
```

### 🎯 Targeted Contribution

Contribute to a specific repository you have in mind:

```bash
python main.py --repo microsoft/pyright --lang Python -a
```

### 💾 Save Settings for Next Run

Apply overrides and save them permanently to `.env`:

```bash
python main.py --lang JavaScript --count 5 --type feature --save
```

Next time you run `python main.py`, those settings will already be loaded.

---

## ⚙️ Configuration

All settings are stored in a `.env` file in the project root. The file is created automatically on first run or by running `--setup`.

### `.env` Reference

```env
# ─── GitHub Credentials ────────────────────────────────────────────
GITHUB_TOKEN=ghp_your_personal_access_token
GITHUB_USERNAME=your_github_username

# ─── Target Repository Override ─────────────────────────────────────
# If set, the agent will contribute to this specific repo instead of searching
# Leave blank to let the agent discover repositories automatically
TARGET_REPO_OVERRIDE=

# ─── Agent Behavior ─────────────────────────────────────────────────
TARGET_LANGUAGE=Python          # Language to search repos for
TARGET_CONTRIBUTIONS=3          # How many contributions to make per run
FEATURE_TYPE=utility            # Type: utility | feature | fix | documentation
MIN_STARS=10                    # Minimum star count for discovered repos
MAX_STARS=1000                  # Maximum star count for discovered repos
EXCLUDED_TOPICS=                # Comma-separated topics to exclude

# ─── Gemini AI ──────────────────────────────────────────────────────
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash   # Model to use for generation

# ─── Timing (seconds) ───────────────────────────────────────────────
CYCLE_DELAY=1800                # Wait between contribution cycles (default 30 min)
RETRY_DELAY=300                 # Wait before retrying after a failure (default 5 min)

# ─── LLM Settings ───────────────────────────────────────────────────
USE_LLM_FIRST=true              # Use Gemini AI first (recommended)
FALLBACK_TO_TEMPLATES=true      # Fall back to templates if AI fails
MAX_LLM_RETRIES=2               # Max self-correction attempts per generation
LLM_RETRY_DELAY=2               # Delay between retries (seconds)
```

---

## 🔄 How It Works

```
┌──────────────┐     ┌──────────────┐     ┌────────────────┐
│  1. DISCOVER │────▶│  2. ANALYZE  │────▶│  3. GENERATE   │
│              │     │              │     │                │
│ Search GitHub│     │ Clone & scan │     │ Gemini AI      │
│ by language, │     │ the repo's   │     │ creates feature│
│ stars, topics│     │ code context │     │ code + fix any │
│              │     │              │     │ syntax errors  │
└──────────────┘     └──────────────┘     └────────┬───────┘
                                                   │
                                                   ▼
┌──────────────┐     ┌──────────────┐     ┌────────────────┐
│  6. LOG      │◀────│  5. OPEN PR  │◀────│  4. COMMIT     │
│              │     │              │     │                │
│ Record to    │     │ Create Pull  │     │ Fork repo,     │
│ your activity│     │ Request on   │     │ create branch, │
│ log repo     │     │ original repo│     │ push changes   │
└──────────────┘     └──────────────┘     └────────────────┘
```

### Step-by-Step Details

1. **Discovery** — Queries the GitHub API for repositories matching your configured language and star range. Supports excluding topics you don't want (e.g. `archived,homework`).

2. **Analysis** — Clones the selected repository temporarily, scans the structure (files, directories, existing patterns), then cleans up.

3. **Feature Generation** — Sends the repository context to Gemini AI with a carefully engineered prompt. Gemini returns complete, production-ready code. If a syntax error is detected, the agent automatically requests a corrected version (up to `MAX_LLM_RETRIES` times).

4. **Commit** — Forks the repository to your account, creates a uniquely named branch, writes the generated file(s), commits, and pushes.

5. **Pull Request** — Opens a PR from your fork's feature branch to the original repository's default branch, with a meaningful title and description.

6. **Logging** — Appends a formatted Markdown entry to a **private GitHub Gist** (one per day, named `[GH-Populator] Activity Log YYYY-MM-DD`). The log is visible only to you at [gist.github.com](https://gist.github.com) — it is never committed to the repository, so users who clone this project never see your personal contribution history.

---

## 📁 Project Structure

```
github-populator/
├── main.py                          # Root entry point (run this)
├── .env                             # Your local config (auto-created)
├── github_populator/
│   ├── main.py                      # CLI argument parser & setup wizard
│   ├── requirements.txt
│   ├── agent_core/
│   │   └── controller.py            # Main agent loop & orchestration
│   ├── repository_discovery/
│   │   └── discoverer.py            # GitHub search & repo selection
│   ├── context_analysis/
│   │   └── analyzer.py              # Clone, scan & cleanup repos
│   ├── llm_generator/
│   │   ├── feature_synthesizer.py   # AI feature generation pipeline
│   │   ├── gemini_client.py         # Google Gemini API client
│   │   └── prompt_engineer.py       # Prompt crafting for feature ideas
│   ├── contribution_execution/
│   │   └── executor.py              # Fork, branch, commit, PR creation
│   ├── integration/
│   │   └── logger.py                # Activity log to your GitHub repo
│   └── utils/
│       ├── config.py                # .env config manager (get/set/save)
│       └── github_client.py         # Authenticated GitHub API wrapper
└── temp_repos/                      # Temporary clones (auto-cleaned)
```

---

## 🛠️ Common Recipes

### First-time user setup
```bash
python main.py --setup
# Add GEMINI_API_KEY to .env manually
python main.py --dry-run -i   # Test everything safely first
```

### Contribute to a language you know
```bash
python main.py --lang TypeScript --count 2 -i
```

### Save language preference permanently
```bash
python main.py --lang Go --save
```

### Fully automated daily contributions
```bash
python main.py -a --count 5
```

### Test without touching GitHub
```bash
python main.py -a --count 1 --dry-run
```

### Contribute to a specific repo interactively
```bash
python main.py --repo fastapi/fastapi -i
```

---

## ❓ Troubleshooting

### `GitHub Token not configured`
Run `python main.py --setup` to add your token, or edit `.env` directly.

### `Failed to clone repository`
- Check your internet connection
- Some repos may be too large or have restricted access
- The agent will automatically skip and try another repo

### `LLM generation failed`
- Verify your `GEMINI_API_KEY` is correct in `.env`
- Check your [Google AI Studio quota](https://aistudio.google.com/)
- Increase `MAX_LLM_RETRIES` in `.env`

### `Rate limit exceeded` (GitHub)
- GitHub API rate limits are 5,000 requests/hour for authenticated users
- Increase `CYCLE_DELAY` in `.env` to slow the agent down
- The agent uses a single token, so heavy use may hit limits

### PRs getting ignored / rejected
- Contribute to repos that are actively maintained (recent commits)
- Adjust `MIN_STARS` / `MAX_STARS` to target more popular high-quality repos
- Use `--type documentation` or `--type fix` for more likely-to-be-accepted contributions

---

## 📄 License

MIT License — use freely, fork openly, contribute back.

---

## 🙌 Contributing

PRs welcome! This project was built with its own agent 🤖
