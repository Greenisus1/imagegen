import base64, json, os, tempfile, threading, unittest, urllib.request
import imagegen

PNG_1PX = base64.b64encode(bytes.fromhex(
    '89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489'
    '0000000d49444154789c626001000000ffff03000006000557bfabd40000000049454e44ae426082')).decode()

class SaveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
    def tearDown(self):
        self.tmp.cleanup()
    def test_save_writes_png(self):
        path = imagegen.save_image('A red ROBOT!', PNG_1PX, self.tmp.name)
        self.assertTrue(os.path.isfile(path))
        self.assertIn('a-red-robot', path)
        with open(path, 'rb') as fh:
            self.assertEqual(fh.read(4), b'\x89PNG')
    def test_rejects_non_png(self):
        with self.assertRaises(ValueError):
            imagegen.save_image('x', base64.b64encode(b'GIF89a....').decode(), self.tmp.name)
    def test_rejects_bad_base64(self):
        with self.assertRaises(Exception):
            imagegen.save_image('x', '!!!notb64!!!', self.tmp.name)
    def test_safe_name(self):
        self.assertEqual(imagegen.safe_name('Hello, World! 42'), 'hello-world-42')
        self.assertEqual(imagegen.safe_name('...'), 'image')
        self.assertEqual(imagegen.safe_name('../../etc/passwd'), 'etc-passwd')

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        imagegen.IMAGE_DIR = cls.tmp.name
        cls.port = imagegen.free_port()
        from http.server import ThreadingHTTPServer
        cls.server = ThreadingHTTPServer(('127.0.0.1', cls.port), imagegen.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.tmp.cleanup()
    def url(self, p): return 'http://127.0.0.1:%d%s' % (self.port, p)
    def test_index_serves_page(self):
        with urllib.request.urlopen(self.url('/')) as r:
            body = r.read().decode()
        self.assertIn('js.puter.com', body)
        self.assertIn('txt2img', body)
        self.assertNotIn('api_key', body.lower())
    def test_index_has_signin_flow(self):
        with urllib.request.urlopen(self.url('/')) as r:
            body = r.read().decode()
        self.assertIn('puter.auth.signIn', body)
        self.assertIn('isSignedIn', body)
        self.assertIn('Sign in with Puter', body)
        self.assertIn('free Puter account', body)
    def test_save_and_list_and_fetch(self):
        req = urllib.request.Request(self.url('/save'), method='POST',
            data=json.dumps({'prompt': 'moon cat', 'data': PNG_1PX}).encode(),
            headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as r:
            saved = json.loads(r.read())['saved']
        self.assertTrue(saved.endswith('.png'))
        with urllib.request.urlopen(self.url('/images')) as r:
            self.assertIn(saved, json.loads(r.read())['images'])
        with urllib.request.urlopen(self.url('/images/' + saved)) as r:
            self.assertEqual(r.headers['Content-Type'], 'image/png')
    def test_save_rejects_bad(self):
        req = urllib.request.Request(self.url('/save'), method='POST',
            data=json.dumps({'prompt': 'x', 'data': 'not-image'}).encode(),
            headers={'Content-Type': 'application/json'})
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 400)
    def test_traversal_blocked(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(self.url('/images/..%2F..%2Fetc%2Fpasswd'))
        self.assertIn(ctx.exception.code, (400, 404))

if __name__ == '__main__':
    unittest.main()
