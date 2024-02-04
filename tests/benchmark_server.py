import concurrent.futures
import requests
import json
import time
import random

from copy import deepcopy


def generate_session_id():
    return str(random.randint(100000, 999999))


port = "8000"
host = "127.0.0.1"
concurrent_requests = 16
repeat_requests = 128
max_sessions = 8
timeout = 60

session_id = generate_session_id()
before_request_ctx = {
    "url": f"http://{host}:{port}",
    "headers": {
        "Content-Type": "application/json",
        "Session-Id": session_id,
    },
    "body": {
        "tracker_config": {
            "track_thresh": 0.25,
            "track_buffer": 30,
            "match_thresh": 0.8,
            "frame_rate": 30,
        },
        "annotation_config": {
            "resolution": [240, 240],
            "polygon": {
                "thickness": 2,
                "text_scale": 0.5,
                "text_thickness": 1,
                "text_padding": 3,
            },
            "bounding_box": {"thickness": 2},
            "tracing": {"position": "CENTER", "trace_length": 30, "trace_thickness": 1},
            "labeling": {
                "text_scale": 0.3,
                "text_thickness": 1,
                "text_padding": 3,
                "text_position": "TOP_LEFT",
                "label_map": {
                    "0": "Person",
                    "1": "Car",
                    "2": "Truck",
                },
            },
            "heatmap": {
                "position": "BOTTOM_CENTER",
                "opacity": 0.5,
                "radius": 10,
                "kernel_size": 5,
            },
        },
        "regions_config": {
            "Region A": {
                "polygon": [[12, 34], [56, 78], [90, 12], [34, 56]],
                "triggering_position": "CENTER",
            },
            "Region B": {
                "polygon": [[10, 10], [200, 10], [200, 200], [10, 200], [30, 30]],
                "triggering_position": "CENTER",
            },
        },
    },
}

request_without_annotation_ctx = {
    "url": f"http://{host}:{port}/{session_id}",
    "headers": {
        "Content-Type": "application/json",
    },
    "body": {
        "boxes": [[20, 23, 12, 24, 89, 0], [12, 34, 45, 56, 78, 1]],
        "annotations": [],
    },
}

request_with_annotation_ctx = {
    "url": f"http://{host}:{port}/{session_id}",
    "headers": {
        "Content-Type": "application/json",
    },
    "body": {
        "boxes": [[20, 23, 12, 24, 89, 0], [12, 34, 45, 56, 78, 1]],
        "annotations": [
            ["polygon", "bounding_box", "tracing", "labeling"],
            ["polygon", "bounding_box", "tracing", "labeling", "heatmap"],
        ],
    },
}


def benchmark_single(ctx, name):

    print(f"Running single session benchmark for '{name}':")

    request_url = ctx["url"]
    request_headers = ctx["headers"]
    request_data = json.dumps(ctx["body"])

    def send_request(_):
        response = requests.post(
            request_url, headers=request_headers, data=request_data, timeout=timeout
        )
        return response.status_code

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=concurrent_requests
    ) as executor:
        success = 0
        s = time.monotonic_ns()
        futures = [executor.submit(send_request, i) for i in range(repeat_requests)]
        for future in concurrent.futures.as_completed(futures):
            success += 1 if future.result() == 200 else 0
        e = time.monotonic_ns()
        print(
            f"  success: {success}/{repeat_requests} in {(e-s)/1e6} ms, average per request: {(e-s)/repeat_requests/1e6} ms\n"
        )


benchmark_single(before_request_ctx, "spawn")
benchmark_single(request_without_annotation_ctx, "request_without_annotation")
benchmark_single(request_with_annotation_ctx, "request_with_annotation")


def benchmark_multiple(ctxs, name):
    print(f"Running multiple session benchmark for '{name}', sessions {len(ctxs)}:")

    url_list = [ctx["url"] for ctx in ctxs]
    headers_list = [ctx["headers"] for ctx in ctxs]
    data_list = [json.dumps(ctx["body"]) for ctx in ctxs]

    occurrences = repeat_requests // max_sessions
    indices = [i for i in range(max_sessions) for _ in range(occurrences)]
    remainder = repeat_requests % max_sessions
    if remainder != 0:
        indices += random.sample(range(max_sessions), remainder)
    random.shuffle(indices)

    def send_request(url, headers, data):
        response = requests.post(url, headers=headers, data=data, timeout=timeout)
        return response.status_code

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=concurrent_requests
    ) as executor:
        success = 0
        s = time.monotonic_ns()
        futures = [
            executor.submit(send_request, url_list[i], headers_list[i], data_list[i])
            for i in indices
        ]
        for future in concurrent.futures.as_completed(futures):
            success += 1 if future.result() == 200 else 0
        e = time.monotonic_ns()
        print(
            f"  success: {success}/{len(indices)} in {(e-s)/1e6} ms, average per request: {(e-s)/len(indices)/1e6} ms\n"
        )


session_ids = []
while len(session_ids) < max_sessions:
    i = generate_session_id()
    if i not in session_ids:
        session_ids.append(i)

bofore_request_ctxs = []
for i in session_ids:
    ctx = deepcopy(before_request_ctx)
    ctx["headers"]["Session-Id"] = i
    bofore_request_ctxs.append(ctx)

request_without_annotation_ctxs = []
for i in session_ids:
    ctx = deepcopy(request_without_annotation_ctx)
    ctx["url"] = f"http://{host}:{port}/{i}"
    request_without_annotation_ctxs.append(ctx)

request_with_annotation_ctxs = []
for i in session_ids:
    ctx = deepcopy(request_with_annotation_ctx)
    ctx["url"] = f"http://{host}:{port}/{i}"
    request_with_annotation_ctxs.append(ctx)

benchmark_multiple(bofore_request_ctxs, "spawn")
benchmark_multiple(request_without_annotation_ctxs, "request_without_annotation")
benchmark_multiple(request_with_annotation_ctxs, "request_with_annotation")


def cleanup():
    response = requests.get(url=f"http://{host}:{port}", timeout=timeout)
    sessions = response.json()["sessions"]
    for session in sessions:
        headers = {
            "Content-Type": "application/json",
            "Session-Id": session,
        }
        requests.delete(url=f"http://{host}:{port}", headers=headers, timeout=timeout)


cleanup()
