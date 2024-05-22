from flask import Flask, render_template
import requests
import json

# Feel free to import additional libraries if you like
from datetime import datetime

app = Flask(__name__, static_url_path="/static")

# Paste the API-key you have received as the value for "x-api-key"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/hal+json",
    "x-api-key": "api-key-here",
}


# Example of function for REST API call to get data from Lime
def get_api_data(headers, url):
    # First call to get first data page from the API
    response = requests.get(url=url, headers=headers, data=None, verify=False)

    # Convert response string into json data and get embedded limeobjects
    json_data = json.loads(response.text)
    limeobjects = json_data.get("_embedded").get("limeobjects")

    # Check for more data pages and get thoose too
    nextpage = json_data.get("_links").get("next")
    while nextpage is not None:
        url = nextpage["href"]
        response = requests.get(url=url, headers=headers, data=None, verify=False)

        json_data = json.loads(response.text)
        limeobjects += json_data.get("_embedded").get("limeobjects")
        nextpage = json_data.get("_links").get("next")

    return limeobjects



# for task 4.2: fetch the api of individual deal objects specific to a company
def get_company_deals(company_id):
    company_id_str = str(company_id)
    url = (
        "https://appercase.testing.limecrm.cloud/appercase/api/v1/limeobject/company/" + company_id_str + "/deal/"
    )

    params = "?dealstatus=agreement"
    url = url + params
    company_deals = get_api_data(headers=headers, url=url)

    return company_deals


# for task 4.3
def get_company_deals_dates(company_id):
    company_id_str = str(company_id)
    url = (
        "https://appercase.testing.limecrm.cloud/appercase/api/v1/limeobject/company/" + company_id_str + "/deal/"
    )

    params = "?dealstatus=agreement"
    url = url + params
    company_deals = get_api_data(headers=headers, url=url)

    closed_dates = []
    for deal in company_deals:
        closed_date = deal.get("closeddate")
        # if the list of dates is not empty
        if closed_date:
            closed_dates.append(closed_date)

    return closed_dates


# Index page
@app.route("/")
def index():

    deal_base_url = (
        "https://appercase.testing.limecrm.cloud/appercase/api/v1/limeobject/deal/"
    )
    # params = "?_limit=50"
    params = "?dealstatus=agreement&min-closeddate=2023-01-01T00:00Z&max-closeddate=2023-12-31T23:59Z"
    url = deal_base_url + params
    response_deals = get_api_data(headers=headers, url=url)


    # fetch the api of companies
    company_base_url = (
        "https://appercase.testing.limecrm.cloud/appercase/api/v1/limeobject/company/"
    )
    c_params = "?_limit=50"
    c_url = company_base_url + c_params
    response_companies = get_api_data(headers=headers, url=c_url)



    # keys represent each month of the year, values represent the number of deals per month
    # handled this way in order to include the months which had 0 deals (Feb & Aug in this case)
    deals_per_month = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        7: 0,
        8: 0,
        9: 0,
        10: 0,
        11: 0,
        12: 0
    }

    total_won_value = 0
    deals_per_company = {}
    for deal in response_deals:
        value = int(deal.get("value"))
        # task 1: get the values
        total_won_value += value

        # task 2
        closed_date = deal.get("closeddate")
        # use the datetime class to fetch the month
        date_time = datetime.fromisoformat(closed_date)
        month = date_time.month
        
        # add 1 every time we see a won deal
        deals_per_month[month] += 1
        
        # task 3
        company_id = deal.get("company")    
        # already in the dictionary: add to its existing value
        if company_id in deals_per_company:
            deals_per_company[company_id] += value

        else:
            # company not in the dictionary
            deals_per_company[company_id] = value


    # task 1: calculate average
    average_won_value = total_won_value / len(response_deals)



    # task 4
    for company in response_companies:
        company_id = company.get("_id")

        # task 4.1: note: did not use "put" since not necessary
        if company_id in deals_per_company:
            company["buyingstatus"]["key"] = "active"
            company["buyingstatus"]["text"] = "Active customer"
        
        # task 4.2: companies that have never bought anything
        else:
            # has status "notinterested", we continue to loop through the rest
            if company.get("buyingstatus").get("key") == "notinterested":
                continue
            
            # has not bought anything + does not have status "notinterested" (array of deal objects is empty)
            if not get_company_deals(company_id):
                company["buyingstatus"]["key"] = "prospect"
                company["buyingstatus"]["text"] = "Prospect"

        # task 4.3: bought something before 2023:
        closed_dates = get_company_deals_dates(company_id)
        years = []
        for date in closed_dates:
            # extract the first 4 characters, which is the digits representing the year
            years.append(date[:4])

        for year in years:
            if int(year) < 2023:
                company["buyingstatus"]["key"] = "excustomer"
                company["buyingstatus"]["text"] = "Former customer"



    # task 3 modification: change the id in deals_per_company to company name
    updated_deals_per_company = {}
    for company in response_companies:
        for id, value in deals_per_company.items():
            if id == company["_id"]:
                updated_deals_per_company[company.get("name")] = value

    # update our dictionary
    deals_per_company = updated_deals_per_company



    return render_template(
        "home.html",
        average_won_value=average_won_value,
        deals_per_month=deals_per_month,
        deals_per_company=deals_per_company,
        companies=response_companies
    )




if __name__ == "__main__":
    app.secret_key = "somethingsecret"
    app.run(debug=True)
