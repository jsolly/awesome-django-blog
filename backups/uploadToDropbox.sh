#!/bin/bash

# Load the environment variables from .env
source $(dirname "$0")/../.env

# Set the date for the backup file
DATE=$(date +"%d_%m_%Y")

# Define the backup directory
BACKUP_DIR=$(dirname "$0")/..

# Zip up the backups directory
zip -r $BACKUP_DIR/backups.zip $BACKUP_DIR/backups

# Upload the zipped file to Dropbox
curl -X POST https://content.dropboxapi.com/2/files/upload \
    --header "Authorization: Bearer $DROPBOX_ACCESS_TOKEN" \
    --header "Dropbox-API-Arg: {\"path\": \"/backups_$DATE.zip\",\"mode\": \"overwrite\",\"autorename\": false,\"mute\": false}" \
    --header "Content-Type: application/octet-stream"
