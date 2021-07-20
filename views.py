import json

from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect, session
from flask_login import login_required, current_user

from mapRender import map_renderer
from searchPipeline import search_pipeline
from . import db
from .models import Contract

views = Blueprint('views', __name__)


@views.route('/saved-contracts', methods=['GET', 'POST'])
@login_required
def saved_contracts():
    if request.method == 'POST':
        contract = request.form.get('contract')
        if len(contract) < 1:
            flash('Contract is too short!', category='error')
        else:
            new_contract = Contract(data=contract, user_id=current_user.id)
            db.session.add(new_contract)
            db.session.commit()
            flash('Contract added!', category='success')

    return render_template("contracts.html", user=current_user)


@views.route('/delete-contract', methods=['POST'])
def delete_contract():
    contract = json.loads(request.data)
    contractId = contract['contractId']
    contract = Contract.query.get(contractId)
    if contract:
        if contract.user_id == current_user.id:
            db.session.delete(contract)
            db.session.commit()

    return jsonify({})


@views.route('/', methods=['GET', 'POST'])
@views.route('/wizard', methods=['GET', 'POST'])
def wizard():
    if request.method == 'POST':
        search_dict = {
            'state': request.form.get('state'),
            'city': request.form.get('city'),
            'business': request.form.get('business'),
            'keywords1': request.form.get('keywords1'),
            'keywords2': request.form.get('keywords2'),
            'keywords3': request.form.get('keywords3')
        }
        session['search_dict'] = search_dict

        return redirect(url_for('.wait_search'))

    else:
        return render_template("wizard.html", user=current_user)


@views.route('/wait-search')
def wait_search():
    """Html displays loading, after </body> calls function to start search"""
    return render_template("wait_search.html", user=current_user)


@views.route('/map-contracts')
def map_contracts():
    search_dict = session.get('search_dict', None)
    print(search_dict)
    map_to_render = map_renderer(search_pipeline(search_dict)[0])
    with open('website/template/map_to_render.html', 'w') as m:
        m.write(map_to_render)
    return render_template("map_to_render.html", user=current_user)


@views.route('/post-location', methods=['POST'])
def post_location():
    # data = json.loads(request.data)
    # location = data['location']
    data = request.get_json()
    print(data)

    return jsonify(data)


@views.route('/get-address')
def get_address():
    # data = json.loads(request.data)
    # location = data['location']
    data = request.get_json()
    print(data)

    return jsonify(data)
