import requests
import time


def report(code):
    print('How did we do {}?',code)
    print('taking 5')

def fetch(url):
    return requests.get(url)

def report_errors(url):
    response = fetch(url)
    if response.status_code == 404:
        print(f"404: {url}")
    return response.status_code

def main():
    urls = [
        'https://condepro.com',
        'http://condepro.com/should-nimot-exist',
    ]
    for url in urls:
        code = report_errors(url)
        time.sleep(4.5)
        # report(code)

if __name__ == "__main__":
    main()
