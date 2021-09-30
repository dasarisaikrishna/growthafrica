# -*- coding: utf-8 -*-
from datetime import datetime, timezone

import scrapy
from crawlers.items import SIESData
from crawlers.spiders.basespider import BaseSpider
from sharedcode.extractors.schema import Core, Description, \
    ExtractedKnowledgeInner
from sharedcode.meta import Source
from sharedcode.urls import Domain


class GrowthAfricaSpider(BaseSpider):
    version = 3
    name = 'growthafrica_com'
    allowed_domains = ['growthafrica.com']
    start_urls = [f'https://growthafrica.com/investors/portfolio-our-ventures/']
    source = Source(
        name=name,
        verbose_name='growthafrica.com',
        domain=Domain.from_url('https://growthafrica.com/')
    )

    slug_pattern = r"(?:http://|https://)(?:|www.)(?:growthafrica\.com/)([-\w\%.]+)(?:|\/)"
    url_template = 'https://growthafrica.com/{slug}'


    def parse(self, response):
        url = "https://growthafrica.com/wp-admin/admin-ajax.php?action=getLoadMoreItems&id=7"
        headers = {
            'authority': 'growthafrica.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'referer': 'https://growthafrica.com/investors/portfolio-our-ventures/'
        }
        yield scrapy.Request(url=url, callback=self.parse_profiles, method='GET', headers=headers)

    def parse_profiles(self, response):
        for profile in response.xpath("//body/div"):
            website = profile.xpath(".//a/@href").get()
            if not website:
                continue
            if website and not website.startswith("http"):
                website = f'http://{website}'
            logo = profile.xpath(".//a/div/img/@src").get('').split('eco/')
            if logo and len(logo) == 2:
                logo = logo[1]
            description = profile.xpath("//a/div[2]/div/div/div/text()[1]").get('').strip()
            knowledge_obj = ExtractedKnowledgeInner(
                website=website,
                core=Core(
                    website=website,
                    name=self.slugify_url(website),
                    logo=logo,
                    description=Description(text_short=description)
                ),
            )
            profile = SIESData(
                data=knowledge_obj,
                request_url=f'https://growthafrica.com/{self.slugify_url(website)}',
                response_url=f'https://growthafrica.com/{self.slugify_url(website)}',
                datetime=datetime.now(timezone.utc)
            )
            yield profile