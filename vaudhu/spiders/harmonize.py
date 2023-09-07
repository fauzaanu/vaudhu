import json
from pathlib import Path

import scrapy
import uuid

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class IbuAslamSpider(CrawlSpider):
    name = "ibu"
    allowed_domains = ["ibuaslam.com"]
    start_urls = ["https://www.ibuaslam.com/"]
    rules = (
        Rule(LinkExtractor(), follow=True, callback="parse_page"),
    )

    def parse_page(self, response):
        tracking_files_dir = Path(__file__).parent.parent / f'{self.name}_tracking_files'
        tracking_files_dir.mkdir(exist_ok=True)

        current_uuid = str()
        # create filemapper.json if it doesn't exist
        if not (tracking_files_dir / 'filemapper.json').exists():
            with open(tracking_files_dir / 'filemapper.json', 'w') as filemapper:
                json.dump({"yy": "xx"}, filemapper)

        with open(tracking_files_dir / 'filemapper.json', 'r') as filemapper:
            filemapper_json = json.load(filemapper)

            # does link exist?
            if str(response.url) in filemapper_json.keys():
                current_uuid = filemapper_json[str(response.url)]
                print(f"Found {current_uuid} for {response.url} in filemapper.json")
            else:
                current_uuid = str(uuid.uuid4())
                while current_uuid in filemapper_json.values():
                    current_uuid = str(uuid.uuid4())
                filemapper_json[str(response.url)] = str(current_uuid)

        with open(tracking_files_dir / 'filemapper.json', 'w') as filemapper:
            json.dump(filemapper_json, filemapper)

        filename = current_uuid + '.html'
        filepath = tracking_files_dir / filename
        with open(filepath, 'wb') as html_file:
            html_file.write(response.body)

    def closed(self, reason):
        # call subprocess and git commit after spider is closed
        import subprocess
        import os

        subprocess.run(["git", "add", "."], cwd=os.path.dirname(os.path.realpath(__file__)))
        subprocess.run(["git", "commit", "-m", f"Scraped {self.name}"], cwd=os.path.dirname(os.path.realpath(__file__)))
        subprocess.run(["git", "push"], cwd=os.path.dirname(os.path.realpath(__file__)))

        print(f"Spider closed: {reason}")
