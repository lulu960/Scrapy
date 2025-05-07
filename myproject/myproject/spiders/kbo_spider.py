import scrapy
import csv
import os


class KboSpider(scrapy.Spider):
    name = "kbo_spider"
    allowed_domains = ["kbopub.economie.fgov.be"]

    def start_requests(self):
        csv_path = os.path.join(os.path.dirname(__file__), "enterprise.csv")
        if not os.path.exists(csv_path):
            self.logger.error(f"CSV file not found: {csv_path}")
            return
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                num = row.get("EnterpriseNumber") or list(row.values())[0]  # support sans en-tête
                if num:
                    url = f"https://kbopub.economie.fgov.be/kbopub/toonondernemingps.html?ondernemingsnummer={num}"
                    yield scrapy.Request(
                        url=url,
                        headers={"Accept-Language": "fr"},
                        callback=self.parse,
                        meta={"numero_entreprise": num}
                    )

    def parse(self, response):
        numero_entreprise = response.meta["numero_entreprise"]
        data = {
            "numero_entreprise": numero_entreprise,
            "generalites": {},
            "fonctions": [],
            "capacites_entrepreneuriales": None,
            "qualites": [],
            "autorisations": [],
            "nace_codes": {
                "2025": [],
                "2008": [],
                "2003": []
            },
            "donnees_financieres": {},
            "liens_entites": [],
            "liens_externes": []
        }

        current_section = None
        rows = response.xpath('//table[1]//tr')

        for row in rows:
            h2 = row.xpath(".//h2/text()").get()
            if h2:
                h2_clean = h2.strip().lower()
                if "généralités" in h2_clean:
                    current_section = "generalites"
                elif "fonctions" in h2_clean:
                    current_section = "fonctions"
                elif "capacités entrepreneuriales" in h2_clean:
                    current_section = "capacites_entrepreneuriales"
                elif "qualités" in h2_clean:
                    current_section = "qualites"
                elif "autorisations" in h2_clean:
                    current_section = "autorisations"
                elif "version 2025" in h2_clean:
                    current_section = "nace_2025"
                elif "version 2008" in h2_clean:
                    current_section = "nace_2008"
                elif "version 2003" in h2_clean:
                    current_section = "nace_2003"
                elif "données financières" in h2_clean:
                    current_section = "donnees_financieres"
                elif "liens entre entités" in h2_clean:
                    current_section = "liens_entites"
                elif "liens externes" in h2_clean:
                    current_section = "liens_externes"
                continue

            cells = row.xpath(".//td")
            if len(cells) >= 2:
                label = " ".join(cells[0].xpath(".//text()").getall()).strip().replace("\xa0", " ")
                value = " ".join(cells[1].xpath(".//text()").getall()).strip().replace("\xa0", " ")

                if current_section == "generalites":
                    data["generalites"][label.rstrip(":")] = value
                elif current_section == "donnees_financieres":
                    data["donnees_financieres"][label.rstrip(":")] = value
                elif current_section == "capacites_entrepreneuriales":
                    data["capacites_entrepreneuriales"] = label + " - " + value
                elif current_section == "qualites":
                    if label:
                        data["qualites"].append(label)
                elif current_section == "autorisations":
                    url = cells[0].xpath(".//a/@href").get()
                    if url:
                        data["autorisations"].append(response.urljoin(url))
                elif current_section == "liens_entites":
                    link = cells[0].xpath(".//a")
                    if link:
                        num = link.xpath("text()").get()
                        name = link.xpath("following-sibling::text()").get()
                        data["liens_entites"].append({
                            "numero": num.strip(),
                            "nom": name.strip() if name else ""
                        })
                elif current_section == "liens_externes":
                    for a in cells[0].xpath(".//a"):
                        url = a.xpath("./@href").get()
                        title = a.xpath("text()").get()
                        if url:
                            data["liens_externes"].append({
                                "titre": title.strip(),
                                "url": response.urljoin(url)
                            })
                elif current_section and current_section.startswith("nace_"):
                    if label:
                        data["nace_codes"][current_section.split("_")[1]].append(label)

        for fct_row in response.xpath("//table[@id='toonfctie']//tr"):
            cells = fct_row.xpath(".//td")
            if len(cells) >= 3:
                fonction = cells[0].xpath("string()").get().strip()
                nom = cells[1].xpath("string()").get().strip()
                date = cells[2].xpath("string()").get().strip()
                data["fonctions"].append({
                    "fonction": fonction,
                    "nom": nom,
                    "date_debut": date
                })
        self.logger.info(f"Généralités pour {numero_entreprise}: {data['generalites']}")
        yield data
