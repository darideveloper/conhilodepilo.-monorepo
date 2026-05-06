from django.test import TestCase, RequestFactory
from django.conf import settings

class SecuritySettingsTest(TestCase):
    def test_secure_proxy_ssl_header_configuration(self):
        """
        Verify that SECURE_PROXY_SSL_HEADER is correctly configured in settings.
        """
        self.assertEqual(settings.SECURE_PROXY_SSL_HEADER, ("HTTP_X_FORWARDED_PROTO", "https"))

    def test_is_secure_with_proxy_header(self):
        """
        Verify that request.is_secure() returns True when the X-Forwarded-Proto header is present.
        """
        factory = RequestFactory()
        
        # Test with https header
        request_secure = factory.get('/', HTTP_X_FORWARDED_PROTO='https')
        self.assertTrue(request_secure.is_secure())
        
        # Test with http header
        request_insecure = factory.get('/', HTTP_X_FORWARDED_PROTO='http')
        self.assertFalse(request_insecure.is_secure())
        
        # Test without header
        request_no_header = factory.get('/')
        self.assertFalse(request_no_header.is_secure())
