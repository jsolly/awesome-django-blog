server {
    listen ${LISTEN_PORT};

    location /static {
        alias /app/static;
    }


    location / {
        uwsgi_pass              ${APP_HOST}:${APP_PORT};
        include                 /etc/nginx/uwsgi_params;
        cleint_max_body_size    100M;

    
}