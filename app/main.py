from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated, Optional
from fastapi.responses import JSONResponse, FileResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, asc, desc
from app.utils import getCountries_ExR, generate_image, serializeCountry
from .settings import *
from app.models import Country
from app.database import *

# STATIC_DIR = Path(__file__).parent / "static"

CACHE_DIR = ROOT_DIR / "cache"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

##VALIDATOR

class CountryValidator(BaseModel):
    name: str
    capital: Optional[str]
    region: Optional[str]
    population: str
    currency_code: Optional[str]
    exchange_rate: Optional[float]
    estimated_gdp: Optional[float]
    flag_url: Optional[str]


@app.post("/countries/refresh", status_code=status.HTTP_201_CREATED)
def RefreshCountries(db: db_dependency):
    countries = getCountries_ExR()

    if isinstance(countries, dict):
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=countries)

    try:
        for country in countries:
            # print(type(Country.name))
            db_country = db.query(Country).filter(func.lower(Country.name) == country.get("name").lower()).first()
            if db_country:
                # country exists in database.. update enteries
                db_country.name = country.get("name")
                db_country.capital = country.get("capital")
                db_country.region = country.get("region")
                db_country.population = country.get("population")
                db_country.currency_code = country.get("currency_code")
                db_country.exchange_rate = country.get("exchange_rate")
                db_country.estimated_gdp = country.get("estimated_gdp")
                db_country.flag_url = country.get("flag_url")
                db.commit()
                db.refresh(db_country)
            else:
                db_country = Country(**country)
                db.add(db_country)
                db.commit()
                db.refresh(db_country)
        generate_image(countries)
    except:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error"}
        )

@app.get("/countries/image", status_code=status.HTTP_200_OK)
def GetSummaryImage():
    filename = CACHE_DIR / "summary.png"

    if not os.path.exists(filename):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Summary image not found"},
        )
    return FileResponse(filename, media_type="image/png")

@app.get("/countries/{name}", status_code=status.HTTP_200_OK)
def getCountry(name: str, db: db_dependency):
    if not isinstance(name, str):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Validation failed"},
        )

    db_country = (
        db.query(Country).filter(func.lower(Country.name) == name.lower()).first()
    )
    
    if not db_country:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Country not found"},
        )

    return serializeCountry(db_country)

@app.delete("/countries/{name}", status_code=status.HTTP_204_NO_CONTENT)
def deleteCountry(name: str, db: db_dependency):
    if not isinstance(name, str):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Validation failed"},
        )

    db_country = (
        db.query(Country).filter(func.lower(Country.name) == name.lower()).first()
    )

    if not db_country:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Country not found"},
        )
    db.delete(db_country)
    db.commit()

@app.get("/status", status_code=status.HTTP_200_OK)
def getDbStatus(db: db_dependency):
    first = db.query(Country).first()
    if not first:
        last_refreshed_at = None
    else:
        last_refreshed_at = serializeCountry(first).get("last_refreshed_at")
    total_countries = db.query(Country).count()
    return {"last_refreshed_at": last_refreshed_at, "total_countries": total_countries}

@app.get("/countries", status_code=status.HTTP_200_OK)
def getCountries(db: db_dependency, request: Request):
    query_params = dict(request.query_params)
    print(query_params)

    sort = query_params.pop("sort", None)
    valid_filters = ["id", "name", "capital", "region", "population", "currency_code", "exchange_rate", "estimated_gdp", "flag_url", "last_refreshed_at"]

    filters = []
    for key, value in query_params.items():
        if key in valid_filters:
            if value is not None:
                if key == "id":
                    filters.append(Country.id == value)
                if key == "name":
                    filters.append(Country.name == value)
                if key == "capital":
                    filters.append(Country.capital == value)
                if key == "region":
                    filters.append(Country.region == value)
                if key == "population":
                    filters.append(Country.population == value)
                if key == "currency_code":
                    filters.append(Country.currency_code == value)
                if key == "exchange_rate":
                    filters.append(Country.exchange_rate == value)
                if key == "estimated_gdp":
                    filters.append(Country.estimated_gdp == value)
                if key == "flag_url":
                    filters.append(Country.flag_url == value)
                if key == "last_refreshed_at":
                    filters.append(Country.last_refreshed_at == value)
    db_countries = db.query(Country)
    if filters:
        db_countries = db_countries.filter(and_(*filters))
    if sort:
        if sort == "gdp_desc":
            # sort by gdp descending
            db_countries = db_countries.order_by(desc(Country.estimated_gdp))
        if sort == "gdp_asc":
            # sort by gdp ascending
            db_countries = db_countries.order_by(asc(Country.estimated_gdp))
        if sort == "pop_desc":
            # sort by gdp descending
            db_countries = db_countries.order_by(desc(Country.population))
        if sort == "pop_asc":
            # sort by gdp ascending
            db_countries = db_countries.order_by(asc(Country.population))
        if sort == "id_desc":
            # sort by gdp descending
            db_countries = db_countries.order_by(desc(Country.id))
        if sort == "id_asc":
            # sort by gdp ascending
            db_countries = db_countries.order_by(asc(Country.id))
    db_countries = db_countries.all()

    if db_countries:
        countries = []
        for db_country in db_countries:
            country = serializeCountry(db_country)
            countries.append(country)
        return countries
    return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Country not found"},
        )
