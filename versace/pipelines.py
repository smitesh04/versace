# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from versace.items import DataItem
from versace.db_config import DbConfig
obj = DbConfig()

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class VersacePipeline:
    def process_item(self, item, spider):
        if isinstance(item, DataItem):
            obj.insert_data_table(item)
            obj.update_store_links_status(store_url=item['url'])

        return item
