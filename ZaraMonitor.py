import requests
from bs4 import BeautifulSoup

class ZaraMonitor():
    #Appear as browser
    headers = {"User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}

    def __init__(self, url):
        self.is_found = False
        self.monitor_url = url
        self.soup = BeautifulSoup(requests.get(self.monitor_url, headers=self.headers).text, 'html.parser')
        try:
            self.get_title()
        except:
            raise Exception    

    def get_title(self):
        return self.soup.title.string

    def check(self):
        print('Checking {}'.format(self.get_title()))
        try:
            not_found = self.soup.find_all('span', {'class': 'button__second-line'})[0].string
        except:
            self.is_found = True
            return True




