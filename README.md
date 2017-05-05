# How to run

## Install Federated Cloud User Interface

```
wget https://raw.githubusercontent.com/EGI-FCTF/fedcloud-userinterface/master/fedcloud-ui.sh
chmod +x fedcloud-ui.sh
sudo ./fedcloud-ui.sh
```

## Install python requirements in a virtualenv

```
virtualenv ~/venv/vmmon
source ~/venv/vmmon/bin/activate
pip install -r requiremnts.txt
```

## Configure application

Edit config.py to include some secret `SECRET_KEY`

## Local testing

```
source ~/venv/vmmon/bin/activate
export FLASK_APP=run.py
flask run --host=0.0.0.0
```

## nginx and systemd-based setup

See https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-16-04 for details.


### Preparing for uwsgi

Logs will go to a logs directory under the project root.

```
source ~/venv/vmmon/bin/activate
pip install -r requiremnts-nginx.txt
mkdir logs
```

### uwsgi systemd service

* Create `/etc/systemd/system/vmmon.service` using provided vmmon.service
  template.
* Edit, enable and start vmmon systemd service

```
sudo systemctl edit --full vmmon.service
sudo systemctl enable vmmon.service
sudo systemctl start vmmon.service
```

### nginx setup

* Create an nginx virtualhost using provided vmmon.conf template.

  * For HTTPS using a Let's Encrypt certificate see commented directives and
    https://certbot.eff.org

* Validate nginx configuration and restart it

```
sudo nginx -t
sudo systemctl restart nginx
```
