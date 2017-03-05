# Answers to some questions

### 1. How would you measure the performance of your service?

#### Baseline
Typically, I'd want to establish the basic performance of a server deploy. I've included `run.sh` that runs the service in a pretty standard server configuration under **Gunicorn**.

Here I use `wrk` to establish a baseline on the service itself, with 10 worker processes.


This is just doing `GET` on the endpoint and we're getting about 12K requests per second running on my Macbook.

```
% wrk -d20s -t10 -c200 http://0.0.0.0:5000

Running 20s test @ http://0.0.0.0:5000
  10 threads and 200 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    16.71ms    7.80ms  71.46ms   69.43%
    Req/Sec     1.21k   189.69     1.66k    58.65%
  241436 requests in 20.02s, 236.24MB read
  Socket errors: connect 0, read 56, write 0, timeout 0
Requests/sec:  12058.77
Transfer/sec:     11.80MB
```
#### Render response time
Because we're working with potentially large sets of data (images) it would pay to know the how the upload/render component performs. I've included a response time check in `test.sh` that uses `curl`, i.e.

```
time -p curl -s -H 'Accept-Encoding: gzip,deflate' \
        -X POST -F "output=raw" \
        -F "image=@test-images/batman.jpeg" \
        http://0.0.0.0:5000 -o /dev/null
```

Here you can see the times. Note that there is a reasonable improvement when we have caching turned on.

```
# NOT IN CACHE
real 1.19
user 0.00
sys 0.00

# CACHE HIT
real 1.02
user 0.00
sys 0.00

# CACHE HIT
real 1.02
user 0.00
sys 0.00
... etc ...
```

### 2. What are some strategies you would employ to make your service more scalable?

#### Caching
I've implemented a simple file-based cache in this server. It makes some difference, but there are a couple problems. 

1. It's wasteful to cache the ASCII output at the node level, since running multiple servers means a high chance of duplicate caching. Moving to a centralized cache configuration with high performance servers such as **Redis** would be preferred.
2. A caching server like **Redis** (or **memcached**) should be used regardless, since it's highly unlikely my rudimentary file caching mechanism can compare performance-wise.
3. Using a remote caching solution (single server or cluster) would take pressure off the node's CPU/disk and move the problem into one of response time -- making it a better fit for an async I/O service, which may provide some benefit.

#### HTTP Compression at proxy level
Because of the high redundancy in ASCII images, they compress really well. In my rather "toy" implementation here I'm doing HTTP Compression at the app level.

**Gunicorn** recommends running behind a proxy server such as **Nginx**. If we were to deploy using a proxy configuration, I'd move the HTTP Compression into the proxy. With **Nginx** this is a just a [configuration option](https://www.nginx.com/resources/admin-guide/compression-and-decompression/), which is convenient. 

#### Horizontal scale
This service would scale pretty easily by just adding nodes. Even my current implementation here could scale this way, without changes. (Non-optimally, to be sure.)

#### Offload processing to clients
An interesting possibility would be to have an endpoint that allows a client to check to see if the image the user is about to upload is already cached. If it is, they'd skip uploading the source image.

You could do this by providing the algorithm for generating the cache key from the file content. The client would perform this operation, send the key to the endpoint, and if the file is already in the cache, immediately download it. 

### 3. How would your design change if you needed to store the uploaded images?

My implementation stores the binary image to disk temporarily before passing it to the ASCII generator function, which expects a file path. After conversion, we delete the source image and cache the ASCII art version.

Ostensibly, we'd change this final delete step and use a storage service to save the binary image. My initial instinct would be to use Amazon's **S3** (or some equivalent).

We are already generating a unique(ish)* identifier for every uploaded file per the cache, so we could easily use that when storing to the central service.

_*We'd have to maybe take some steps to better ensure uniqueness for the identifier in this scenario, since the potential for collisions would be higher. I don't feel like the steps I've taken so far would be quite good enough._