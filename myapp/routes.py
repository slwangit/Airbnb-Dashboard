from myapp import app
import json, plotly, folium
from flask import render_template
from wrangling_scripts.wrangle_data import return_figures, return_map

@app.route('/')
@app.route('/airbnb-dashboard')
def index():

    figures = return_figures()

    # plot ids for the html id tag
    ids = ['figure-{}'.format(i) for i, _ in enumerate(figures)]

    # Convert the plotly figures to JSON for javascript in html template
    figuresJSON = json.dumps(figures, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html',
                           ids=ids,
                           figuresJSON=figuresJSON)
    
@app.route('/')
@app.route('/map')
def map():
    folium_map = return_map()
    return folium_map._repr_html_()
