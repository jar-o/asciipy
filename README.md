# ASCIIfy server 

## Overview

This is a **Python/Flask** app that allows you to upload images and convert them to
ASCII art.

It consists of a single endpoint `/` that accepts either `GET` or `POST`. A `GET` will provide an upload form, and a `POST` will allow you to upload a file.

## Getting started
**Prerequisites**: Python/pip

To get started, clone this repository, `cd` into the folder and do

```
pip install -r requirements.txt
```

### Running
You can run the server in "dev mode" by doing:

```
python app.py
```

It listens on port `5000`. You can also run it under [Gunicorn](http://gunicorn.org/), as you might in production (i.e. with 10 worker processes). See `run.sh`.

### Testing
Basic unit tests can be run simply by doing

```
python test.py
```

However, this implementation uses [HTTP Compression](https://en.wikipedia.org/wiki/HTTP_compression) on response to improve bandwidth utilization. To test that along with the unit tests, you will need `curl` and a Unix-like environment (Bash) with some standard utilities.

If you have those, you can run the "test suite" by doing

```
./test.sh
```
## API

### `POST /`
There is a single verb and endpoint that constitutes the API. Doing `GET /` will simply return a login form, which is primarily useful for browsers.

However, you can do `POST /` with `multipart/form-data`, and you will get a JSON response with the ASCII art:

```
{
  "ascii": "... the art ..."
}
```



Note that `POST /` does **not** expect JSON input. It expects only `multipart/form-data`. This is a design choice, because `multipart/form-data` allows you to upload straight binary data without inflating it with something like Base64.

You can specify to get non-JSON output by setting `output="raw"` as a form variable. An example of doing this with curl:

```
curl -sv -H 'Accept-Encoding: gzip,deflate' -X POST \
	-F "output=raw" -F "image=@test-images/batman.jpeg" \
	http://0.0.0.0:5000
```