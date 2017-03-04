import os, time, md5
from flask import Flask, flash, request, Response, redirect, render_template
from flask_compress import Compress
from werkzeug.utils import secure_filename
from lib import cache

###############################################################################
# Config and init
###############################################################################

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']

app = Flask(__name__)
app.config['CACHE_FOLDER'] = 'cache'
app.secret_key = os.environ.get('SECRET_KEY', '123abc')

# This enables HTTP compression on the responses, which is helpful since with
# ascii art there should be plenty of repeated characters.
app.config['COMPRESS_MIMETYPES'] = [
        'text/html',
        'text/css',
        'text/xml',
        'text/text'
    ] 
Compress(app)

# Our simple caching mechanism for the ascii art we generate.
cache = cache.AsciiCache(app.config['CACHE_FOLDER'])

###############################################################################
# Helpers
###############################################################################

# This decorator handles the image upload scenario on the given endpoint. It
# also implements a simple cache that stores the ascii art for a given image ID
# and returns that instead of rendering the image to ascii each time. NOTE that
# in a production deploy, we'd probably want to use an actual caching server,
# like Redis, with TTL, etc ... 
def image_upload(func):
    def wrapper(*args):
        if request.method == 'POST':
            if ok_file(request):
                fil = request.files['image']

                # Get a unique identifier based on the file content before we
                # try and save the binary and convert to ascii. This identifier
                # is the key used for the file-based cache that follows.

                # A large file was uploaded, use only part to generate key
                if type(fil.stream) is file:
                    key = file_id(secure_filename(fil.filename) + fil.stream.read(16384))
                    # Reset file pointer or trying to do fil.save() will error
                    fil.stream.seek(0,0)
                else:
                    key = file_id(fil.stream.getvalue())

                # Check cache for ascii version, otherwise generate from source
                # image and cache it.
                content = cache.cache(key, fil)
                resp = Response(content, mimetype='text/text')
                return resp

            flash('Must upload a file of the appropriate type and name!')
            return redirect(request.url)
        return func(*args)
    return wrapper

def ok_file(request):
    return request.files \
        and request.files['image'] \
        and ('.' in request.files['image'].filename) \
        and (request.files['image'].filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)

def file_id(contents):
    m = md5.new()
    m.update(contents)
    return m.hexdigest()

###############################################################################
# Routes
###############################################################################

@app.route('/', methods=['GET', 'POST'])
@image_upload
def upload_file():
    return render_template('index.html',
        allowed_extensions = '.' + ', .'.join(ALLOWED_EXTENSIONS))


# Dev mode
if __name__ == '__main__':
    app.run(debug = True)
