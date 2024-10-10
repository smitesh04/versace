import datetime
import scrapy
from versace.db_config import DbConfig
from fake_useragent import UserAgent
from scrapy.cmdline import execute as ex
import json
from versace.items import DataItem
import os
import hashlib

ua = UserAgent()
obj = DbConfig()
today_date = datetime.datetime.today().strftime("%d_%m_%Y")
def create_md5_hash(input_string):
    md5_hash = hashlib.md5()
    md5_hash.update(input_string.encode('utf-8'))
    return md5_hash.hexdigest()
def page_write(pagesave_dir, file_name, data):
    if not os.path.exists(pagesave_dir):
        os.makedirs(pagesave_dir)
    file = open(file_name, "w", encoding='utf8')
    file.write(data)
    file.close()
    return "Page written successfully"

class DataSpider(scrapy.Spider):
    name = "data"
    def start_requests(self):
        obj.cur_versace.execute(f"select * from {obj.store_links_table} where status=0")
        rows = obj.cur_versace.fetchall()
        for row in rows:

            store_link = row['store_link']
            hashid = create_md5_hash(store_link)
            pagesave_dir = rf"C:/Users/Actowiz/Desktop/pagesave/versace/{today_date}"
            file_name = fr"{pagesave_dir}/{hashid}.html"
            row['file_name'] = file_name
            row['pagesave_dir'] = pagesave_dir

            if os.path.exists(file_name):

                yield scrapy.Request(
                    url='file:///' + file_name,
                    callback=self.parse,
                    cb_kwargs=row
                )
            else:
                headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'priority': 'u=0, i',
                'user-agent': ua.random,
                }
                yield scrapy.Request(url=store_link, headers=headers, callback=self.parse, cb_kwargs=row)

    def parse(self, response, **kwargs):
        file_name = kwargs['file_name']
        pagesave_dir = kwargs['pagesave_dir']
        if not(os.path.exists(file_name)):
            page_write(pagesave_dir, file_name, response.text)

        store_div = response.xpath('//div[contains(@class,"js-storecard") and not(contains(@class, "d-none"))]//div[@class="storecard__info"]')
        store_id = store_div.xpath(".//h1/@data-store-id").get()
        store_name = store_div.xpath(".//h1/@data-store-name").get()
        jsn_text = response.xpath("//script[@type='application/ld+json']/text()").get()
        jsn = json.loads(jsn_text)
        opening_hours = jsn['openingHours']
        store_timings = list()
        for i in opening_hours:
            if 'None' not in i:
                day = i.split(' ')[0]
                timings = i.split(' ')[1]
                store_timings.append(f'{day}: {timings}')
        store_timings_final = ' | '.join(store_timings)
        street_address = jsn['address']['streetAddress']
        postal_code = jsn['address']['postalCode']
        address_region = jsn['address']['addressRegion']
        address_locality = jsn['address']['addressLocality']
        lat = jsn['geo']['latitude']
        lng = jsn['geo']['longitude']
        phone = jsn['telephone']
        store_url = jsn['url']
        direction_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"

        item = DataItem()
        item['store_no'] = store_id
        item['name'] = store_name
        item['latitude'] = lat
        item['longitude'] = lng
        item['street'] = street_address
        item['city'] = address_locality
        item['state'] = address_region
        item['zip_code'] = postal_code
        item['county'] = address_locality
        item['phone'] = phone
        item['open_hours'] = store_timings_final
        item['url'] = kwargs['store_link']
        item['provider'] = "Versace"
        item['category'] = "Apparel And Accessory Stores"
        item['updated_date'] = datetime.datetime.today().strftime("%d-%m-%Y")
        item['country'] = "US"
        item['status'] = "Open"
        item['direction_url'] = direction_url
        item['pagesave_path'] = file_name
        yield item

if __name__ == '__main__':
    ex("scrapy crawl data".split())

