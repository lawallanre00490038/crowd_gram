# 🤖 Distributed Telegram-Based Data Collection & Enrichment Platform

A modular, scalable, and intelligent Telegram bot system designed for **data collection**, **annotation**, **quality assurance**, and **agent management** in **multimodal AI training workflows**.

> Built with **Aiogram 3.x**, supports **text, speech, image, and video tasks**, along with robust onboarding, task routing, QA, and admin insights.

---

## 🧠 Features

- 🎓 **Intelligent Onboarding Flow**  
  Video-based explanations, interactive quiz, and profile capture.

- ⚙️ **Task Management & Distribution**  
  Smart task dispatch based on agent profiles and preferences.

- 🧪 **Real-time QA & Validation**  
  Built-in and ML-assisted checks for audio, image, and text tasks.

- 💼 **Admin Dashboard Support**  
  Track submissions, agent progress, QA flags, and performance scores.

- 💰 **Milestone-Based Payment Logic**  
  Auto/manual payouts based on performance.

- 🎉 **Community Engagement Tools**  
  Leaderboards, badges, contests, feedback, and wellness modules.

---

## 🗂 Project Structure

```
aiogram-bot/
│
├── src/
│   ├── database/                  # DB connection & queries
│   ├── handlers/
│   │   ├── onboarding_routes/     # Intro, video, quiz, profile
│   │   ├── task_routes/           # Task sender, status, reworks
│   │   ├── payment_routes/        # Payment status & triggers
│   │   ├── community_routes/      # Broadcasts, leaderboards
│   │   ├── refresher_routes/      # Re-training & reminder flows
│   │   ├── admin_routes/          # Admin-only flows
│   │   └── errors_routes/         # Error and fallback handlers
│   ├── keyboards/                 # Inline and reply keyboards
│   ├── middlewares/              # Optional auth or logging middlewares
│   ├── services/                  # Notifications, schedulers
│   ├── states/                    # FSM states for onboarding/tasks
│   ├── utils/                     # Validators, logger, helpers
│   ├── config.py                  # Environment configs
│   ├── loader.py                  # Dispatcher & bot factory
│   └── data/quiz.json             # Quiz data + reference video links
│
├── init_db.sql                    # SQL for agent profile & logs
├── main.py                        # Entrypoint
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables (e.g. BOT_TOKEN)
└── README.md                      # You're here!
```

---

## 🚀 Setup Guide

### 1. Clone the Repo

```bash
git clone https://github.com/your-org/aiogram-data-collection-bot.git
cd aiogram-data-collection-bot
```

### 2. Set Environment Variables

Create a `.env` file:

```
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=your_database_url
```

### 3. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
psql your_database_url < init_db.sql
```

> You can also use Supabase, Firebase, or SQLite for early versions.

### 5. Run the Bot

```bash
python main.py
```

> ✅ You'll see: `Bot is running... Press Ctrl+C to stop.`

---

## 🧩 Key Modules

### Onboarding & Profiling

- `/start` command
- Video education → interactive quiz → profile form
- Fields: name, phone, gender, location, languages, education, task type, referrer

### Quiz Logic

- Defined in `data/quiz.json`
- 3 tries per question; after 3rd fail, shows explainer video
- Score tracked and stored in FSM

### Task Engine

- Assigns tasks based on:
  - Language, skill, location, history, availability
- Task types:
  - 🎤 Speech prompts
  - 📃 Text annotation
  - 🖼️ Image tagging
  - 🎬 Spontaneous video

### Quality Assurance

- ✅ Audio:
  - Duration, SNR, loudness, format
- 🖼️ Image:
  - Size, content check (e.g. nudity)
- 📄 Text:
  - Completeness, coherence, grammar
- Automatic + human review pipeline

### Payments

- Triggered after milestones
- Exportable as `CSV: Agent ID, Task Count, Amount`
- Users get `/payment_status` feedback

### Engagement

- 🎯 Leaderboards
- 🏅 Badges
- 📢 Broadcasts
- 🧠 Quizzes, wellness tips, contests

---

## 📦 Dependencies

```txt
aiogram==3.x
aiohttp
python-dotenv
asyncpg / psycopg2 / sqlite3
```

_Optional:_  
- `pydantic`, `sqlalchemy`, `firebase-admin`, `supabase`

---

## 🛠️ Deployment Notes

- ✅ Use [supervisor](http://supervisord.org) or `pm2` for process management
- 🐳 Dockerize if needed (`Dockerfile`, `docker-compose.yml`)
- 🌍 Deploy to:
  - Render
  - Railway
  - Fly.io
  - EC2 or VPS

---

## 📌 Future Extensions

- Agent dashboard (web view)
- B2B integration with annotation platforms
- OAuth or phone-number based verification
- In-bot file manager & resume flows
- Admin approval workflows

---

## 🙌 Contributing

We welcome PRs and feedback! To contribute:

```bash
git checkout -b feature/your-feature
```

Push and open a PR.

---

## 🧠 License

MIT License © 2025 EqualyzAI

---

## 📞 Contact

- Email: uche@equalyz.ai
- Telegram: [@equalyzcrowd](https://t.me/equalyzcrowd)
