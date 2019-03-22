
from __future__ import print_function
from trend import Trend
import argparse
import intrinio_sdk
from intrinio_sdk.rest import ApiException
from pprint import pprint
intrinio_sdk.ApiClient().configuration.api_key['api_key'] = '<YOUR INTRINIO API KEY HERE'

company_api = intrinio_sdk.CompanyApi()


def historical_data_per_company(ticker, start_date):
    if start_date:
        history_response = company_api.get_company_historical_data(ticker, 'adj_close_price', start_date=start_date,
                                                               end_date='2019-03-20', page_size=8000)
    else:
        history_response = company_api.get_company_historical_data(ticker, 'adj_close_price', start_date='2003-01-01',
                                                                   end_date='2019-03-20', page_size=8000)
    values = []
    historical_data = history_response.historical_data
    for value in historical_data:
        values.append(value.value)
    pprint(ticker)
    historical_data.reverse()
    values.reverse()
    trends = start_historical_check(values, historical_data)
    for trend in trends:
        print("Price %f on %s went down %f%% before regaining full value. This took %s days." %
              (trend.start_value, trend.start_date, trend.percentage *100, trend.get_trend_length_in_days()))
        # pprint("Start Date: %s End Date: %s Percentage: %f" % (trend.start_date, trend.end_date, (trend.percentage * 100)))
        # pprint("Trend Length: %d Days" % trend.get_trend_length_in_days())

    percentages = []
    for trend in trends:
        if trend.percentage >= .05:
            percentages.append(trend.percentage)

    sum_of_percentages = sum(percentages)

    pprint("The average days to recovery for over 5%% is: %d" % (sum_of_percentages/len(percentages)))

def start_historical_check(values, historical_data):
    value_count = len(values)
    start_index = 0
    end_index = 0
    current_value = values[start_index]

    trends = []
    while start_index < value_count:
        if (values[start_index] - current_value) < 0:  # this means that the value has dropped
            return_trend = start_trend(values, historical_data, start_index, end_index)
            if return_trend[0] is not None:
                trends.append(return_trend[0])
            start_index = return_trend[1]
            start_index += 1
            end_index = start_index
        else:
            current_value = values[start_index]
            start_index += 1
            end_index = start_index
    return trends


def start_trend(values, historical_data, start_index, end_index):
    if start_index+1 < len(values):
        new_trend = Trend()
        new_trend.start_value = values[start_index]
        new_trend.start_date = historical_data[start_index].date
        temp_timeline = values[start_index+1:]
        min_value = temp_timeline[0]
        for value in temp_timeline:
            if value < min_value:
                min_value = value

            if values[start_index] > value:
                end_index += 1
            else:
                new_trend.end_value = value
                new_trend.end_date = historical_data[end_index].date
                break
        start_index = end_index
        if new_trend.end_date != new_trend.start_date:
            # do not record one day trends
            if (new_trend.end_value == 0.0) and (min_value > 0.0) and (end_index == len(values)-1):
                # if we are still trending down at the end of timeline,
                # we will have to set to last date and value in list
                new_trend.end_value = values[len(values)-1]
                new_trend.end_date = historical_data[len(historical_data)-1].date
            new_trend.min_value = min_value
            new_trend.percentage = 1 - (new_trend.min_value / new_trend.start_value)
            return [new_trend, start_index]
        else:
            return [None, start_index]


def print_symbols(data):
    company_list = data.companies
    for company in company_list:
        pprint(company.ticker)


try:
    # api_response = company_api.get_all_companies()
    parser = argparse.ArgumentParser(description="Historical analysis on stock price drops")
    parser.add_argument('ticker', help="The ticker symbol")
    parser.add_argument('--start_date', help="Date to start analysis (format '1970-01-01)")
    args = parser.parse_args()
    historical_data_per_company(args.ticker, args.start_date)
    exit(1)
except ApiException as e:
    print("Exception when calling CompanyApi->filter_companies: %s\n" % e)



