# AWS Infrastructure Setup Guide

To run this application on AWS EC2 with S3 connectivity, follow these steps. We recommend using the **ap-south-1 (Mumbai)** region.

## 1. S3 Bucket Setup
1. Log in to the [AWS S3 Console](https://s3.console.aws.amazon.com/).
2. Click **Create bucket**.
3. **Bucket name**: `my-devops-files-mumbai` (must be globally unique).
4. **AWS Region**: `ap-south-1`.
5. Keep **"Block all public access"** checked (Safety first! Pre-signed URLs bypass this securely).
6. Click **Create bucket**.

## 2. IAM Role for EC2
We use IAM Roles so we never have to hardcode AWS Access Keys.
1. Open the [IAM Console](https://console.aws.amazon.com/iam/).
2. Click **Roles** > **Create role**.
3. Select **AWS service** and the use case **EC2**.
4. Search for and check **`AmazonS3FullAccess`**. 
   - *Production Tip*: In a real company, you'd create a "Least Privilege" policy restricted to just your bucket.
5. Name the role: `EC2S3AccessRole`.
6. Click **Create role**.

## 3. Launch EC2 Instance
1. Open the [EC2 Console](https://console.aws.amazon.com/ec2/).
2. Click **Launch Instance**.
3. **AMI**: Ubuntu 22.04 LTS (Free Tier eligible).
4. **Instance Type**: `t2.micro`.
5. **Key pair**: Create/Select your SSH key.
6. **Network Settings**:
   - Allow **SSH** (Port 22) from your IP.
   - Allow **HTTP** (Port 80) from anywhere.
7. **Advanced Details**:
   - **IAM instance profile**: Select `EC2S3AccessRole` (Crucial step!).
8. Click **Launch instance**.

## 4. Security Group (Port 80)
Ensure your Security Group has an **Inbound Rule** for:
- Type: HTTP
- Protocol: TCP
- Port Range: 80
- Source: 0.0.0.0/0 (Everywhere)

---

## 5. Deployment Commands on EC2
Once SSH'd into your EC2 instance, run these:

```bash
# Update and install dependencies
sudo apt update && sudo apt install python3-pip python3-venv git -y

# Clone your project (assuming you pushed to GitHub)
git clone <your-repo-url>
cd <your-repo-name>

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file for configuration
echo "S3_BUCKET=my-devops-files-mumbai" > .env
echo "S3_REGION=ap-south-1" >> .env

# Run using Gunicorn (Production Server) on Port 80
sudo venv/bin/gunicorn --bind 0.0.0.0:80 app:app
```
