#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        from dotenv import load_dotenv

        # Local development uses this project's explicit environment settings.
        env_file = Path(os.getenv('TEACHTRACK_ENV_FILE') or '.env')
        if not env_file.is_absolute():
            env_file = Path(__file__).resolve().parent / env_file
        load_dotenv(env_file, override=True)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Classroom.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
