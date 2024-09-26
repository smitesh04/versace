import scrapy
from scrapy.cmdline import execute
from versace.db_config import DbConfig
from fake_useragent import UserAgent
ua = UserAgent()
obj = DbConfig()


class LinkSpider(scrapy.Spider):
    name = "link"
    # allowed_domains = ["."]
    def start_requests(self):

        url = "https://www.versace.com/us/en/find-a-store/?country=US&countryCode=us"    # def start_requests(self):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'user-agent': ua.random,
        }
        yield scrapy.Request(url, headers=headers, callback=self.parse)


    def parse(self, response):
        store_div = response.xpath('//div[contains(@class,"js-storecard") and not(contains(@class, "d-none"))]')

        for store in store_div:
            us_check = store_div.xpath(".//input[@value='US']")
            if us_check:
                store_name = store.xpath('.//h2[@class="storecard__name"]/a/@data-store-name').get()
                store_url = store.xpath('.//h2[@class="storecard__name"]/a/@href').get()
                store_id = store.xpath('.//h2[@class="storecard__name"]/a/@data-store-id').get()
                store_hours_all = store.xpath('.//p[@class="storecard__hours"]//span/text()').getall()
                store_timings = list()
                for i in store_hours_all:
                    if 'None' not in i:
                        day = i.split(' ')[0]
                        timings = i.split(' ')[1]
                        store_timings.append(f'{day}: {timings}')
                store_timings_final = ' | '.join(store_timings)
                phone = store_div.xpath(".//a[@aria-label='Contact Us']/@href").get()
                phone = phone.replace('tel:', '')
                directions_url = store_div.xpath(".//a[@aria-label='Directions']/@href").get()
                # store_details_url = store_div.xpath(".//a[@aria-label='Boutique Details']/@href").get()
                obj.insert_store_links_table(store_url, directions_url)
                print(store_url)


if __name__ == '__main__':
  execute("scrapy crawl link".split())