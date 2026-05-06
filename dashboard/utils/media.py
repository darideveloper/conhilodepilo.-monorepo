import os
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import serializers

def get_media_url(object_or_url: object) -> str:
    url_str = ""
    if type(object_or_url) is str:
        url_str = object_or_url
    else:
        url_str = object_or_url.url

    if "s3.amazonaws.com" not in url_str and "digitaloceanspaces" not in url_str:
        return f"{settings.HOST}{url_str}"
    return url_str

class AbsoluteImageField(serializers.ImageField):
    def to_representation(self, value):
        if not value:
            return None
        
        # If HOST is set, use the specialized utility
        if getattr(settings, 'HOST', None):
            return get_media_url(value)
            
        # Fallback to default DRF behavior (request-based) if HOST is missing
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(value.url)
        return value.url

def get_test_image(image_name: str = "test.webp") -> SimpleUploadedFile:
    app_path = os.path.dirname(os.path.abspath(__file__))
    project_path = os.path.dirname(app_path)
    media_path = os.path.join(project_path, "media")

    image_path = os.path.join(media_path, image_name)
    image_file = SimpleUploadedFile(
        name=image_name,
        content=open(image_path, "rb").read(),
        content_type="image/webp",
    )
    return image_file
