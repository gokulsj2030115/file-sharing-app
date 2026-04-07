# S3 Storage Hub Setup Guide

This guide covers the necessary steps to deploy and run the **S3 Storage Hub** on AWS EC2 with IAM roles, or locally for development.

## 1. AWS Configuration (Production)

### S3 Bucket
1. Create an S3 bucket (e.g., `s3-storage-hub-prod`).
2. Keep all public access blocked (the app uses backend access).

### IAM Role (EC2)
Instead of using Access Keys, attach an IAM Role to your EC2 instance:
1. Go to **IAM Console** > **Roles** > **Create role**.
2. Select **AWS Service** and choose **EC2**.
3. Attach the `AmazonS3FullAccess` policy (or a custom scoped policy).
4. Name it `S3StorageHubRole`.
5. Attach the role to your EC2 instance (**Actions** > **Security** > **Modify IAM role**).

## 2. Local Setup (Development)

### Prerequisites
- Python 3.9+
- AWS CLI configured (`aws configure`) or `.env` file.

### Installation
1. Clone the repository to your machine/EC2.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Variables
Create a `.env` file in the root directory:
```env
S3_BUCKET=your-bucket-name
S3_REGION=ap-south-1
SECRET_KEY=your-random-secret
```

## 3. Running the App

### Development Mode
```bash
python app.py
```
The app will be available at `http://localhost:5000`.

### Production Mode (Gunicorn)
On EC2, use Gunicorn for better performance:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 4. Troubleshooting & Debugging

- **Permissions Error**: Ensure the IAM Role has `s3:ListBucket`, `s3:PutObject`, `s3:DeleteObject`, and `s3:GetObject` permissions.
- **Prefix Issues**: If folders aren't appearing, check if there are zero-byte objects with a trailing slash in S3.
- **Empty Folders**: S3 doesn't have "real" folders. Deleting a "folder" in this app recursively deletes all objects with that prefix.
- **Large Files**: Adjust `MAX_CONTENT_LENGTH` in `config.py` if you need to upload files larger than 16MB.

---
**S3 Storage Hub** - Built for high-performance cloud file management.
