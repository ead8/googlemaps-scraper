from playwright import sync_playwright
from dataclasses import dataclass, field, asdict
import pandas as pd
import argparse  # for command line arguments

@dataclass
class Business:
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None

@dataclass
class BusinessList:
    business_list: list[Business] = field(default_factory=list)

    def datafram(self):
        return pd.json_normalize([asdict(business) for business in self.business_list])
    
    def save_to_csv(self, filename):
        self.datafram().to_csv(f"{filename}.xlsx", index=False)
    
    def save_to_excel(self, filename):
        self.datafram().to_excel(f"{filename}.csv", index=False)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        #context = browser.newContext()
        page = browser.new_page()
        page.goto("https://www.google.com/maps",timeout=60000)
        page.wait_for_timeout(50000)
        page.locator('//input[@id="searchboxinput"]').fill(search_for)
        page.click("text=Log In")
        page.wait_for_timeout(3000)
        page.keyboard.press("Enter")
        page.wait_for_timeout(5000)

        listings=page.locator('//div[@role="article"]').all()
        print(len(listings))

        business_list=BusinessList()

        for listing in listings[:5]:
            
            listing.click()
            page.wait_for_timeout(5000)

            name_xpath='//h1[@contains(@class,"fontHeadlineLarge")]/span[2]'
            address_xpath='//button[@data-item-id="address"]//div[contains(@class,"fontBody")]/span[2]'
            website_xpath='//a[@data-item-id="authority"]//div[contains(@class,"fontBodyMedium")]/span[2]'
            phone_number_xpath='//button[contains(@data-item-id,"phone:tel:)"]//div[contains(@class,"fontBody")]/span[2]'

            business=Business()
            business.name=page.locator(name_xpath).inner_text()
            business.address=page.locator(address_xpath).inner_text()
            business.website=page.locator(website_xpath).inner_text()
            business.phone_number=page.locator(phone_number_xpath).inner_text()

            business_list.business_list.append(business)

        business_list.save_to_csv("google_maps_data")
        business_list.save_to_excel("google_maps_data")


        browser.close()

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Scrape Yelp")
    parser.add_argument("--location", default="New York", help="Location to search for", type=str)
    parser.add_argument("--term", default="Restaurants", help="Term to search for", type=str)
    args=parser.parse_args()

    if args.location and args.term:
        search_for=f'{args.term} {args.location}'
    else:
        search_for="Restaurants New York"
