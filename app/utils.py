import requests
import random
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
from .settings import ROOT_DIR

CACHE_DIR = ROOT_DIR / "cache"

COUNTRIES_API = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"

EXCHANGE_RATE_API = "https://open.er-api.com/v6/latest/USD"


def getCountries_ExR():
    try:
        countries_json = requests.get(COUNTRIES_API).json()
    except:
        return {
            "error": "External data source unavailable",
            "details": f"Could not fetch data from {COUNTRIES_API}",
        }
    try:
        exr_json = requests.get(EXCHANGE_RATE_API).json().get("rates")
    except:
        return {
            "error": "External data source unavailable",
            "details": f"Could not fetch data from {COUNTRIES_API}",
        }

    if not countries_json or not exr_json:
        return None

    seen = []
    countries = []
    country = {}

    for country_json in countries_json:
        country["name"] = country_json.get("name")        
        country["capital"] = country_json.get("capital")
        country["region"] = country_json.get("region")
        country["population"] = country_json.get("population")

        currencies = country_json.get("currencies")

        if currencies:
            country["currency_code"] = currencies[0].get("code")
            if country["currency_code"] in exr_json.keys():
                country["exchange_rate"] = round(exr_json[country["currency_code"]], 2)
                country["estimated_gdp"] = round((country["population"] * random.randint(1000, 2000)) / country["exchange_rate"], 1)
            else:
                country["exchange_rate"] = None
                country["estimated_gdp"] = None
        else:
            country["currency_code"] = None
            country["exchange_rate"] = None
            country["estimated_gdp"] = 0

        country["flag_url"] = country_json.get("flag")

        # clean dictionary of duplicate enteries
        if country["name"] not in seen:
            seen.append(country["name"])
            countries.append(country)

        country = {}

    print(countries)
    return countries


def generate_image(countries: list):
    os.makedirs("cache", exist_ok=True)
    print("IN IMAGE GENERATOR")
    '''
    generates a summary image
    containing:
    -Total number of countries
    -Top 5 countries by estimated GDP
    -Timestamp of last refresh
    
    **saves to "cache/summary.png"
    '''
    # countries is a list object containing countries successfully inserted into the dadatabase

    try:
        total_no_countries = len(countries)

        countries 
        countries = sorted((c for c in countries if c["estimated_gdp"] is not None), key=lambda x: x["estimated_gdp"], reverse=True)[:5]
        print("COUNTRIES")
        print(countries)
        last_updated = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        ##Create image
        filename = "cache/summary.png"

        img = Image.new("RGB", (600, 200), color=(255, 255, 255))

        if not img:
            return
        # Drawing context
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()

        lines = [
            f"Total number of countries: {total_no_countries}",
            "Top 5 countries by estimated GDP: "
            + ',\n'.join([f'{country.get("name")}: {country.get("estimated_gdp")}' for country in countries]),
            f"Timestamp of last refresh: {last_updated}",
        ]
        y = 10
        for text in lines:
            draw.text((10, y), text, fill=(0, 0, 0), font=font)
            y += 20
            if y == 50:
                y += 60

        img.save(filename)
        return filename
    except Exception as e:
        print(e)


def serializeCountry(country_obj):
    country = {
        "id": country_obj.id,
        "name": country_obj.name,
        "capital": country_obj.capital,
        "region": country_obj.region,
        "population": country_obj.population,
        "currency_code": country_obj.currency_code,
        "exchange_rate": country_obj.exchange_rate,
        "estimated_gdp": country_obj.estimated_gdp,
        "flag_url": country_obj.flag_url,
        "last_refreshed_at": country_obj.last_refreshed_at.replace(
            tzinfo=timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    return country
