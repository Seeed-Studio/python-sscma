## Run REST API Server

```sh
python3 sscma.cli server
```

Arguments:

- `--host`: host address of the server, default: `127.0.0.1`
- `--port`: port number of the server, default: `8000`
- `--ssl`: enable SSL, default: `False`
- `--ssl_certfile`: SSL certificate file, default: `None`
- `--ssl_keyfile`: SSL key file, default: `None`
- `--max_workers`: maximum number of workers, default: `4`

Virtual environment is recommended.

```sh
conda create -n bytetrack_server python=3.10
conda activate bytetrack_server
```

## API Reference

The server supports the following HTTP methods, using a HTTP debug tool like [HTTPie](https://httpie.io/app) or `curl` to test the API.

### GET

#### Get all active sessions

Requset:

```sh
curl -X GET http://127.0.0.1:8000
```

Response:

```json
{
    "sessions": [],
    "max_sessions": 32,
    "active_threads": 2
}
```

#### Create a new session

Request:

```sh
curl -X POST http://127.0.0.1:8000 \
    -H "Content-Type: application/json" \
    -H "Session-Id: 72d6be50" \
    --data-binary @body.json
```

Request body:

```json
{
    "resolution": [240, 240],
    "tracker_config": {
        "track_thresh": 0.25,
        "track_buffer": 30,
        "match_thresh": 0.8,
        "frame_rate": 30
    },
    "trace_config": {
        "trace_position": "CENTER",
        "trace_length": 30
    },
    "annotation_config": {
        "labels": {
            "0": "Person",
            "1": "Car",
            "2": "Bicycle",
            "3": "Motorcycle",
            "4": "Bus",
            "5": "Truck"
        },
        "bbox_thickness": 2,
        "bbox_text_scale": 0.3,
        "bbox_text_padding": 5,
        "polygon_thickness": 1,
        "polygon_text_scale": 0.3,
        "polygon_text_padding": 5,
        "trace_line_thickness": 2
    },
    "filter_regions": {
        "Region A": {
            "polygon": [[12, 34], [56, 78], [90, 12], [34, 56]],
            "triggering_position": "CENTER"
        },
        "Region B": {
            "polygon": [[10, 10], [200, 10], [200,200], [10, 200], [30, 30]],
            "triggering_position": "CENTER"
        }
    }
}
```

- `trace_position` and `triggering_position` could be one of the following:
    - CENTER
    - CENTER_LEFT
    - CENTER_RIGHT
    - TOP_CENTER
    - TOP_LEFT
    - TOP_RIGHT
    - BOTTOM_LEFT
    - BOTTOM_CENTER
    - BOTTOM_RIGHT

- `filter_regions` is a dictionary of regions (can be empty), each region is a dictionary of `polygon` and `triggering_position`.

- `polygon` is a list of points, each point is a list of `[x, y]`, minimum 3 points are required.

- If a session exists already, the request will repleace the existing session with new configurations.


### POST

#### Create or attach detection results to a session

Request:

```sh
curl -X POST http://127.0.0.1:8000/72d6be50 \
    -H "Content-Type: application/json" \
    --data-binary @body.json
```

Request body:

```json
{
    "boxes": [
        [20, 23, 12, 24, 89, 0], [12, 34, 45, 56, 78, 1]
    ],
    "image": "data:image/any;base64,..."
}
```

- `boxes` is a list of bounding boxes, each box is a list of `[cx, cy, w, h, score, label]`.

- `image` is optional, if not provided or failed to decode from base64 string, the server will return the annotated image as transparent mask in the response.

Response:

```json
{
    "tracked_boxes": [
        [20, 23, 12, 24, 89, 0, 1],
        [12, 34, 45, 56, 78, 1, 2]
    ],
    "filtered_regions": {
        "Region A": [],
        "Region B": [2]
    },
    "annotated_image": "data:image/png;base64,..."
}
```

- `tracked_boxes` is a list of tracked bounding boxes, each box is a list of `[cx, cy, w, h, score, label, tracker_id]`.

- `filtered_regions` is a dictionary of filtered regions, each region is a list of tracker IDs which bounding boxes inside the region.

- `annotated_image` is base64 encoded annotated image, PNG format.


### DELETE

#### Remove a active session

Request:

```sh
curl -X DELETE http://127.0.0.1:8000 \
    -H "Content-Type: application/json" \
    -H "Session-Id: 72d6be50"
```
