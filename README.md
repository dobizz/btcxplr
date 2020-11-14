# btcxplr
Bitcoin Block Explorer

## Requirements
1. Install required packages with pip
```
pip3 install -r requirements.txt
```

2. [A fully synced Bitcoin Full Node running the bitcoind service](https://bitcoin.org/en/full-node) installed in the same system or in any network that is reachable from your host.

3. `BTC_RPC_USER` and `BTC_RPC_PASS` must be present in the system environment and contains the correct credentials to make RPC calls to your bitcoin full node.

4. Ports for HTTP, HTTPS, and RPC should be allowed in your firewall rules.
Example for `ufw`
```
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8332:8333
```

## Deployment
### Flask
```
python3 run.py
```

### Gunicorn
```
gunicorn --bind 0.0.0.0:5000 run:app
```

### Gunicorn + Nginx
Create a unit file ending in .service within the `/etc/systemd/system` directory
```
sudo vim /etc/systemd/system/btcxplr.service
```

Sample contents of unit file 
```
[Unit]
#  specifies metadata and dependencies
Description=Gunicorn instance to serve btcxplr

# tells the init system to only start this after the networking target has been reached
After=network.target

[Service]
# Service specify the user and group under which our process will run.
User=<replace with username>

# Give group ownership to the www-data group so that Nginx can communicate easily with the Gunicorn processes.
Group=www-data

# Specify the working directory and set the PATH environmental variable so that the init system knows where our the executables for the process are located (within our virtual environment).
WorkingDirectory=<replace with path to btcxplr>
Environment="PATH=<replace with path to btcxplr virtual environment>"

# Specify the commanded to start the service
# Rule of thumb for number of workers is twice the number of cores plus one
# Example for a dual core system, the ideal number of workers is five (5).
ExecStart=<replace with path to gunicorn> --workers <replace with number of workers> --bind unix:app.sock -m 007 run:app

[Install]
# This will tell systemd what to link this service to if we enable it to start at boot. We want this service to start when the regular multi-user system is up and running:
WantedBy=multi-user.target
```

Start the Gunicorn service we created
```
sudo systemctl start btcxplr
```

Enable the service so that it starts at boot
```
sudo systemctl enable btcxplr
```

A new `app.sock` file will be created inside the btcxplr directory automatically

Create a new server block configuration file in Nginx’s sites-available directory named `btcxplr`
```
sudo vim /etc/nginx/sites-available/btcxplr
```

Open up a server block in which nginx will listen to `PORT 80`. This block will also be used for requests for the server’s domain name or IP address
```
server {
    listen 80;
    server_name <replace with server ip or domain name>;
}
```

Add a location block that matches every request. In this block, include the `proxy_paramsfile` that specifies some general proxying parameters that need to be set. Then pass the requests to the socket defined earlier using the `proxy_pass` directive
```
server {
    listen 80;
    server_name <replace with server ip or domain name>;

    location / {
      include proxy_params;
      # replace with path to btcxplr app.sock file
      proxy_pass http://unix:/home/username/btcxplr/app.sock;
        }
}
```

Create a symbolic link inside the `sites-enabled` directory to enable Nginx server block just created.
```
sudo ln -s /etc/nginx/sites-available/btcxplr /etc/nginx/sites-enabled/btcxplr
```

Test syntax errors by typing
```
sudo nginx -t
``` 

If there is no issues, restart the Nginx process to load new config
```
sudo systemctl restart nginx
```

If firewall rules are not yet updated to allow `HTTP` and `HTTPS`.
Example for `ufw`
```
sudo ufw allow 'Nginx Full'
```

You may now access `btcxplr` by keying your ip address or domain name in your web browser.
```
http://server_domain_or_ip_address
```

##### Optional HTTPS
To enable `HTTPS` using certificates, you can use [Certbot](https://certbot.eff.org/) and create a `HTTP 301` redirect from `PORT 80` to `PORT 443` in your server configuration in nginx.

Example server block configuration
```
server {
  server_name <your_server_domain>;

  location / {
    include proxy_params;
    # replace with path to btcxplr app.sock file
    proxy_pass http://unix:/home/username/btcxplr/app.sock;
  }

  listen 443 ssl; # managed by Certbot
  ssl_certificate /etc/letsencrypt/live/<your_server_domain>/fullchain.pem; # managed by Certbot
  ssl_certificate_key /etc/letsencrypt/live/<your_server_domain>/privkey.pem; # managed by Certbot
  include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
  ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

server {
    if ($host = <your_server_domain>) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    listen 80;
    server_name <your_server_domain>;
    return 404; # managed by Certbot
}
```

You may now securely access `btcxplr` by keying your ip address or domain name in your web browser.
```
https://server_domain_or_ip_address
```
Keying in the url with `http://server_domain_or_ip_address` will automatically redirect users to `https://server_domain_or_ip_address`.
