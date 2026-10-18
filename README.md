# Persona — Personalized AI Newsletter Agent

Persona is an automated, self-hosted system that delivers personalized news digests to users based on their custom interests, preferred times, and timezones.

It is built using **N8N**, **Supabase (PostgreSQL)**, **Mistral AI**, and **NewsAPI**, and is fully containerized with Docker.

---

## What the Workflows Do

The system consists of two core workflows:

### 1. Persona News Ingest (`Persona_News_Ingest.json`)

* **Timezone-Aware Trigger**: Runs every hour to check the database for users whose scheduled delivery hour matches the current hour in their local timezone.
* **Topic Extraction & AI Expansion**: Takes each user's interests (e.g., "artificial intelligence", "tech startups") and uses **Mistral AI** to generate optimized, english-translated keywords for NewsAPI.
* **News Fetching**: Queries NewsAPI for the latest articles on those expanded topics.
* **Premium HTML Email Digest**: Normalizes the articles, formats them into a beautiful, mobile-responsive HTML digest, and emails it directly to the user using your SMTP server (e.g., Gmail). The sender address is read from `SMTP_USER` in `.env` (`{{ $env.SMTP_USER }}` in the **Send Email** node).

### 2. Persona ChatBot (`Persona_ChatBot.json`)

* An interactive AI-driven chatbot allowing users to:
  * Log in with their email and password (passwords are stored as SHA-256 hashes in Supabase).
  * Register a new account when the email is unknown.
  * Set or update their newsletter topics, delivery times, and timezones once logged in (chat sessions are stored in Supabase).

---

## How the Automation Scripts Work

Setting up n8n workflows on a new machine usually requires manually creating credentials, copying IDs, and re-linking nodes. Persona automates all of this:

* **`update_credentials.py`**: A python script that reads your `.env` configuration file, generates `credentials.json` (the **Supabase**, **Mistral**, and **SMTP** credentials, filled with the real values from `.env`), and updates the credential IDs inside both workflow JSON files to keep them aligned.
* **`credentials.json`**: Generated locally by `update_credentials.py`. It contains your real keys, so it is gitignored and never committed.
* **`launch.sh`**: The one-click entry point. It runs the credentials updater, spins up the Docker containers, automatically imports the generated credentials, and imports the workflows into n8n.
* **`export.sh`**: Exports every workflow from the running n8n instance back into the project folder (`n8n export:workflow --backup`), to save changes made in the n8n UI.

---

## Getting Started (Local Setup)

### Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.
* A [NewsAPI key](https://newsapi.org/) (free tier).
* A [Mistral AI API key](https://mistral.ai/) (free tier).

---

### Step 1: Configure Environment Variables

Copy the example environment file and open it:

```bash
cp env.example .env
```

Edit your `.env` and fill in the values:

```text
# ─── Supabase Config ───
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key

# ─── News API Config ───
NEWS_API_KEY=your_news_api_key

# ─── N8N Encryption Key ───
# Generate a random 64-hex string using: openssl rand -hex 32
N8N_ENCRYPTION_KEY=your_64_hex_encryption_key

# ─── Credential Mapping IDs (Defaults) ───
CREDENTIAL_MISTRAL_CLOUD_API_ID=personaMistral01
CREDENTIAL_SUPABASE_API_ID=personaSupabase1
CREDENTIAL_SMTP_ID=personaSMTPLocal

# ─── Mistral API Key ───
MISTRAL_KEY=your_mistral_api_key

# ─── SMTP/Email Settings (Automated Setup) ───
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
# SMTP_USER is also the sender address of the digest e-mails
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_16_character_app_password
SMTP_SECURE=true
```

---

### Step 2: Set up Supabase

1. Log in to your **Supabase Dashboard** ➔ Go to the **SQL Editor**.
2. Open **supabase-setup.sql** from this project.
3. Copy the entire file, paste it into a new query in Supabase, and click **Run**.
   * *This automatically creates the tables, indexes, RLS, and the `users_to_schedule` database view.*

---

### Step 3: Launch the Stack (One-Click)

Make sure `launch.sh` is executable, then run it:

```bash
chmod +x launch.sh
./launch.sh
```

This single command will:

1. Synchronize the credential IDs in your workflow files and templates using `update_credentials.py`.
2. Spin up the N8N docker container.
3. Automatically create your **Supabase**, **Mistral**, and **SMTP** credentials inside N8N.
4. Import the **ChatBot** and **News Ingest** workflows.
5. **No manual steps are required in the n8n UI!** Everything is ready to go.

---

## Useful Commands

```bash
# View live logs from the N8N container
docker compose logs -f n8n

# Stop the services without removing data
docker compose down

# Full reset (removes all database and configuration volumes)
docker compose down -v
```
