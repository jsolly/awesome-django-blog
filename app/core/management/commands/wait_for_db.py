from time import sleep
from psycopg.errors import OperationalError as PsycopgOperationalError
from django.core.management.base import BaseCommand
import logging

MAX_RETRIES = 30


class Command(BaseCommand):
    help = "Waits until database is available"
    logger = logging.getLogger("django")

    def handle(self, *args, **options):
        self.logger.info("Waiting for database...")
        retries = 0
        db_up = False
        while not db_up and retries < MAX_RETRIES:
            try:
                self.check(databases=["default"])
                db_up = True
            except PsycopgOperationalError as e:
                self.logger.warning(
                    f"Database unavailable, waiting 1 second... Error: {e}"
                )
                sleep(1)
                retries += 1

        if db_up:
            self.logger.info("Database is ready!")
        else:
            self.logger.error(
                "Database is not available after maximum retries. Exiting."
            )
