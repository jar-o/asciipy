import os
import base64
import asciigen

class AsciiCache(object):
    """ Cache is file based. Using a uniquely generated "key" we create a
    file with that name in the CACHE_FOLDER. """

    def __init__(self, path):
        self.path = path

    def cache(self, key, fil):
        key = base64.urlsafe_b64encode(key) # Make key filename safe
        cache_key = os.path.join(self.path, key)
        if os.path.exists(cache_key):
            with open(cache_key, 'r') as f:
                content = f.read()
        else:
            fpath = os.path.join(self.path, 'temp.' + key)
            fil.save(fpath)
            content = asciigen.from_filename(fpath, width=150)
            os.remove(fpath)
            with open(cache_key, 'w') as f:
                f.write(content)
        return content

    # TODO unused, probably should be part of a scheduled task
    def cache_purge(self, path, days):
        for f in os.listdir(path):
            if os.stat(os.path.join(path,f)).st_mtime < (time.time() - (days * 86400)):
                os.remove(f)
