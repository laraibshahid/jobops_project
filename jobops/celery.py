import os

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobops.settings')

try:
    from celery import Celery
    
    app = Celery('jobops')
    
    # Using a string here means the worker doesn't have to serialize
    # the configuration object to child processes.
    app.config_from_object('django.conf:settings', namespace='CELERY')
    
    # Load task modules from all registered Django apps.
    app.autodiscover_tasks()
    
    @app.task(bind=True)
    def debug_task(self):
        print(f'Request: {self.request!r}')
        
except ImportError:
    # Celery not available, create a dummy app
    app = None 