# Deploying to Heroku

This guide walks through deploying the Django application to Heroku with PostgreSQL.

## Initial Login and Setup

1. First, ensure you're logged into the Heroku CLI:
   ```bash
   heroku login
   ```

2. Check if you're already connected to the app:
   ```bash
   heroku apps:info -a <your_app_name>
   ```

3. If you're not connected, add the remote:
   ```bash
   heroku git:remote -a <your_app_name>
   ```

## Configure Environment Variables

Transfer your current environment variables to Heroku:

```bash
heroku config:set DJANGO_SETTINGS_MODULE=app.settings -a <your_app_name>
heroku config:set SECRET_KEY=<your-secret-key> -a <your_app_name>
heroku config:set DEBUG=False -a <your_app_name>
heroku config:set ALLOWED_HOSTS="<your_app_name>.herokuapp.com" -a <your_app_name>
heroku config:set USE_SQLITE=False -a <your_app_name>

# AWS S3 settings
heroku config:set USE_CLOUD=True -a <your_app_name>
heroku config:set AWS_ACCESS_KEY_ID=<your-aws-key> -a <your_app_name>
heroku config:set AWS_SECRET_ACCESS_KEY=<your-aws-secret> -a <your_app_name>
heroku config:set AWS_STORAGE_BUCKET_NAME=<your-bucket-name> -a <your_app_name>

# OpenAI
heroku config:set OPENAI_API_KEY=<your-openai-key> -a <your_app_name>
```

## Database Setup

1. Verify PostgreSQL addon is installed:
   ```bash
   heroku addons:info heroku-postgresql -a <your_app_name>
   ```

2. If not installed, create it:
   ```bash
   heroku addons:create heroku-postgresql:mini -a <your_app_name>
   ```

3. Push your code to Heroku:
   ```bash
   git push heroku main
   ```

4. Run migrations:
   ```bash
   heroku run python manage.py migrate -a <your_app_name>
   ```

5. Load a local database backup (if you have one):
   ```bash
   psql <postgres_url>
   \i db_backup.sql
   ```

## Verify Deployment

1. Open your application:
   ```bash
   heroku open -a <your_app_name>
   ```

2. Check logs if needed:
   ```bash
   heroku logs --tail -a <your_app_name>
   ```

## Common Issues and Solutions

### Database Connection Issues
- Verify database URL: `heroku config:get DATABASE_URL -a <your_app_name>`
- Check database status: `heroku pg:info -a <your_app_name>`

### Static Files Missing
- Ensure AWS S3 credentials are correct
- Verify static files were collected: `heroku run python manage.py collectstatic --noinput -a <your_app_name>`

### Application Errors
- Check logs: `heroku logs --tail -a <your_app_name>`
- Verify all environment variables are set: `heroku config -a <your_app_name>`

## Useful Commands

- Scale dynos: `heroku ps:scale web=1 -a <your_app_name>`
- Run Django shell: `heroku run python manage.py shell -a <your_app_name>`
- Database shell: `heroku pg:psql -a <your_app_name>`
- Restart application: `heroku restart -a <your_app_name>`


Remember to never commit sensitive information like API keys or credentials to version control. Always use environment variables for sensitive data.

## Custom Domain Configuration

1. Current domains setup:
   ```bash
   heroku domains -a <your_app_name>
   ```
   Shows:
   - <your_app_name>.com -> cardiovascular-river-a9hrkazn27kyro8bm1...
   - www.<your_app_name>.com -> fierce-whale-tw5is3mas1ivyb63kt71222l.jke...

2. For new domains, add them using:
   ```bash
   heroku domains:add <your_app_name>.com -a <your_app_name>
   heroku domains:add www.<your_app_name>.com -a <your_app_name>
   ```

3. Configure DNS with your domain provider:
   - For <your_app_name>.com: Add a DNS target pointing to `cardiovascular-river-a9hrkazn27kyro8bm1...`
   - For www.<your_app_name>.com: Add a CNAME record pointing to `fierce-whale-tw5is3mas1ivyb63kt71222l.jke...`

4. Verify DNS configuration:
   ```bash
   heroku domains:wait -a <your_app_name>
   ```

5. Update ALLOWED_HOSTS:
   ```bash
   heroku config:set ALLOWED_HOSTS="<your-heroku-domain> <your-custom-domain> www.<your-custom-domain>" -a <your_app_name>
   ```

6. SSL should be automatically enabled, but verify with:
   ```bash
   heroku certs:auto -a <your_app_name>
   ```

## Namecheap DNS Configuration

1. Log into Namecheap and go to Domain List
2. Click "Manage" next to <your_app_name>.com
3. Go to the "Advanced DNS" tab
4. Configure the following records:

For www subdomain:
- Type: CNAME Record
- Host: www
- Value: cardiovascular-river-a9hrkazn27kyro8bm1ffx4a5.herokudns.com
- TTL: 30 min

For root domain (@):
- Type: CNAME Record
- Host: @
- Value: cardiovascular-river-a9hrkazn27kyro8bm1ffx4a5.herokudns.com
- TTL: 30 min

Important Notes:
- It may take up to 24-48 hours for DNS changes to fully propagate
- You can verify DNS propagation using:
  ```bash
  dig <your_app_name>.com
  dig www.<your_app_name>.com
  ```


## Export prod database and restore locally

TODO
