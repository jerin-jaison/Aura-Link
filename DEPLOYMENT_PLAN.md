# 🚀 SaaS Deployment & Business Master Plan

This document outlines the most cost-effective yet scalable strategy to host Aura Link, along with a pricing model to ensure profitability.

---

## 🏗️ 1. Infrastructure Architecture (Budget-Friendly Stack)

We will use a "Best of Breed" approach using free/cheap tiers from specialized providers rather than putting everything on one expensive cloud.

| Component | Provider Recommendation | Why? | Estimated Cost (MVP) |
|-----------|------------------------|------|----------------------|
| **Web Server** | **Render.com** | Easiest setup, git-push deployment, free SSL. | **$7/mo** (Starter Video requires reliable uptime) |
| **Worker (Celery)**| **Render.com** | Background tasks (video processing) need a separate process. | **$7/mo** |
| **Database** | **Supabase** (PostgreSQL) | Managed Postgres. Generous free tier (500MB). Better than Render's free DB (which expires). | **$0/mo** (Free Tier) |
| **Redis** | **Upstash** | Serverless Redis for caching/Celery. Free tier is perfect for startups. | **$0/mo** (Free Tier) |
| **Storage** | **AWS S3** | Industry standard, durable, scalable. | **Usage Based** (~$0.023/GB) |
| **CDN (Optional)** | **Cloudflare** | Free Caching / DDoS protection. Saves bandwidth costs. | **$0/mo** |

**💰 Total Fixed Cost:** ~$14/month
**💰 Variable Cost:** Based on user uploads and views.

---

## 📊 2. Profitability & Pricing Strategy

To make a profit, your plan prices MUST cover **Storage** (keeping files) and **Bandwidth** (users ensuring videos).

### The Costs (AWS us-east-1)
- **Storage**: $0.023 per GB / month
- **Bandwidth (Egress)**: ~$0.09 per GB / month (This is the expensive part!)

### Scenario: "Premium Plan" (50GB Storage)
If a user fills their 50GB and streams it all once a month:
1.  **Storage Cost**: 50 GB * $0.023 = **$1.15**
2.  **Bandwidth Cost**: 50 GB * $0.09 = **$4.50**
3.  **Total Cost to You**: **$5.65 / user / month**

### ✅ Recommended Pricing
To maintain a healthy **50%+ profit margin**:

| Plan Name | Storage | Features | Recommended Price | Margin (Est) |
|-----------|---------|----------|-------------------|--------------|
| **Free** | 500 MB | No Cloud, Low Quality | **$0** | Loss Leader (Marketing) |
| **Starter**| 50 GB | Cloud Upload, Loop | **$12 - $15 / mo** | ~50-60% |
| **Pro** | 200 GB | Priority Support, 4K | **$39 - $49 / mo** | ~60% |

> **💡 Pro Tip**: Use **Cloudflare R2** instead of AWS S3 in the future. R2 has **$0 egress fees**, meaning you effectively pay $0 for bandwidth. This would drop your cost from $5.65 to **$1.15**, increasing your profit margin to **90%**!

---

## 🛠️ 3. Pre-Deployment Checklist

Before pushing to Render, you must configure your Django app for production.

### 1. Install Production Dependencies
Add these to `requirements.txt`:
```text
gunicorn==21.2.0        # Production Server
psycopg2-binary==2.9.9  # Postgres Adapter
dj-database-url==2.1.0  # DB Connection String Parser
whitenoise==6.6.0       # Static File Hosting
django-storages[s3]==1.14.2 # AWS S3 Support
boto3==1.34.0           # AWS SDK
redis==5.0.1            # Redis Client
```

### 2. Create `render.yaml` (Infrastructure as Code)
Create a file named `render.yaml` in your root directory:

```yaml
databases:
  - name: auralink-db
    plan: free # Note: Render free DBs expire. Use Supabase connection string instead!

services:
  - type: web
    name: auralink-web
    env: python
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput
    startCommand: gunicorn config.wsgi:application
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.0
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: 'False'
      - key: ALLOWED_HOSTS
        value: '*' # Or your domain
  
  - type: worker
    name: auralink-worker
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: celery -A config worker -l info --concurrency=2
    envVars:
      - key: DEBUG
        value: 'False'
```

### 3. Configure `settings/production.py`
Ensure your production settings handle the environment variables correctly:

```python
import dj_database_url
import os

# Database
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}

# Static Files (WhiteNoise)
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# AWS S3 Settings
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = 'us-east-1'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

---

## 🚀 4. Step-by-Step Hosting Guide

### Step 1: Database (Supabase)
1.  Go to [supabase.com](https://supabase.com) and create a free project.
2.  Go to **Settings** -> **Database**.
3.  Copy the **Connection String (URI)**. It looks like:
    `postgres://postgres.xxxx:password@aws-0-us-east-1.pooler.supabase.com:5432/postgres`

### Step 2: Storage (AWS S3)
1.  Go to AWS Console -> S3 -> **Create Bucket**.
2.  Name it (e.g., `auralink-production`).
3.  Uncheck "Block all public access" (handled by Django policies) OR configure CORS.
4.  Go to IAM -> Users -> Create User -> Attach `AmazonS3FullAccess`.
5.  Save the **Access Key** and **Secret Key**.

### Step 3: Redis (Upstash)
1.  Go to [upstash.com](https://upstash.com) and create a Redis database.
2.  Copy the `REDIS_URL`.

### Step 4: Deploy to Render
1.  Push your code to GitHub.
2.  Go to [dashboard.render.com](https://dashboard.render.com).
3.  Click **New +** -> **Web Service**.
4.  Connect your GitHub repo.
5.  **Environment Variables**: Add these:
    *   `DATABASE_URL`: (Paste Supabase string)
    *   `REDIS_URL`: (Paste Upstash string)
    *   `AWS_ACCESS_KEY_ID`: (Your AWS Key)
    *   `AWS_SECRET_ACCESS_KEY`: (Your AWS Secret)
    *   `AWS_STORAGE_BUCKET_NAME`: `auralink-production`
    *   `DJANGO_SETTINGS_MODULE`: `config.settings.production`
    *   `SECRET_KEY`: (Generate a random string)
    *   `DEBUG`: `False`
6.  Click **Deploy**.

### Step 5: Post-Deploy Checks
1.  **Run Migrations**: In Render Dashboard -> Shell, run:
    `python manage.py migrate`
2.  **Create Admin**:
    `python manage.py create_admin`
3.  **Verify S3**: Upload a test video from the admin panel to ensure it saves to AWS.

---

## 📉 Summary of Actions

1.  **Create Upgrade Plan**: Implement the Pricing Strategy above.
2.  **Optimize**: Switch to Cloudflare R2 later to multiply profits.
3.  **Monitor**: Use Sentry (Free tier) to catch production errors early.
