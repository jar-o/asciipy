import os
import app
import unittest

cache_folder = 'cache'

class AppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.app.test_client()

    def tearDown(self):
        folder = cache_folder
        for f in os.listdir(folder):
            fp = os.path.join(folder, f)
            if os.path.isfile(fp): os.unlink(fp)

    def test_basic(self):
        assert '<h1>Upload image to ASCIIfy</h1>' in self.app.get('/').data

    def test_bad_image(self):
        assert 'Redirecting...' in self.app.post('/', data = { 'image': 'wut' }).data
        assert 'Must upload a file of the appropriate type and name!' in self.app.get('/').data

    def test_upload(self):
        with open('test-images/batman.jpeg', 'rb') as f:
            resp = self.app.post('/', data={ 'image': f }).data
        cache_file = os.path.join(cache_folder, 'NmNjZGY4NTM2YzkwNDZlMjk0Njc5MWEwNjhiYzkyNWU=')
        # Make sure it's actually text
        assert '^mlajF1&&&&&&&&&&&sjlf22444224PW' in resp
        assert os.path.exists(cache_file)
        with open(cache_file, 'rb') as f:
            content = f.read()
            assert resp == content # response == cache data

if __name__ == '__main__':
    unittest.main()
