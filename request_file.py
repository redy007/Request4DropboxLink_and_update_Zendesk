import sys, requests, json
if len(sys.argv) == 1:
        sys.exit("Please specify Zendesk ticket to proceed. Eg. create_file_request.py 12345")
ticket=sys.argv[1]
zd_login=''
zd_password=''
company=''
dropbox_token='vkcVsBosu8AAAAAAAAAE5OpQGwLCyYiPICR9xzBGYOlz6AmnjLoR74vasQ9uVgFQ'

#Check if ticket exists
print("Checking, if Zendesk ticket exists...")
ticket_url='https://'+ company +'.zendesk.com/api/v2/tickets/{ticket}.json'.format(ticket=str(ticket))
headers = {
    'content-type': 'application/json',
}
params = (
    ('priority', 'normal'),
)
r=requests.get(ticket_url, headers=headers, params=params, auth=(zd_login, zd_password))
if r.status_code!=200:
        print(r.text)
        sys.exit("There was an error obtaining ticket info. Please double check, that the ticket exists.")

#Check if file request exists
print("ZD ticket exists.\nChecking, if File Request already exists...")
headers = {
        'Authorization': 'Bearer '+dropbox_token
}
list_url='https://api.dropboxapi.com/2/file_requests/list'
r=requests.post(list_url, headers=headers)
if r.status_code!=200:
        print(r.text)
        sys.exit("There was an error obtaining Request Files list. ")
file_requests = json.loads(r.text)
for request in file_requests["file_requests"]:
        if request["title"]==ticket:
                dest='https://www.dropbox.com/home'+request["destination"]
                sys.exit("File Request already exists: {url}, {dest}".format(url=request["url"], dest=dest))

#Create request files folder:
print("File request does not exist. Creating...")
headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+dropbox_token
}
data=json.dumps({
'title': str(ticket),
'destination': '/Technical/04-testing/02-Zendesk/{ticket}'.format(ticket=ticket),
'open': True
})
r = requests.post("https://api.dropboxapi.com/2/file_requests/create", headers=headers, data=data)
if r.status_code!=200:
        print(r.text)
        sys.exit("There was an error during File Request creation.")
print("File Request created successfully...")
request=json.loads(r.text)
dest='https://www.dropbox.com/home'+request["destination"]
print(request["title"], request["url"], dest)


#update ticket
print("Updating ticket {ticket}".format(ticket=ticket))
headers = {
        'Content-Type': 'application/json',
}
data=json.dumps({"ticket":{"custom_fields":[{"id": 33168047, "value": request["url"]+'\n'+dest}]}})
#print(data)
r = requests.put(ticket_url, headers=headers, data=data, auth=(zd_login, zd_password))
if r.status_code!=200:
        print(r.text)
        sys.exit("There was an error updating ticket. ")
print("Ticket updated successfully...")
