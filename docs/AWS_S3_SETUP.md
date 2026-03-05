# Configure AWS S3 for Scholarvalley

The app uses **Amazon S3** for document uploads (transcript, degree, etc.). Users upload files via **presigned URLs**: the API generates a temporary URL; the browser uploads directly to S3.

You need:

1. An **S3 bucket**
2. **IAM credentials** with permission to put/get objects in that bucket
3. **CORS** on the bucket so the browser can send `PUT` requests from your frontend origin
4. **Environment variables** so the API can generate presigned URLs

---

## Option A: Manual setup (AWS Console)

### 1. Create an S3 bucket

1. Open [AWS Console → S3](https://s3.console.aws.amazon.com/s3/).
2. **Create bucket**.
3. Choose a **name** (e.g. `scholarvalley-docs-YOUR_ACCOUNT_ID`) and **region** (e.g. `us-east-1`).
4. Leave default settings (block public access on). Create bucket.

### 2. Add CORS for browser uploads

Without CORS, the browser will block `PUT` requests from your site to S3.

1. In S3, open your bucket → **Permissions** tab.
2. Scroll to **Cross-origin resource sharing (CORS)** → **Edit**.
3. Use a config like this (replace `http://localhost:8000` with your frontend URL if different):

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "HEAD"],
    "AllowedOrigins": ["http://localhost:8000", "https://yourdomain.com"],
    "ExposeHeaders": []
  }
]
```

4. Save.

### 3. Create IAM credentials for the app

1. Open [IAM → Users](https://console.aws.amazon.com/iam/home#/users) → **Create user** (e.g. `scholarvalley-app`).
2. **Attach policies directly** → **Create policy** (or use a custom policy).
3. Use this policy (replace `YOUR-BUCKET-NAME` with your bucket name):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::YOUR-BUCKET-NAME",
        "arn:aws:s3:::YOUR-BUCKET-NAME/*"
      ]
    }
  ]
}
```

4. Create the policy, attach it to the user.
5. **Create access key** for the user (use “Application running outside AWS” if asked). Save the **Access key ID** and **Secret access key**.

### 4. Set environment variables

In your project root, create or edit **`.env`**:

```bash
# Required for document uploads
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1

# Credentials (for local / Docker). On ECS, the task role is used instead.
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

- **Bucket name**: the exact name from step 1.
- **Region**: the bucket’s region (e.g. `us-east-1`).
- **Credentials**: the access key and secret from step 3.  
  If you already use `aws configure`, the app can use that; in Docker you must pass these in `.env` or in `docker-compose` `environment`.

### 5. Restart the app

```bash
docker compose down
docker compose up -d
```

Then try **Register** again with transcript and degree files; upload should succeed.

---

## Option B: Use Terraform (infra already defines S3)

If you deploy with the project’s Terraform in `infra/`:

1. Run `terraform apply` (see `infra/README.md`). Terraform creates the S3 bucket and gives the ECS task role access.
2. For **local/Docker** dev, you still need credentials that can access that bucket:
   - Create an IAM user (or use an existing one) with the same S3 policy as in Option A, using the Terraform bucket name.
   - Put `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET`, and `AWS_REGION` in `.env` as in step 4 above.
3. Bucket **CORS** is now defined in Terraform (see `infra/main.tf`). After `terraform apply`, browser uploads from the allowed origins will work.

---

## Checklist

| Item | Done |
|------|------|
| S3 bucket created | ☐ |
| CORS set on bucket (PUT from your frontend origin) | ☐ |
| IAM user/keys with `s3:PutObject`, `s3:GetObject`, `s3:ListBucket` | ☐ |
| `.env` has `AWS_S3_BUCKET`, `AWS_REGION`, and (for local) `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | ☐ |
| App restarted (`docker compose up -d`) | ☐ |

---

## Troubleshooting

- **“Failed to generate presigned URL”**  
  Check: bucket name correct, credentials in `.env`, and IAM policy allows `s3:PutObject` (and the bucket exists in that account/region).

- **CORS error in browser when uploading**  
  Add your frontend origin (e.g. `http://localhost:8000`) to the bucket CORS **AllowedOrigins** and ensure **AllowedMethods** includes `PUT`.

- **Docker can’t see AWS credentials**  
  Either put `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `.env` (and use `env_file: [.env]` in `docker-compose`), or mount `~/.aws` into the container (not recommended for production).
