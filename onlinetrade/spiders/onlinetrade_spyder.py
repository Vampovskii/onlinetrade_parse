import numpy as np
import scrapy
import re

class OnlinetradeSpyderSpider(scrapy.Spider):
    custom_settings = {'FEED_URI' : 'results/onlinetrade.csv'}

    name = 'onlinetrade'

    """ Составляем корректный список страниц. """
    allowed_domains = ['www.onlinetrade.ru']
    first_page = ['https://www.onlinetrade.ru/catalogue/noutbuki-c9/'] 
    all_others = ['https://www.onlinetrade.ru/catalogue/noutbuki-c9/?page='+str(x) for x in range(1,1859)]

    """ Вставлем на 1 меcто (0 индекс) нашу первую страницу. """
    start_urls = first_page+all_others
    
    def refine(self, string, field):
        compiled = re.compile('<.*?>')
        clean = re.sub(compiled, '|', string)
        clean = clean.replace('Новая цена:','').replace('Старая цена:', '').replace('₽', '').replace('Цена:','').replace(' ', '') # очищаем от артефактов
        amount = abs(int(clean.split('|')[field]))
        return amount

    def parse(self, response):
        imgs = response.xpath("//div[@class='indexGoods__item__flexCover']//img/@src").extract()
        titles = response.xpath("//div[@class='indexGoods__item__descriptionCover']//a[@class='indexGoods__item__name  indexGoods__item__name__3lines  ']//text()").extract()
        prices = response.xpath("//div[@class='indexGoods__item__price']").extract()
        clean_old_prices = [self.refine(price, 5) if '<span class="gray">' in price else np.nan for price in prices]
        clean_new_prices = [self.refine(price, 10) if '<span class="price js__actualPrice" itemprop="price" title="Новая цена">' in price else 0 for price in prices]
        clean_reg_prices = [self.refine(price, 4) if '<span class="price regular js__actualPrice" itemprop="price" title="Обычная цена">' in price else np.nan for price in prices]

        for item in zip(titles, clean_reg_prices, clean_new_prices, clean_old_prices, imgs):
                scraped_info = {
                    'title' : item[0],
                    'reg_price' : item[1],
                    'new_price' : item[2],
                    'old_price' : item[3],
                    'image_urls' : [item[4]]}
                yield scraped_info