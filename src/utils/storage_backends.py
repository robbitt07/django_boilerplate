from django.conf import settings
from django.core.files.storage import FileSystemStorage

from storages.backends.s3boto3 import S3Boto3Storage

if settings.USE_DO_SPACES:

	class StaticStorage(S3Boto3Storage):
		location = settings.AWS_STATIC_LOCATION
		default_acl = "public-read"
		file_overwrite = True
		querystring_auth = False
		
	class PublicMediaStorage(S3Boto3Storage):
		location = settings.AWS_PUBLIC_MEDIA_LOCATION
		default_acl = "public-read"
		file_overwrite = False


	class PrivateMediaStorage(S3Boto3Storage):
		location = settings.AWS_PRIVATE_MEDIA_LOCATION
		default_acl = "private"
		file_overwrite = True
		custom_domain = False


	class PrivateDataStorage(S3Boto3Storage):
		location = "yat-data" # Override settings config
		default_acl = "private"
		file_overwrite = True
		custom_domain = False

else:
	
	class StaticStorage(FileSystemStorage):
		pass


	class PublicMediaStorage(FileSystemStorage):
		pass


	class PrivateMediaStorage(FileSystemStorage):
		pass


	class PrivateDataStorage(FileSystemStorage):
		pass