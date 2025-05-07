import scrapy
import json
from urllib.parse import urlencode


class NbbSpider(scrapy.Spider):
    name = 'nbb_spider'
    allowed_domains = ['consult.cbso.nbb.be']
    company_numbers = ['0200068636']  # Ajouter plus si besoin

    def start_requests(self):
        for number in self.company_numbers:
            yield from self.fetch_page(number, page=0)

    def fetch_page(self, number, page):
        base_url = 'https://consult.cbso.nbb.be/api/rs-consult/published-deposits'
        params = {
            'page': page,
            'size': 100,
            'enterpriseNumber': number,
            'sort': ['periodEndDate,desc', 'depositDate,desc']
        }
        url = f'{base_url}?{urlencode(params, doseq=True)}'
        return [scrapy.Request(url, callback=self.parse, meta={'company_number': number, 'page': page})]

    def parse(self, response):
        data = json.loads(response.text)
        number = response.meta['company_number']
        page = response.meta['page']

        for item in data.get("content", []):
            doc_id = item.get("id")
            file_ext = item.get("importFileType", "PDF").lower()
            file_url = f"https://consult.cbso.nbb.be/api/rs-consult/deposits/{doc_id}/files/{file_ext}" if doc_id else None

            yield {
                "company_number": number,
                "titre_publication": item.get("modelName"),
                "reference_publication": item.get("reference"),
                "date_depot": item.get("depositDate"),
                "date_fin_exercice": item.get("periodEndDate"),
                "langue": item.get("language"),
                "fichier": file_url
            }

        # Pagination
        if not data.get("last", True):
            yield from self.fetch_page(number, page + 1)
