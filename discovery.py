import meraki
import credentials

api_key = credentials.api_key
baseurl = credentials.base_url
org_name = credentials.org_name
network_name = credentials.network_name

dashboard = meraki.DashboardAPI(
        api_key=api_key,
        base_url=baseurl,
        print_console=False)

orgs=dashboard.organizations.getOrganizations()
for item in orgs:
        if item['name']==org_name:
                org_id=item['id']
print('Your Organization ID is {}'.format(org_id))

networks=dashboard.networks.getOrganizationNetworks(org_id)
for item in networks:
        if item['name']==network_name:
                network_id=item['id']
print('Your Network ID is {}'.format(network_id))

print('Copy and paste these values into the respective fields in the credentials.py file and then run clientvpn.py')
