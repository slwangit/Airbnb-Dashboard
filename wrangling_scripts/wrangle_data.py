import pandas as pd
import plotly.graph_objs as go
from statsmodels.tsa.seasonal import seasonal_decompose
from plotly.subplots import make_subplots
import folium

# Use this file to read in your data and prepare the plotly visualizations. The path to the data files are in
# `data/file_name.csv`

def clean_calendar():
    """
    The function clean_calendar is to clean the calendar dataset and make it ready for time series analysis.
    :param df: a pandas dataframe
    :return: a pandas dataframe
    """
    # read csv
    df = pd.read_csv('data/calendar.csv')
    
    # Drop missing values for those unavailable listings
    df = df.dropna()

    # Convert 'price' currency to numeric data
    df['price'] = df['price'].apply(lambda x: float(x.replace('$', '').replace(',', '')))

    # Convert 'date' to datetime type
    df['date'] = pd.to_datetime(df['date'])

    return df


def return_figures():
    """Creates four plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing the four plotly visualizations

    """

    # first chart plots the time series decomposition with 4 subplots
   
    # clean
    df = clean_calendar()
   
    # time series analysis
    # aggregate mean price by date
    tmp = df.groupby('date')[['price']].aggregate('mean')
    
    analysis = tmp['price'].copy()
    decompose_result = seasonal_decompose(analysis)


    observe = decompose_result.observed
    trend = decompose_result.trend
    seasonal = decompose_result.seasonal
    residual = decompose_result.resid
    
    
    graph_one = make_subplots(
            rows=4,
            cols=1,
            subplot_titles=["Observed", "Trend", "Seasonal", "Residuals"],
            vertical_spacing = 0.05
        ).add_trace(
            go.Scatter(x=observe.index, y=observe.values, mode="lines", name="Observed"),
            row=1,
            col=1,
        ).add_trace(
            go.Scatter(x=trend.index, y=trend.values, mode="lines", name="Trend"),
            row=2,
            col=1,
        ).add_trace(
            go.Scatter(x=seasonal.index, y=seasonal.values, mode="lines", name="Seasonal"),
            row=3,
            col=1,
        ).add_trace(
            go.Scatter(x=residual.index, y=residual.values, mode="lines", name="Residuals"),
            row=4,
            col=1,
        ).update_layout(
            height=920,
            title='Seasonality Decomposition of Price in Seattle',
            margin=dict(t=60), title_x=0.5, showlegend=False
        )
    
    # second chart plots the busiest time to travel to Seattle
    # as a bar chart
    
    # clean
    df = clean_calendar()

    # group by month
    df['month'] = df.date.dt.month

    groupby_month = df.groupby('month').count()[['price']].reset_index().rename(columns={'price': 'counts'})

    groupby_month.sort_values('counts', ascending=False, inplace=True)

    # plot
    graph_two = []   
    graph_two.append(
      go.Bar(
      x = groupby_month.month,
      y = groupby_month.counts,
      )
    )

    layout_two = dict(title = 'Booked Homestay Count in Seattle in 2016',
                xaxis = dict(title = 'Month'),
                yaxis = dict(title = 'Counts'),
                )

    # third chart plots weekday_decomposition
    # create weekday column
    df['month'] = df['date'].dt.month
    df['weekday'] = df['date'].dt.day_name()

    # Order x-axis categories
    df['weekday'] = pd.Categorical(df['weekday'],
                                   categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
                                               'Sunday'],
                                   ordered=True)

    # group by weekday and month
    tmp = df.groupby(['month', 'weekday']).mean()[['price']].reset_index()
    
    # plots
    months = tmp.month.unique().tolist()
    graph_three = []
    
    for month in months:
      x_val = tmp[tmp['month'] == month].weekday
      y_val =  tmp[tmp['month'] == month].price
      graph_three.append(
          go.Scatter(
          x = x_val,
          y = y_val,
          mode = 'lines',
          name = month
          )
        )

    layout_three = dict (title = 'Price by Weekday and Month',
                xaxis = dict(title = 'Weekday'),
                yaxis = dict(title = 'Price'),
                legend_title = 'Month',
                )
    
    
    # append all charts to the figures list
    figures = []
    figures.append(dict(data=graph_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    figures.append(dict(data=graph_three, layout=layout_three))

    return figures



def return_map():
    """
    The function listing_distribution_map() is to give an overview of listings distribution in Seattle area.
    :param none
    :return: a folium marker map object of listings scattered in Seattle, with room type legend and price popup
    """
    # read csv
    df = pd.read_csv('data/listings.csv')
    
    # seattle location
    seattle_location = [47.6062, -122.3321]

    # visualize on map
    # Instantiate a feature group for the listings
    listing = folium.map.FeatureGroup()

    # Loop through the listings adn add to the map
    latitude = df.latitude
    longitude = df.longitude
    types = df.room_type
    prices = df.price  # assign an uncleaned version for map popup
    df['price'] = df['price'].replace({'\$': '', '%': '', ',': ''}, regex=True).astype(float)

    for lat, lng, price, type in zip(latitude, longitude, prices, types):
        if type == 'Entire home/apt':
            listing.add_child(
                folium.CircleMarker(
                    location=[lat, lng],
                    popup=price,
                    radius=0.5,
                    color='red',
                )
            )
        elif type == 'Private room':
            listing.add_child(
                folium.CircleMarker(
                    location=[lat, lng],
                    popup=price,
                    radius=0.5,
                    color='green',
                )
            )
        else:
            listing.add_child(
                folium.CircleMarker(
                    location=[lat, lng],
                    popup=price,
                    radius=0.5,
                    color='yellow',
                )
            )

    # Add listings to map
    listing_map = folium.Map(location=seattle_location, zoom_start=12)
    listing_map.add_child(listing)


    return listing_map

