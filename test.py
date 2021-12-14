from main import app
import unittest


# set up mock secret key for tests
def setUp(self):
    app.config['SECRET_KEY'] = 'sekrit!'
    self.app = app.app.test_client()


class FlaskTestCase(unittest.TestCase):

    # ensure flask is set up properly
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/index', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # test that the login page loads
    def test_login_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # test that the profile page loads
    def test_profile_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/profile', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # test getting a single product if a product is there
    def test_product(self):
        tester = app.test_client(self)
        response = tester.get('/product/1', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # test getting a single product if no product is there
    def test_no_product(self):
        tester = app.test_client(self)
        response = tester.get('/product/', content_type='html/text')
        self.assertEqual(response.status_code, 404)

    # testing add a product to the cart
    def test_add_to_cart(self):
        tester = app.test_client(self)
        response = tester.get('/cart/5', content_type='html/text')
        self.assertEqual(response.status_code, 302)

    # test cart creates a session
    def test_cart_session(self):
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['cart'] = []
            response = c.get('/index')
            self.assertEqual(response.status_code, 200)

    # test order page loads
    def test_order_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/order', content_type='html/text')
        self.assertEqual(response.status_code, 302)

    # test new product page loads
    def test_newproduct_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/newproduct', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # test delete product function works
    def test_delete_product(self):
        tester = app.test_client(self)
        response = tester.get('/deleteproduct/1', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # testing delete order function works
    def test_order_product(self):
        tester = app.test_client(self)
        response = tester.get('/deleteorder/1', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # testing edit product function works
    def test_edit_product(self):
        tester = app.test_client(self)
        response = tester.get('/editproduct/1', content_type='html/text')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
