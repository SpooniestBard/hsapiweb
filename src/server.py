from flask import Flask, render_template, request, redirect, url_for
from hsapi.client import HSApiClient

app = Flask(__name__, template_folder="web_content")

api_client = HSApiClient()

@app.route('/')
def default_route():
    """
    The default route for the application. Reroutes to the search page
    """
    return redirect(url_for('search'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    The search route handles API query submission and rendering of API output for hearthstone card
    searches
    """
    if request.form:
        search_params = (request.form.to_dict())
        search_params['class'] = ','.join(request.form.getlist('class'))
        search_params['attack'] = ','.join(request.form.getlist('attack'))
        search_params['health'] = ','.join(request.form.getlist('health'))
        search_params['manaCost'] = ','.join(request.form.getlist('manaCost'))
        card_list = api_client.search(**search_params)
        return render_template('search.j2', cards=card_list)
    return render_template('search.j2')
