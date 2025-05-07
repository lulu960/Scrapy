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
                num = (row.get("EnterpriseNumber") or list(row.values())[0]).replace(".", "")
                if num:
                    url = f"https://kbopub.economie.fgov.be/kbopub/toonondernemingps.html?lang=fr&ondernemingsnummer={num}"
                    yield scrapy.Request(
                        url=url,
                        headers={"Accept-Language": "fr"},
                        callback=self.parse,
                        meta={"numero_entreprise": num}
                    )

    def parse(self, response):
        numero_entreprise = response.meta["numero_entreprise"]

        def extract_text(label):
            xpath = f'//td[contains(normalize-space(string(.)), "{label.split(":")[0]}")]/following-sibling::td[1]'
            return response.xpath(xpath).xpath(".//text()").getall()

        def join_text(text_list):
            return " ".join(t.strip().replace("\xa0", " ") for t in text_list if t.strip())

        data = {
            "EnterpriseNumber": numero_entreprise,
            "Status": join_text(extract_text("Statut:")),
            "JuridicalSituation": join_text(extract_text("Situation juridique:")),
            "StartDate": join_text(extract_text("Date de début:")),
            "TypeOfEnterprise": join_text(extract_text("Type d'entité:")),
            "JuridicalForm": join_text(extract_text("Forme légale:")),
            "Name": join_text(extract_text("Dénomination:")),
            "HeadOfficeAddress": join_text(extract_text("Adresse du siège:"))
        }

        # Fonctions (table masquée)
        data["Functions"] = []
        for fct_row in response.xpath("//table[@id='toonfctie']//tr"):
            cells = fct_row.xpath(".//td")
            if len(cells) >= 3:
                fonction = cells[0].xpath("string()" ).get().strip()
                nom = cells[1].xpath("string()").get().strip()
                date = cells[2].xpath("string()").get().strip()
                data["Functions"].append({
                    "Function": fonction,
                    "Name": nom,
                    "StartDate": date
                })

        # NACE codes
        for version in ["2025", "2008", "2003"]:
            xpath = f"//h2[contains(text(), '{version}')]/following-sibling::table[1]//tr"
            data[f"NACE_{version}"] = []
            for row in response.xpath(xpath):
                text = " ".join(row.xpath(".//text()").getall()).strip()
                if text:
                    data[f"NACE_{version}"].append(text)

        # Autorisations
        data["Authorizations"] = []
        for a in response.xpath("//h2[contains(text(),'Autorisations')]/following::a"):
            href = a.xpath("@href").get()
            title = a.xpath("text()").get()
            if href and title:
                data["Authorizations"].append({
                    "Title": title.strip(),
                    "URL": response.urljoin(href)
                })

        # Liens entre entités
        data["RelatedEntities"] = []
        for row in response.xpath("//h2[contains(text(),'Liens entre entités')]/following-sibling::table[1]//tr"):
            link = row.xpath(".//a")
            if link:
                num = link.xpath("text()").get()
                name = link.xpath("following-sibling::text()").get()
                if num:
                    data["RelatedEntities"].append({
                        "Number": num.strip(),
                        "Name": name.strip() if name else ""
                    })

        # Liens externes
        data["ExternalLinks"] = []
        for row in response.xpath("//h2[contains(text(),'Liens externes')]/following-sibling::table[1]//tr/td//a"):
            href = row.xpath("@href").get()
            title = row.xpath("text()").get()
            if href and title:
                data["ExternalLinks"].append({
                    "Title": title.strip(),
                    "URL": response.urljoin(href)
                })

        self.logger.info(f"Données extraites pour {numero_entreprise} : {data}")
        yield data
