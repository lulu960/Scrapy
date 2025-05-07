import scrapy
import unicodedata
import re


class EjusticeSpider(scrapy.Spider):
    name = "ejustice_spider"
    allowed_domains = ["ejustice.just.fgov.be"]
    start_urls = [
        "https://www.ejustice.just.fgov.be/cgi_tsv/list.pl?language=fr&btw=201310731"
    ]

    def clean_text(self, text):
        if not text:
            return ""
        text = unicodedata.normalize("NFKC", text)  # Normalisation unicode
        text = re.sub(r"[\u2026\u200B\u00A0]+", " ", text)  # Remplacer points de suspension, espaces insécables, etc.
        text = re.sub(r"\s+", " ", text)  # Réduire les espaces multiples
        return text.strip()

    def parse(self, response):
        publications = response.css("div.list-item")

        for pub in publications:
            title_full = pub.css("p.list-item--subtitle font::text").get()
            address_block = pub.css("a.list-item--title").xpath("text()[1]").get()
            reference_number = pub.css("a.list-item--title").xpath("text()[2]").get()
            type_pub = pub.css("a.list-item--title").xpath("text()[3]").get()
            date_numero = pub.css("a.list-item--title").xpath("text()[4]").get()
            image_link = pub.css("a.standard::attr(href)").get()

            if not (address_block and reference_number and type_pub and date_numero):
                continue  # Évite de scraper une ligne incomplète

            # Séparer la date et le numéro
            if '/' in date_numero:
                date_pub, numero_pub = [s.strip() for s in date_numero.split("/")]
            else:
                date_pub = ""
                numero_pub = date_numero.strip()

            yield {
                "titre_publication": self.clean_text(title_full),
                "adresse_publication": self.clean_text(address_block),
                "reference_publication": self.clean_text(reference_number),
                "type_publication": self.clean_text(type_pub),
                "date_publication": self.clean_text(date_pub),
                "numero_publication": self.clean_text(numero_pub),
                "url_image": response.urljoin(image_link) if image_link else None,
            }
