import meraki
import credentials
import re
import time
import cvpn_mail
import datetime

from flask import Flask

api_key = credentials.api_key
baseurl = credentials.base_url
org_id = credentials.organization_id
network_id = credentials.network_id
client_vpn_threshold = credentials.client_vpn_threshold

# initialization
app = Flask(__name__)  # create the Flask app

# Instantiate Meraki Python SDK Client
dashboard = meraki.DashboardAPI(
        api_key=api_key,
        base_url=baseurl,
        print_console=False)


@app.route('/', methods=['GET'])
def main():
        # i = 0
        while True:
                clientvpn = dashboard.clients.getNetworkClients(networkId=network_id)
                cvpn_users = 0
                for item in clientvpn:
                        #Check if Client Device belongs to ClientVPN Subnet
                        l = re.split('(.*)\.(.*)\.(.*)\.(.*)', item['ip'])
                        network_add = l[1:-1]
                        if network_add[0:3] == ['192','168','92'] or network_add[0:3] == ['192','168','93']:
                                curr_stamp = datetime.datetime.utcnow().timestamp()
                                dt = datetime.datetime.strptime(item['lastSeen'], '%Y-%m-%dT%H:%M:%SZ')
                                client_stamp=dt.timestamp()
                                # If Client VPN user has been seen in the last 10 minutes, count it
                                if (curr_stamp - 600) <= client_stamp:
                                        cvpn_users = cvpn_users + 1
                print(cvpn_users)
                # Set client threshold to desired amount in credentials file
                if cvpn_users >= client_vpn_threshold:
                        sender_email = credentials.email
                        password = credentials.password
                        subject = "WARNING TOO MANY VPN USERS!"
                        body = "ALERT, TOTAL CLIENT VPN USERS IS {} ".format(cvpn_users)
                        body = body + "\nREMEMBER TO START THE SCRIPT AGAIN!"
                        cvpn_mail.send_mail(sender_email, password, subject, body)
                        # i = 1
                else:
                        now = datetime.datetime.today()
                        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

                        sender_email = credentials.email
                        password = credentials.password
                        subject = "WARNING TOO MANY VPN USERS!"
                        body = "ALERT, TOTAL CLIENT VPN USERS IS {} ".format(cvpn_users)
                        body = body + "\nREMEMBER TO START THE SCRIPT AGAIN!" + dt_string
                        cvpn_mail.send_mail(sender_email, password, subject, body)
                time.sleep(30)


if __name__ == 'main':
        app.run(port=5000, debug=False)
