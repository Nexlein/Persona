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
* **Premium HTML Email Digest**: Normalizes the articles, formats them into a beautiful, mobile-responsive HTML digest, and emails it directly to the user using your SMTP server (e.g., Gmail).

### 2. Persona ChatBot (`Persona_ChatBot.json`)

* An interactive AI-driven chatbot allowing users to:
  * Log in securely with their email.
  * Verify their account using a 6-digit email confirmation code.
  * Register new accounts and set or update their newsletter topics, delivery times, and timezones.

---

## How the Automation Scripts Work

Setting up n8n workflows on a new machine usually requires manually creating credentials, copying IDs, and re-linking nodes. Persona automates all of this:

* **`credentials.json`**: A template containing the structural definitions for the **Supabase**, **Mistral**, and **SMTP** credentials. Instead of storing actual private keys, it contains expressions (e.g., `{{$env.SUPABASE_URL}}`) referencing the Docker environment.
* **`update_credentials.py`**: A python script that reads your `.env` configuration file and dynamically updates the credential IDs inside both the workflow JSON files and the `credentials.json` template to keep them aligned.
* **`launch.sh`**: The one-click entry point. It runs the credentials updater, spins up the Docker containers, automatically imports your credentials template, and imports the workflows into n8n.

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
