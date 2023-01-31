#!/bin/bash

# Define the backup directories
DAILY_DIR=~/Documents/code/blogthedata/backups/daily
WEEKLY_DIR=~/Documents/code/blogthedata/backups/weekly
MONTHLY_DIR=~/Documents/code/blogthedata/backups/monthly

# Define the number of daily backups to keep
DAILY_BACKUPS_TO_KEEP=7

# Define the number of weekly backups to keep
WEEKLY_BACKUPS_TO_KEEP=4

# Define the number of monthly backups to keep
MONTHLY_BACKUPS_TO_KEEP=12

# Clean up old daily backups
find $DAILY_DIR -type f -mtime +$DAILY_BACKUPS_TO_KEEP -exec rm {} \;

# Clean up old weekly backups
find $WEEKLY_DIR -type f -mtime +$(($DAILY_BACKUPS_TO_KEEP * 7 + $WEEKLY_BACKUPS_TO_KEEP)) -exec rm {} \;

# Clean up old monthly backups
find $MONTHLY_DIR -type f -mtime +$(($DAILY_BACKUPS_TO_KEEP * 7 + $WEEKLY_BACKUPS_TO_KEEP * 4 + $MONTHLY_BACKUPS_TO_KEEP * 30)) -exec rm {} \;
