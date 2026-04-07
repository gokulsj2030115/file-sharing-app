import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from config import Config

class S3Service:
    def __init__(self):
        # Implicitly uses IAM Role credentials on EC2
        self.s3 = boto3.client('s3', region_name=Config.S3_REGION)
        self.bucket_name = Config.S3_BUCKET

    def upload_file(self, file_obj, filename, content_type):
        try:
            self.s3.upload_fileobj(
                file_obj,
                self.bucket_name,
                filename,
                ExtraArgs={'ContentType': content_type}
            )
            return True
        except ClientError as e:
            print(f"Error uploading file: {e}")
            return False

    def list_files(self):
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name)
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'name': obj['Key'],
                        'last_modified': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
                        'size': self._format_bytes(obj['Size'])
                    })
            return sorted(files, key=lambda x: x['last_modified'], reverse=True)
        except ClientError as e:
            print(f"Error listing files: {e}")
            return []

    def get_presigned_url(self, filename, expiration=3600):
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': filename},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None

    def _format_bytes(self, size):
        # Helper to convert bytes to human-readable format
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
