import boto3
from botocore.exceptions import ClientError
from config import Config

class S3Service:
    def __init__(self):
        # Uses IAM Role credentials on EC2 or local 'aws configure'
        self.s3 = boto3.client('s3', region_name=Config.S3_REGION)
        self.bucket_name = Config.S3_BUCKET

    def check_connection(self):
        """Verifies S3 connection by attempting to head the bucket."""
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError:
            return False

    def get_bucket_stats(self, capacity_gb=5.0):
        """Calculates total size and percentage used."""
        try:
            paginator = self.s3.get_paginator('list_objects_v2')
            total_size = 0
            count = 0
            for page in paginator.paginate(Bucket=self.bucket_name):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        total_size += obj['Size']
                        count += 1
            
            used_gb = total_size / (1024**3)
            percent = (used_gb / capacity_gb) * 100 if capacity_gb > 0 else 0
            
            return {
                'used_gb': round(used_gb, 2),
                'total_gb': capacity_gb,
                'percent': min(round(percent, 1), 100),
                'count': count,
                'formatted_size': self._format_bytes(total_size)
            }
        except Exception as e:
            print(f"Stats Error: {e}")
            return {'used_gb': 0, 'total_gb': capacity_gb, 'percent': 0, 'count': 0, 'formatted_size': '0 B'}

    def get_recent_files(self, limit=7):
        """Fetches the 7 most recently modified files across the entire bucket."""
        try:
            # List all objects without delimiter to get a flat list
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, MaxKeys=50) # Initial Fetch
            all_files = []
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Skip folder placeholders
                    if obj['Key'].endswith('/'):
                        continue
                    
                    all_files.append({
                        'name': obj['Key'].split('/')[-1],
                        'full_path': obj['Key'],
                        'last_modified': obj['LastModified'],
                        'size': self._format_bytes(obj['Size']),
                        'is_image': self._is_image(obj['Key'])
                    })
            
            # Sort by LastModified descending
            sorted_files = sorted(all_files, key=lambda x: x['last_modified'], reverse=True)
            
            # Format date for template
            for f in sorted_files:
                f['last_modified_str'] = f['last_modified'].strftime('%d %b, %H:%M')
                
            return sorted_files[:limit]
        except Exception as e:
            print(f"Recent Files Error: {e}")
            return []

    def upload_file(self, file_obj, filename, content_type, prefix=''):
        try:
            # Ensure file is uploaded to the correct prefix
            full_key = f"{prefix}{filename}" if prefix else filename
            self.s3.upload_fileobj(
                file_obj,
                self.bucket_name,
                full_key,
                ExtraArgs={'ContentType': content_type}
            )
            return True
        except ClientError as e:
            print(f"S3 Upload Error: {e}")
            return False

    def list_files(self, prefix=''):
        try:
            # Use Delimiter='/' to simulate folders
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                Delimiter='/'
            )
            
            folders = []
            files = []

            # 1. Extract Folders (CommonPrefixes)
            if 'CommonPrefixes' in response:
                for cp in response['CommonPrefixes']:
                    folders.append({
                        'name': cp['Prefix'].split('/')[-2] + '/',
                        'full_path': cp['Prefix'],
                        'is_folder': True
                    })

            # 2. Extract Files (Contents)
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Skip the current folder's placeholder object and empty prefixes
                    if obj['Key'] == prefix:
                        continue
                    
                    files.append({
                        'name': obj['Key'].split('/')[-1],
                        'full_path': obj['Key'],
                        'last_modified': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
                        'size': self._format_bytes(obj['Size']),
                        'is_image': self._is_image(obj['Key']),
                        'is_folder': False
                    })
            
            # Combine: Folders first, then Files
            return folders + sorted(files, key=lambda x: x['last_modified'], reverse=True)
        except ClientError as e:
            print(f"S3 List Error: {e}")
            return []

    def create_folder(self, folder_name, prefix=''):
        try:
            # Ensure folder name ends with /
            if not folder_name.endswith('/'):
                folder_name += '/'
            
            full_key = f"{prefix}{folder_name}" if prefix else folder_name
            self.s3.put_object(Bucket=self.bucket_name, Key=full_key)
            return True
        except ClientError as e:
            print(f"S3 Create Folder Error: {e}")
            return False

    def copy_object(self, source_key, destination_key):
        """Helper to copy an object in S3."""
        try:
            copy_source = {'Bucket': self.bucket_name, 'Key': source_key}
            self.s3.copy_object(CopySource=copy_source, Bucket=self.bucket_name, Key=destination_key)
            return True
        except ClientError as e:
            print(f"S3 Copy Error: {e}")
            return False

    def move_to_trash(self, key):
        """Moves an object to the trash/ prefix."""
        try:
            trash_key = f"trash/{key}"
            if self.copy_object(key, trash_key):
                self.s3.delete_object(Bucket=self.bucket_name, Key=key)
                return True
            return False
        except ClientError as e:
            print(f"S3 Move to Trash Error: {e}")
            return False

    def restore_from_trash(self, trash_key):
        """Moves an object from the trash/ prefix back to its original path."""
        try:
            original_key = trash_key.replace('trash/', '', 1)
            if self.copy_object(trash_key, original_key):
                self.s3.delete_object(Bucket=self.bucket_name, Key=trash_key)
                return True
            return False
        except ClientError as e:
            print(f"S3 Restore Error: {e}")
            return False

    def delete_recursive(self, prefix):
        """Deletes all objects with a given prefix (effectively deleting a folder)"""
        try:
            # 1. List all objects with the prefix
            paginator = self.s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)

            delete_batch = []
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        delete_batch.append({'Key': obj['Key']})
                
                # Delete in batches of 1000 (S3 limit)
                if len(delete_batch) >= 1000:
                    self.s3.delete_objects(
                        Bucket=self.bucket_name,
                        Delete={'Objects': delete_batch}
                    )
                    delete_batch = []

            # Delete remaining
            if delete_batch:
                self.s3.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': delete_batch}
                )
            return True
        except ClientError as e:
            print(f"S3 Recursive Delete Error: {e}")
            return False

    def delete_file(self, filename):
        """Permanently deletes an object."""
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=filename)
            return True
        except ClientError as e:
            print(f"S3 Delete Error: {e}")
            return False

    def get_presigned_url(self, filename, expiration=3600, inline=False):
        try:
            # If inline is True, the file will open in the browser instead of downloading
            disposition = 'inline' if inline else f'attachment; filename="{filename.split("/")[-1]}"'
            
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name, 
                    'Key': filename,
                    'ResponseContentDisposition': disposition
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"S3 Presign Error: {e}")
            return None

    def _format_bytes(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0: return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def _is_image(self, filename):
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        return ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']
