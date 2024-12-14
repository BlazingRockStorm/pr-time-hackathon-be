# Press Release API

This is a simple API for storing and retrieving press releases.

## Running the API

1. Install the dependencies with `pip install -r requirements.txt`
2. Start the API with `uvicorn main:app --reload`

## Endpoints

### GET /

Returns a simple message.

### GET /press_releases

Returns a list of all press releases.

### GET /press_releases/{id}

Returns a single press release by it's ID.

## Data Model

A press release is represented as a JSON object with the following fields:

* `title`: the title of the press release
* `description`: the description of the press release
* `uid`: a unique identifier for the press release
* `image`: a list of URLs for images associated with the press release

## Storage

The API stores press releases in a MongoDB database. The database is specified by the `MONGODB_URI` environment variable. If this variable is not set, the API will use the default MongoDB URI `mongodb://localhost:27017/`.
