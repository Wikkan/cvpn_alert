import meraki
import credentials
import re
import time
import cvpn_mail

from flask import Flask

import traceback
from werkzeug.wsgi import ClosingIterator


class AfterResponse:
    def __init__(self, app=None):
        self.callbacks = []
        if app:
            self.init_app(app)

    def __call__(self, callback):
        self.callbacks.append(callback)
        return callback

    def init_app(self, app):
        # install extension
        app.after_response = self

        # install middleware
        app.wsgi_app = AfterResponseMiddleware(app.wsgi_app, self)

    def flush(self):
        for fn in self.callbacks:
            try:
                fn()
            except Exception:
                traceback.print_exc()


class AfterResponseMiddleware:
    def __init__(self, application, after_response_ext):
        self.application = application
        self.after_response_ext = after_response_ext

    def __call__(self, environ, after_response):
        iterator = self.application(environ, after_response)
        try:
            return ClosingIterator(iterator, [self.after_response_ext.flush])
        except Exception:
            traceback.print_exc()
            return iterator


api_key = credentials.api_key
baseurl = credentials.base_url
org_id = credentials.organization_id
network_id = credentials.network_id
client_vpn_threshold = credentials.client_vpn_threshold

# initialization
app = Flask("after_response")  # create the Flask app
AfterResponse(app)

# Instantiate Meraki Python SDK Client
dashboard = meraki.DashboardAPI(
    api_key=api_key,
    base_url=baseurl,
    print_console=False)


def get_count_network_clients_online():
    condition = False
    list_clients = []
    list_clients_online = []
    user_id = ''

    while not condition:
        try:
            clients = dashboard.clients.getNetworkClients(networkId=network_id, total_pages=1, direction='next',
                                                          perPage=1000, startingAfter=user_id)
        except Exception:
            return False

        if len(clients) != 1000:
            condition = True

        for c in clients:
            list_clients.append(c)

        user_id = list_clients[-1]['id']

    for client in list_clients:
        if client['ip'] is not None:
            # Check if Client Device belongs to ClientVPN Subnet
            l = re.split('(.*)\.(.*)\.(.*)\.(.*)', client['ip'])
            network_add = l[1:-1]
            if network_add[0:3] == ['192', '168', '92'] or network_add[0:3] == ['192', '168', '93']:
                if client['status'] == 'Online':
                    list_clients_online.append(client)

    return len(list_clients_online)


@app.after_response
def main():
    while True:
        result = get_count_network_clients_online()

        if not result:
            print("There was a problem getting the cvpn users")
            time.sleep(300)
        else:
            cvpn_users = result
            print(cvpn_users)

            # Set client threshold to desired amount in credentials file
            if cvpn_users >= client_vpn_threshold:
                sender_email = credentials.email
                password = credentials.password
                subject = "WARNING TOO MANY VPN USERS!"
                body = "ALERT, TOTAL CLIENT VPN USERS IS {} ".format(cvpn_users)
                result = cvpn_mail.send_mail(sender_email, password, subject, body)

                if not result:
                    print("There was a problem sending the email")
                    time.sleep(300)
                else:
                    print('Waiting...')
                    time.sleep(1500)

            time.sleep(300)


@app.route('/')
def main():
    return "Success!\n"


if __name__ == '__main__':
    app.run(port=5000, debug=False)
