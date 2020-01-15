import pandas as pd
from decimal import Decimal
from urllib.parse import urlparse
import datefinder


class FundingResource:
    required_fields = ["name", "source", "keywords", "main_cat"]

    def __init__(self, **kwargs):
        ## Check for required fields
        for field in FundingResource.required_fields:
            if field not in list(kwargs.keys()):
                raise Exception(
                    "A funding resource object needs a {} descriptor".format(
                        field))

        # Assign fields
        self.id = 0
        self.name = kwargs.get("name", False)
        self.source = kwargs.get("source", False)
        self.URL = kwargs.get("URL", False)
        self.deadline = kwargs.get("deadline", False)
        self.description = kwargs.get("description", False)
        self.criteria = kwargs.get("criteria", False)
        self.amount = kwargs.get("ammount", False)
        self.restrictions = kwargs.get("restrictions", False)
        self.timeline = kwargs.get("timeline", False)
        self.point_of_contact = kwargs.get("point_of_contact", False)
        self.ga_contact = kwargs.get("ga_contact", False)
        self.keywords = kwargs.get("keywords", False)
        self.main_cat = kwargs.get("main_cat", False)

        self._clean_ammount()
        self._clean_url()
        self._clean_dates()

    def _clean_ammount(self):
        if self.amount:
            try:
                self.amount = Decimal(re.sub("[^0-9]", "", self.amount))
            except:
                self.amount = False

    def _clean_url(self):
        if self.URL:
            self.URL = urlparse(self.URL, scheme="http")

    def _clean_dates(self):
        if self.deadline:
            deadlines = list(datefinder.find_dates(self.deadline))
            if len(deadlines) is not 0:
                self.deadline = deadlines[0]
            else:
                self.deadline = False

    def set_id(self,id):
        self.id = id

    def __repr__(self):
        return "{} for {} due {}".format(self.name, self.amount,
                                         self.deadline)


class FundingResources:
    funding_resources = []

    def __init__(self, df):
        for iloc in range(1, len(df)):
            FundingResources.funding_resources.append(
                FundingResource(**df.iloc[iloc]))
            FundingResources.funding_resources[-1].set_id(
                len(FundingResources.funding_resources))

    def find_by(self, keyword, value):
        matches = []
        for fund in FundingResources.funding_resources:
            if fund.__dict__[keyword]:
                if value in fund.__dict__[keyword]:
                    matches.append(fund.__dict__)

        return matches

    def find_deadline_after_date(self, date):
        pass

    def find_ammount_greater(self, ammount):
        pass

    def find_by_keywords(self, keywords):
        pass

    def find_by_category(self, category):
        pass

    def filter_by_type(self, type_of_funding, type_criteria):
        matches = []
        for fund in FundingResources.funding_resources:
            if fund.__dict__["main_cat"]:
                if fund.__dict__["keywords"]:
                    if fund.__dict__["main_cat"] == \
                            type_of_funding and type_criteria in \
                            fund.__dict__["keywords"]:
                        matches.append(fund.__dict__)
        return matches

