#!/usr/bin/env python
import sys
from pathlib import Path
from dotenv import load_dotenv
from django.core.management.utils import get_random_secret_key

load_dotenv()

def setup_env():
    env_example_path = Path('.') / '.env.example'
    env_path = Path('.') / '.env'

    if env_path.exists():
        print(".env file already exists. Exiting.")
        return

    if not env_example_path.exists():
        print(".env.example file not found. Exiting.")
        return

    secret_key = get_random_secret_key()

    with open(env_example_path, 'r') as example_file:
        env_content = example_file.readlines()

    with open(env_path, 'w') as env_file:
        for line in env_content:
            key_value = line.strip().split('=', 1)
            if key_value[0] == 'SECRET_KEY':
                env_file.write(f'SECRET_KEY={secret_key}\n')
            else:
                env_file.write(key_value[0] + '=' + key_value[1].split('#')[0].strip() + '\n')

    print(".env file created with a new SECRET_KEY and other values from .env.example.")

# Make sure DJANGO_SETTINGS_MODULE is added to .env file
def main():
    if 'setup_env' in sys.argv:
        setup_env()
        sys.argv.remove('setup_env')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
