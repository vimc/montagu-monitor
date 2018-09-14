#!/usr/bin/env python3
from flask import Flask

from helpers import combine_dictionaries
from metrics import bucket_metrics, render_metrics
from s3 import S3Helper

app = Flask(__name__)


@app.route('/metrics')
def metrics():
    bucket_ids = [
        'montagu-db',
        'montagu-orderly',
        'montagu-teamcity',
        'montagu-vault'
    ]
    s3 = S3Helper()
    metrics = combine_dictionaries(bucket_metrics(b, s3) for b in bucket_ids)
    return render_metrics(metrics)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=5000)
