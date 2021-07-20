import re


def map_renderer(map_html: str) -> str:
    """Takes as input the string of the html made by the searchPipeline and
        outputs a flask-friendly string of html"""
    map_html = re.sub('<!DOCTYPE html>', '{% extends "base.html" %} {% block title %}Map Rendered{% endblock %}',
                      map_html)
    map_html = re.sub('<head>', '{% block content%}', map_html)
    map_html = re.sub('</head>', '', map_html)
    map_html = re.sub('<body>', '', map_html)
    map_html += '{% endblock%}'
    return map_html
