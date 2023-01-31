#!/bin/bash

# Set the date for the backup file
DATE=$(date +"%d_%m_%Y")

# Define the backup directories
DAILY_DIR=~/Documents/code/blogthedata/backups/daily
WEEKLY_DIR=~/Documents/code/blogthedata/backups/weekly
MONTHLY_DIR=~/Documents/code/blogthedata/backups/monthly

# Run pg_dump on the remote machine and send the output directly to the host machine
ssh john@198.74.48.211 "sudo -u postgres pg_dump blogthedata" > $DAILY_DIR/blogthedata_db_$DATE.sql

# Check if it's the 7th day of the month
if [ $(date +\%d -d tomorrow) -eq 7 ]
then
  cp $DAILY_DIR/blogthedata_db_$DATE.sql $WEEKLY_DIR/blogthedata_db_$DATE.sql
fi

# Check if it's the 1st day of the month
if [ $(date +\%d) -eq 1 ]
then
  cp $DAILY_DIR/blogthedata_db_$DATE.sql $MONTHLY_DIR/blogthedata_db_$DATE.sql
fi