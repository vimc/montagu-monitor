#!/usr/bin/env python3
from flask import Flask, Response
import random

app = Flask(__name__)

def render_metrics(metrics):
	output = ""
	for k,v in metrics.items():
		output += "{k} {v}\n".format(k=k, v=v)
	return Response(output, mimetype='text/plain')

@app.route('/metrics')
def metrics():
	return render_metrics({
		'demo_a': 0.0,
		'demo_b': random.random()
	})