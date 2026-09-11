from django.test import TestCase
from django.conf import settings

class DeploymentReadinessTest(TestCase):
    def test_whitenoise_installed_for_static_files(self):
        self.assertIn(
            'whitenoise.middleware.WhiteNoiseMiddleware', 
            settings.MIDDLEWARE, 
            'Whitenoise is missing from MIDDLEWARE'
        )

    def test_database_url_support(self):
        try:
            import dj_database_url
        except ImportError:
            self.fail('dj_database_url is not installed, which is required for Render/Supabase DATABASE_URL parsing')
