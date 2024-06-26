import pandas as pd
import plotly.express as px
from pandas.api.types import is_numeric_dtype
import os
#################################################################################

# Variables and data

DIR_PATH = os.path.dirname(os.path.realpath(__file__)) # path of directory to this folder
DATASET_SOURCE = 'https://www.kaggle.com/datasets/patrickzel/flight-delay-and-cancellation-dataset-2019-2023'


FLIGHTS = pd.read_csv(DIR_PATH + '/dataset/flights_tiny.csv', on_bad_lines='skip')
CODES = pd.read_csv(DIR_PATH + '/dataset/airports_codes.csv', sep = ';', on_bad_lines='skip')

FLIGHTS = FLIGHTS.iloc[:, 1:]
FLIGHTS_SAMPLE = FLIGHTS.sample(n = 1000, random_state=2024)
NUMERIC_COLS = list(FLIGHTS.select_dtypes(include=['number']).drop(['CANCELLED', 'DIVERTED', 'DOT_CODE', 'FL_NUMBER'], axis  = 1).columns)


# Color map of Airlines in dataset
AIRLINE_COLORS = {
    'Alaska Airlines Inc.': '#0033A0',
    'Allegiant Air': '#7A0048',
    'American Airlines Inc.': '#DF0024',
    'Delta Air Lines Inc.': '#8B1024',
    'Endeavor Air Inc.': '#8A8D8F',
    'Envoy Air': '#949CA0',
    'ExpressJet Airlines LLC d/b/a aha!': '#FF6600',
    'Frontier Airlines Inc.': '#1E4FA3',
    'Hawaiian Airlines Inc.': '#FF0000',
    'Horizon Air': '#74ACD1',
    'JetBlue Airways': '#0071BC',
    'Mesa Airlines Inc.': '#5276A7',
    'PSA Airlines Inc.': '#004A85',
    'Republic Airline': '#3B75B3',
    'SkyWest Airlines Inc.': '#0033A0',
    'Southwest Airlines Co.': '#EE352E',
    'Spirit Air Lines': '#FF7F00',
    'United Air Lines Inc.': '#002244'
}


with open(DIR_PATH + '/dataset/dictionary_nicer.html', 'r') as f:
    DESCRIPTION_HTML = f.read()


#################################################################################
# Functions

def summarize_routes_from_origin(flights:pd.DataFrame, origin: str) -> pd.DataFrame:
    filtered_flights = flights[flights['ORIGIN'] == origin]

    # dest = row['DEST']
    # origin_city = row['ORIGIN_CITY']
    # airline = row['AIRLINE']
    # dest_city = row['DEST_CITY']
    # distance = row['mean_distance']

    summary = filtered_flights.groupby('DEST').agg(
                                        ORIGIN = ('ORIGIN', 'first'),
                                        ORIGIN_CITY=('ORIGIN_CITY', 'first'),
                                        DEST_CITY=('DEST_CITY', 'first'),
                                        AIRLINE = ('AIRLINE', 'first'),
                                        mean_crs_dep_time=('CRS_DEP_TIME', 'mean'),
                                        mean_dep_time=('DEP_TIME', 'mean'),
                                        mean_dep_delay=('DEP_DELAY', 'mean'),
                                        mean_taxi_out=('TAXI_OUT', 'mean'),
                                        mean_wheels_off=('WHEELS_OFF', 'mean'),
                                        mean_wheels_on=('WHEELS_ON', 'mean'),
                                        mean_taxi_in=('TAXI_IN', 'mean'),
                                        mean_crs_arr_time=('CRS_ARR_TIME', 'mean'),
                                        mean_arr_time=('ARR_TIME', 'mean'),
                                        mean_arr_delay=('ARR_DELAY', 'mean'),
                                        mean_cancelled=('CANCELLED', 'mean'),
                                        mean_diverted=('DIVERTED', 'mean'),
                                        mean_crs_elapsed_time=('CRS_ELAPSED_TIME', 'mean'),
                                        mean_elapsed_time=('ELAPSED_TIME', 'mean'),
                                        mean_air_time=('AIR_TIME', 'mean'),
                                        mean_distance=('DISTANCE', 'mean'),
                                        ).reset_index()
    

    return summary


def summarize_from_origin(flights: pd.DataFrame, origin: str):
    filtered_flights = flights[flights['ORIGIN'] == origin]
    
    flights_groups = filtered_flights.groupby('DEST')

    # Group: Airline and Airport Information
    summary_airports = flights_groups.agg(
        ORIGIN=('ORIGIN', 'first'),
        DEST=('DEST', 'first'),
        AIRLINE=('AIRLINE', lambda x: ', '.join(x.unique())),
        AIRLINE_DOT=('AIRLINE_DOT', lambda x: ', '.join(x.unique())),
        AIRLINE_CODE=('AIRLINE_CODE', lambda x: ', '.join(x.unique())),
        DOT_CODE=('DOT_CODE', 'first'),
        ORIGIN_CITY=('ORIGIN_CITY', 'first'),
        DEST_CITY=('DEST_CITY', 'first')
    )

    # Group: Departure and Arrival Times
    summary_times = flights_groups.agg({
        'ORIGIN': 'first',
        'DEST': 'first',
        'CRS_DEP_TIME': 'mean',
        'DEP_TIME': 'mean',
        'DEP_DELAY': 'mean',
        'CRS_ARR_TIME': 'mean',
        'ARR_TIME': 'mean',
        'ARR_DELAY': 'mean'
    })

    # Group: In-Flight Times
    summary_in_flight_times = flights_groups.agg({
        'ORIGIN': 'first',
        'DEST': 'first',
        'TAXI_OUT': 'mean',
        'WHEELS_OFF': 'mean',
        'WHEELS_ON': 'mean',
        'TAXI_IN': 'mean',
        'AIR_TIME': 'mean'
    })

    # Group: Flight Duration and Distance
    summary_duration_distance = flights_groups.agg({
        'ORIGIN': 'first',
        'DEST': 'first',
        'CRS_ELAPSED_TIME': 'mean',
        'ELAPSED_TIME': 'mean',
        'DISTANCE': 'mean'
    })

    # Group: Flight Status
    summary_flight_status = flights_groups.agg({
        'ORIGIN': 'first',
        'DEST': 'first',
        'CANCELLED': 'sum',
        'DIVERTED': 'sum'
    })

    # Combine all summaries into a single dictionary
    summary = {
        'airports': summary_airports,
        'times': summary_times,
        'in_flight_times': summary_in_flight_times,
        'duration_distance': summary_duration_distance,
        'flight_status': summary_flight_status
    }

    return summary


def get_origins(flights):
    originandcity = flights['ORIGIN'] + ', ' + flights['ORIGIN_CITY']
    return originandcity.unique().tolist()

def get_dests(flights):
    return flights['DEST'].unique().tolist()


def get_coords(codes, airport):
    coords = codes.loc[codes['Airport Code'] == airport][['Latitude', 'Longitude']].iloc[0].to_dict()

    return coords



ORIGIN_AIRPORTS = get_origins(FLIGHTS)