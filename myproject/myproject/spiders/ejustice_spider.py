import scrapy


class EjusticeSpider(scrapy.Spider):
    name = "ejustice_spider"
    allowed_domains = ["ejustice.just.fgov.be"]
    start_urls = [
        "https://www.ejustice.just.fgov.be/cgi_tsv/list.pl?language=fr&btw=201310731"
    ]

    def parse(self, response):
        publications = response.css("div.list-item")

        for pub in publications:
            title_full = pub.css("p.list-item--subtitle font::text").get()
            address_block = pub.css("a.list-item--title").xpath("text()[1]").get().strip()
            reference_number = pub.css("a.list-item--title").xpath("text()[2]").get().strip()
            type_pub = pub.css("a.list-item--title").xpath("text()[3]").get().strip()
            date_numero = pub.css("a.list-item--title").xpath("text()[4]").get().strip()
            image_link = pub.css("a.standard::attr(href)").get()

            # Séparer la date et le numéro (ex: "2024-04-05 / 0056619")
            if '/' in date_numero:
                date_pub, numero_pub = [s.strip() for s in date_numero.split("/")]
            else:
                date_pub = ""
                numero_pub = date_numero.strip()

            yield {
                "titre_publication": title_full.strip() if title_full else "",
                "adresse_publication": address_block,
                "reference_publication": reference_number,
                "type_publication": type_pub,
                "date_publication": date_pub,
                "numero_publication": numero_pub,
                "url_image": response.urljoin(image_link) if image_link else None,
            }
