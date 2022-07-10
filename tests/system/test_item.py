from models.store import StoreModel
from models.user import UserModel
from models.item import ItemModel
from tests.base_test import BaseTest
import json


class ItemTest(BaseTest):
    def setUp(self):
        super(ItemTest, self).setUp()
        with self.app() as client:
            with self.app_context():
                client.post('/register', json={'username': 'test', 'password': '1234'})
                auth_request = client.post('/auth',
                                           data=json.dumps({'username': 'test', 'password': '1234'}),
                                           headers={'Content-Type': 'application/json'})
                auth_token = json.loads(auth_request.data)['access_token']
                self.access_token = f'JWT {auth_token}'

    def test_get_item_no_auth(self):
        with self.app() as client:
            with self.app_context():
                resp = client.get('/item/test')
                self.assertEqual(resp.status_code, 401)

    def test_get_item_not_found(self):
        with self.app() as client:
            with self.app_context():
                resp = client.get('/item/test', headers={'Authorization': self.access_token})
                self.assertEqual(resp.status_code, 404)

    def test_get_item(self):
        with self.app() as client:
            with self.app_context():
                client.post('/store/test')
                ItemModel('test', 1.1, 1).save_to_db()
                resp = client.get('/item/test', headers={'Authorization': self.access_token})
                self.assertEqual(resp.status_code, 200)

    def test_delete_item(self):
        with self.app() as client:
            with self.app_context():
                client.post('/store/test')
                ItemModel('test', 1.1, 1)

                resp = client.delete('/item/test')
                self.assertEqual(resp.status_code, 200)
                self.assertDictEqual({'message': 'Item deleted'},
                                     json.loads(resp.data))

    def test_create_item(self):
        with self.app() as client:
            with self.app_context():
                client.post('/store/test')
                resp = client.post('/item/test', json={'price': 1.1, 'store_id': 1})

                self.assertEqual(resp.status_code, 201)
                self.assertDictEqual({'name': 'test', 'price': 1.1},
                                     json.loads(resp.data))

    def test_create_dublicate_item(self):
        with self.app() as client:
            with self.app_context():
                client.post('/store/test')
                client.post('/item/test', json={'price': 1.1, 'store_id': 1})

                resp = client.post('/item/test', json={'price': 1.1, 'store_id': 1})

                self.assertEqual(resp.status_code, 400)
                self.assertDictEqual({'message': 'An item with name \'test\' already exists.'},
                                     json.loads(resp.data))

    def test_put_item(self):
        with self.app() as client:
            with self.app_context():
                client.post('/store/test')

                resp = client.put('/item/test', json={'price': 1.1, 'store_id': 1})

                self.assertEqual(resp.status_code, 200)
                self.assertEqual(ItemModel.find_by_name('test').price, 1.1)
                self.assertDictEqual({'name': 'test', 'price': 1.1},
                                     json.loads(resp.data))

    def test_put_update_item(self):
        with self.app() as client:
            with self.app_context():
                client.post('/store/test')
                ItemModel('test', 100, 1).save_to_db()

                self.assertEqual(ItemModel.find_by_name('test').price, 100)

                resp = client.put('/item/test', json={'price': 1.1, 'store_id': 1})

                self.assertEqual(resp.status_code, 200)
                self.assertEqual(ItemModel.find_by_name('test').price, 1.1)
                self.assertDictEqual({'name': 'test', 'price': 1.1},
                                     json.loads(resp.data))

    def test_item_list(self):
        with self.app() as client:
            with self.app_context():
                client.post('/store/test')
                client.post('/item/test', json={'price': 1.1, 'store_id': 1})

                resp = client.get('/items')

                self.assertDictEqual({'items': [{'name': 'test', 'price': 1.1}]},
                                     json.loads(resp.data))

