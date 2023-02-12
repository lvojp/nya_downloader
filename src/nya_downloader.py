import os
import sys
import argparse
import urllib.request
import urllib.error
import re
import pathlib
import requests
from bs4 import BeautifulSoup


class NyaDownloader:
    def get_html(self, url: str) -> str:
        res = requests.get(url)
        result = res.text
        return result

    def get_last_page_number(self) -> int:
        result = 0
        return result

    def get_valid_url(self) -> str:
        result = ''
        return result

    def get_image(self, url, dst_path):
        def create_request(url):
            req = urllib.request.Request(url)
            # req.add_header('Referer', 'http://www.python.org/')
            req.add_header('User-Agent', 'Mozilla/5.0')
            return req

        try:
            req = create_request(url)
            with urllib.request.urlopen(req) as web_file:
                data = web_file.read()
                with open(dst_path, mode='wb') as local_file:
                    local_file.write(data)
        except urllib.error.URLError as e:
            print(e)

    def check_dupe(self, target_dir) -> str:
        if os.path.exists(target_dir):
            num = str(target_dir.split('_')[-1])
            if num.isdigit():
                num = int(num) + 1
                base_name = target_dir.split('_')[0]
                new_target_dir = f'{base_name}_{num}'
                return self.check_dupe(new_target_dir)
            else:
                new_target_dir = f'{target_dir}_2'
                return self.check_dupe(new_target_dir)
        else:
            return target_dir

    def download(self, target_url: str, title: str, last_page_number: int, output: str) -> None:
        target_dir = f'{output}/{title}'.replace('//', '/')
        target_dir = self.check_dupe(target_dir)
        os.makedirs(target_dir, exist_ok=True)
        print(f'Make a directory {target_dir}')
        for i in range(1, last_page_number + 1):
            self.get_image(f'{target_url}/{i}.webp', f'{target_dir}/{i}.webp')
            print(f'Image saved {i}/{last_page_number}')

    def main(self, url: str, output: str) -> None:
        html = self.get_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.text.split()[0]
        last_page_url = soup.find_all(alt=re.compile(title))[-1]['src']
        last_page_number = int(last_page_url.split('/')[-1].split('.')[0])
        img_url = str(pathlib.Path(last_page_url).parent).replace('https:/', 'https://')
        self.download(img_url, title, last_page_number, output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download target')
    parser.add_argument('-o', '--output', required=True, help='Output directory')
    parser.add_argument('-u', '--url', required=False, help='Enter a valid URL')
    parser.add_argument('-f', '--file', required=False, help='Line-wrapped list file')

    args = parser.parse_args()
    url = args.url
    file = args.file
    output = args.output

    nd = NyaDownloader()

    if url is None and file is None:
        print('URL(-u) or file(-f) input is required.')
        sys.exit()
    if file is None:
        nd.main(url, output)
    else:
        with open(file, mode='r') as f:
            urls = f.read().split()
            for url in urls:
                nd.main(url, output)
