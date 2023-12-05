from storages.backends.s3boto3 import S3Boto3Storage

from django_app.settings import AWS_CLOUDFRONT_DOMAIN


class MediaStorage(S3Boto3Storage):
    """uploads to 'mybucket/media/', serves from 'cloudfront.net/media/'"""

    location = 'media'
    file_overwrite = True
    default_acl = 'public-read'

    def __init__(self, *args, **kwargs):
        kwargs['custom_domain'] = AWS_CLOUDFRONT_DOMAIN
        super(MediaStorage, self).__init__(*args, **kwargs)
