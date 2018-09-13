from flask import Response

from helpers import seconds_elapsed_since


def render_metrics(metrics):
    output = ""
    for k,v in metrics.items():
        output += "{k} {v}\n".format(k=k, v=v)
    return Response(output, mimetype='text/plain')


def label_metrics(metrics, labels):
    label_items = ",".join("{k}={v}".format(k=k, v=v) for k, v in labels.items())
    label = "{" + label_items + "}"

    labelled = {}
    for k, v in metrics.items():
        labelled[k + label] = v
    return labelled


def bucket_metrics(bucket_id, s3):
    bucket = s3.get_bucket(bucket_id)
    metrics = {
        "bucket_exists": bucket is not None
    }
    if bucket:
        files = list(bucket.objects.all())
        metrics["bucket_files_count"] = len(files)
        if files:
            last_modified = max(f.last_modified for f in files)
            age = seconds_elapsed_since(last_modified)
            metrics["bucket_files_time_since_last_modified_minutes"] = age / 60
            metrics["bucket_files_time_since_last_modified_hours"] = age / (60 * 60)
            metrics["bucket_files_time_since_last_modified_days"] = age / (24 * 60 * 60)
            size = sum(f.size for f in files)
            metrics["bucket_files_total_size_bytes"] = size
            metrics["bucket_files_total_size_kb"] = size / 1024
            metrics["bucket_files_total_size_mb"] = size / (1024 * 1024)
            metrics["bucket_files_total_size_gb"] = size / (1024 * 1024 * 1024)

    return label_metrics(metrics, {"id": bucket_id})
