import csv
import hashlib
import json
import time
from subprocess import check_output, Popen, PIPE, STDOUT, CalledProcessError

from app import app

def update_resources(endpoint, proxy, res_file):
    args = {"endpoint": endpoint, "proxy": proxy}
    cmd = ('occi -X -o json_extended -e %(endpoint)s -x %(proxy)s -n x509 '
           '-a describe -r compute') % args
    try:
        print cmd.split()
        out = check_output(cmd.split(), shell=False)
        vms = json.loads(out)
    except CalledProcessError as e:
        print "PUM!"
        print e
        return
    except ValueError:
        print "PUM!"
        print e
        return

    r = []
    with open(res_file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            r.append({"time": row[0], "vms": row[1], "cpus": row[2], "mem": row[3]})

    row = [time.time(), len(vms), 
           sum([v['attributes']['occi']['compute']['cores'] for v in vms]),
           sum([v['attributes']['occi']['compute']['memory'] for v in vms])]

    r.append({
        "time": row[0],
        "vms":  row[1],
        "cpus": row[2],
        "mem": row[3],
    })

    with open(res_file, 'a+') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(row)
    return r

def create_user(username, passwd):
    m = hashlib.sha256()
    m.update(username)
    # m.update(passwd)
    user_id = m.hexdigest()

    server = app.config['MYPROXY_SERVER']
    vo = app.config['VO']
    try:
        # Check that we have valid proxy
        out = check_output(['voms-proxy-info', '-e', '-file', '/tmp/%s' % user_id])
    except CalledProcessError as e:
        # Get new one
        cmd = 'myproxy-logon -l %s -s %s -m %s -o /tmp/%s -S' % (username, server, vo, user_id)
        p = Popen(cmd.split(), stdout=PIPE, stdin=PIPE, stderr=STDOUT)    
        out = p.communicate(input=passwd)[0]
        if p.returncode != 0:
            print out
            return None
    return User(user_id) 

class User():
    def __init__(self, user_id):
        self.user_id = user_id
        self.proxy = '/tmp/%s' % self.user_id
        self.csv_file = '/tmp/%s.csv' % self.user_id
        open(self.csv_file, 'a+') 

    def reset_data(self):
        from shutil import copyfile
        copyfile(self.csv_file, '.'.join([self.csv_file, 'bak', str(time.time())]))
        open(self.csv_file, 'w') 

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user_id

    def valid_proxy(self):
        try:
            # Check that we have valid proxy
            out = check_output(['voms-proxy-info', '-e', '-file', '%s' % self.proxy])
            return True
        except CalledProcessError as e:
            return False

