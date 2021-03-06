import requests

from flask import Blueprint
from flask import request, url_for, render_template, jsonify, make_response
from flask import current_app as app

from .so2html import conll_to_standoff, standoff_to_html, generate_legend
from .so2html import sort_types


TAGGER_URL = 'http://127.0.0.1:8080'


bp = Blueprint('view', __name__, static_folder='static', url_prefix='/tagdemo')


@bp.route('/')
def root():
    return show_index()


@bp.route('/')
def show_index():
    return render_template('index.html')


@bp.route('/tag', methods=['GET', 'POST'])
def tag_text():
    text = str(request.values['text'])
    format_ = str(request.values.get('format', 'html'))

    req = requests.get(TAGGER_URL, data={ 'text': text })
    annotations = conll_to_standoff(text, req.text)

    if format_ == 'json':
        anns = [a.to_dict(text) for a in annotations]
        return jsonify(anns)
    elif format_ == 'tsv':
        r = make_response(req.text)
        r.mimetype = 'text/plain'
        return r
    elif format_ == 'ann':
        annstr = '\n'.join(
            a.to_standoff(text, i+1) for i, a in enumerate(annotations))
        r = make_response(annstr)
        r.mimetype = 'text/plain'
        return r

    # assume html format
    types = sort_types(list(set([a.type for a in annotations])))
    content = standoff_to_html(text, annotations)
    legend = generate_legend(types, include_style=True)
    annotated_strings = sorted(list(set([
        text[a.start:a.end] for a in annotations
    ])))
    return render_template('visualize.html', **locals())
