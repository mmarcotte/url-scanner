import requests

res = requests.get('http://job-01.ampcms.internal:3000/api/sites')
data = res.json()
domains = set()
for site in data["sites"]:
    for domain in site["domains"]:
        domains.add(domain)

f = open('domains.txt', 'w')
for domain in domains:
    f.write(domain)
    f.write("\n")

f.close()


