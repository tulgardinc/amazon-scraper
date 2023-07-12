from pathlib import Path
from ..items import Product

import scrapy
import re


class SpinnerSpider(scrapy.Spider):
    name = "spinner"

    def start_requests(self):
        URL = "https://www.amazon.com/s?k=fidget+spinner"
        yield scrapy.Request(url=URL, callback=self.parse)

    def parse(self, response):
        cards = response.css(".s-card-border")

        for card in cards:
            price_whole = card.css(".a-price-whole::text").get()
            price_frac = card.css(".a-price-fraction::text").get()
            reviews_result = card.css(".aok-align-bottom .a-icon-alt::text").get()
            reviews = (
                float(re.findall(r"\d+.\d+", reviews_result)[0])
                if reviews_result is not None
                else -1.0
            )
            review_amount_result = card.css(
                ".s-link-style .s-underline-text::text"
            ).get()
            review_amount = (
                int(review_amount_result.replace(",", ""))
                if review_amount_result is not None
                else -1
            )
            original_price_result = card.css(".a-text-price span::text").get()
            original_price = (
                float(original_price_result[1:])
                if original_price_result is not None
                else -1.0
            )

            yield Product(
                name=card.css(".a-color-base.a-text-normal::text").get(),
                price=f"{price_whole}.{price_frac}",
                original_price=original_price,
                reviews=reviews,
                review_amount=review_amount,
            )

        next_url = response.css(".s-pagination-next::attr(href)").get()
        if next_url is not None:
            yield response.follow(
                "https://www.amazon.com/" + next_url, callback=self.parse
            )
