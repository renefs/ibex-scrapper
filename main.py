import requests
from bs4 import BeautifulSoup
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import WEBSITE_URL, DIV_ID, SQLALCHEMY_DATABASE_URI

Base = declarative_base()


class Company(Base):
    __tablename__ = 'company'

    required_attributes = (
        'ticker', 'latest', 'difference', 'difference_percentage', 'max_value', 'min_value', 'volume', 'capital', 'rpd',
        'per',
        'bpa', 'last_update',)

    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)

    latest = Column(String(255), nullable=False)
    ticker = Column(String(250), nullable=False)
    difference = Column(String(250), nullable=False)
    difference_percentage = Column(String(250), nullable=False)
    max_value = Column(String(250), nullable=False)
    min_value = Column(String(250), nullable=False)
    volume = Column(String(250), nullable=False)
    capital = Column(String(250), nullable=False)
    rpd = Column(String(250), nullable=False)
    per = Column(String(250), nullable=False)
    bpa = Column(String(250), nullable=False)
    last_update = Column(String(250), nullable=False)

    def __init__(self, ticker=None, latest=None, difference=None, difference_percentage=None, max_value=None,
                 min_value=None, volume=None, capital=None, rpd=None, per=None, bpa=None, last_update=None):

        self.ticker = ticker
        self.latest = latest
        self.difference = difference
        self.difference_percentage = difference_percentage
        self.max_value = max_value
        self.min_value = min_value
        self.volume = volume
        self.capital = capital
        self.rpd = rpd
        self.per = per
        self.bpa = bpa
        self.last_update = last_update

        for key in self.required_attributes:
            if self.__dict__[key] is None:
                raise ValueError("All the {} values must be fulfilled: {}".format(self.__class__.__name__, str(key)))

    def __repr__(self):
        return '<Company {} (Latest: {} {}) BPA: {} RPD: {}>'.format(self.ticker,
                                                                     self.latest,
                                                                     self.last_update,
                                                                     self.difference,
                                                                     self.bpa,
                                                                     self.rpd)


def scrap_page_for_table():
    page = requests.get(WEBSITE_URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find('div', id=DIV_ID).find(
        "table")

    return table


def get_table_headers(table=None):
    headers = table.find_all("th")
    headers_names = []
    for header in headers:
        header = header.get_text().strip()
        if header != "":
            headers_names.append(header)
    return headers_names


def get_table_companies(table=None):
    company_rows = table.find("tbody").find_all("tr")

    companies = []
    for company in company_rows:
        values = company.find_all("td")
        company_values = []
        for value in values:
            value = value.get_text().strip()

            if value != "":
                company_values.append(value)

        companies.append(company_values)

    return companies


def convert_table_to_object(headers=None, companies=None):
    object_companies = []
    for company in companies:

        zero = headers[0]
        one = headers[1]
        two = headers[2]
        three = headers[3]
        four = headers[4]
        five = headers[5]
        six = headers[6]
        seven = headers[7]
        eight = headers[8]
        nine = headers[9]
        ten = headers[10]
        eleven = headers[11]

        ticker = ''
        latest = ''
        difference = ''
        difference_percentage = ''
        max_value = ''
        min_value = ''
        volume = ''
        capital = ''
        rpd = ''
        per = ''
        bpa = ''
        last_update = ''

        if len(company) > 0:
            if zero == 'TKR':
                ticker = company[0]
            if one == u'\xdaltimo':
                latest = company[1]
            if two == u'Dif.':
                difference = company[2]
            if three == u'Dif. %':
                difference_percentage = company[3]
            if four == u'Max.':
                max_value = company[4]
            if five == u'Min.':
                min_value = company[5]
            if six == u'Volume':
                volume = company[6]
            if seven == u'Capital':
                capital = company[7]
            if eight == u'Rt/Div':
                rpd = company[8]
            if nine == u'PER':
                per = company[9]
            if ten == u'BPA':
                bpa = company[10]
            if eleven == 'Hora':
                last_update = company[11]

            comp = Company(ticker=ticker,
                           latest=latest,
                           difference=difference,
                           difference_percentage=difference_percentage,
                           max_value=max_value,
                           min_value=min_value,
                           volume=volume,
                           capital=capital,
                           rpd=rpd,
                           per=per,
                           bpa=bpa,
                           last_update=last_update)

            object_companies.append(comp)

    return object_companies

if __name__ == "__main__":
    # Create an engine that stores data in the local directory's
    # sqlalchemy_example.db file.
    engine = create_engine(SQLALCHEMY_DATABASE_URI)

    Base.metadata.create_all(bind=engine)

    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    table = scrap_page_for_table()
    headers = get_table_headers(table)
    companies = get_table_companies(table)
    companies_objects = convert_table_to_object(headers=headers, companies=companies)

    if companies_objects:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        for company in companies_objects:
            session.add(company)
            session.commit()
