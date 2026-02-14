# Cost – keeping AWS spend low

This stack is tuned for **low cost** (dev / small production). Rough **monthly** estimates in **us-east-1**:

| Resource | Config | Approx. monthly (USD) | Notes |
|----------|--------|------------------------|--------|
| **ECS Fargate** | 1 task, 0.25 vCPU, 512 MB | ~\$7–10 | Smallest Fargate size. Scale to 0 when not needed to save more. |
| **ALB** | 1 ALB, HTTP | ~\$16–20 | Fixed cost; shared if you add more target groups. |
| **RDS PostgreSQL** | db.t3.micro, 20 GB, single AZ | ~\$15–18 | Free tier: 750 hrs/mo for 12 months if eligible. |
| **S3** | 1 bucket, low storage | &lt;\$1 | Pay for storage + requests; usually cents. |
| **ECR** | 1 repo, 1 image | &lt;\$1 | 500 MB free/month. |
| **CloudWatch Logs** | 7-day retention (dev) | &lt;\$1 | First 5 GB ingestion/month free. |
| **Data transfer** | Out to internet | varies | First 1 GB/month free; then ~\$0.09/GB. |

**Rough total (dev, 1 task, RDS, ALB): ~\$40–50/month** if not on free tier. With **12‑month free tier** (new account): RDS and some Fargate/usage can be free or heavily discounted; expect **~\$20–30 or less**.

## How we keep cost down

- **Default VPC** – No NAT gateway (~\$32/mo saved).
- **Single AZ RDS** – No multi-AZ (~same again saved).
- **Fargate 256 CPU / 512 MB** – Smallest task size.
- **One ECS task** – `ecs_desired_count = 1`; increase only when needed.
- **db.t3.micro** – Smallest RDS instance; use **Aurora Serverless v2** only if you need it.
- **Short log retention** – 7 days in dev (30 in prod) to limit CloudWatch cost.
- **HTTP only by default** – No ACM/HTTPS unless you add it (no extra cost for the cert, but you may use more ALB/Route53).

## Optional: reduce cost further

1. **Skip RDS in Terraform** – Set `create_rds = false` and use an existing DB or external Postgres; saves ~\$15–18/mo.
2. **Run ECS only when needed** – Set `ecs_desired_count = 0` when idle; set back to 1 when you want the API up (saves Fargate, not ALB).
3. **Use a single EC2** – Replace ECS + ALB with one small EC2 (e.g. t3.micro) and run Docker there; can be cheaper at very low traffic but you manage the server.
4. **Free tier** – New AWS accounts get 12 months free tier (RDS, some Fargate/EC2, S3, etc.); check [AWS Free Tier](https://aws.amazon.com/free/).

## Billing alerts (recommended)

1. In **AWS Billing** → **Billing preferences**, turn on **Receive Free Tier Alerts** and **Receive Billing Alerts**.
2. Create a **Budget** (e.g. \$50/month) with an email alert at 80% and 100%.

Prices vary by region and over time; use the [AWS Pricing Calculator](https://calculator.aws/) for your region and usage.
