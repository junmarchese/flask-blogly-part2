import unittest
from app import app, db
from models import User, Post

class BloglyTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a test client and sample data."""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'

        with self.app.app_context():
            db.create_all()

            # Add individual users
            self.user1 = User(first_name="Test", last_name="User", image_url="https://via.placeholder.com/150")
            self.user2 = User(first_name="Another", last_name="User", image_url="https://via.placeholder.com/150")
            db.session.add(self.user1)
            db.session.add(self.user2)
            db.session.commit()

            # Add a post
            self.post1 = Post(title="Test Post", content="Test Content", user_id=self.user1.id)
            db.session.add(self.post1)
            db.session.commit()

            #Re-query the instances to attach them to the current session
            self.user1 = User.query.get(self.user1.id)
            self.user2 = User.query.get(self.user2.id)
            self.post1 = User.query.get(self.post1.id)

        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_list_users(self):
        """Test the /users route."""
        with self.client as c:
            response = c.get('/users')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test User', response.data)
            self.assertIn(b'Another User', response.data)

    def test_show_user(self):
        """Test the /users/<int:user_id> route."""
        with self.client as c:
            with self.app.app_context():
                self.user1 = User.query.get(self.user1.id)
            # Test for first user
            response = c.get(f'/users/{self.user1.id}')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test User', response.data)

            # Test for second user
            response = c.get(f'/users/{self.user2.id}')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Another User', response.data)

    def test_add_user(self):
        """Test the /users/new route."""
        with self.client as c:
            response = c.post('/users/new', data={
                "first_name": "New",
                "last_name": "User",
                "image_url": "https://via.placeholder.com/150"
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'New User', response.data)

    def test_delete_user(self):
        """Test the /users/<int:user_id>/delete route."""
        with self.client as c, self.app.app_context():
            user = User.query.get(self.user1.id)
            # Delete first user
            response = c.post(f'/users/{user.id}/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            # Check user has been deleted and name is not in the response
            self.assertNotIn(b'Test User', response.data)

            # Ensure the user is deleted from the database
            self.assertIsNone(User.query.get(user.id))

            # Check if second user is still present
            response = c.get('/users')
            self.assertIn(b'Another User', response.data)

    def test_add_post(self):
        """Test the /users/<int:user_id>/posts/new route."""
        with self.client as c:
            with self.app.app_context():
                self.user1 = User.query.get(self.user1.id)

            response = c.post(f'/users/{self.user1.id}/posts/new', data={
                "title": "New Post",
                "content": "New Post Content"
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'New Post', response.data)

    def test_show_post(self):
        """Test the /posts/<int:post_id> route."""
        with self.client as c:
            with self.app.app_context():
                self.post1 = Post.query.get(self.post1.id)

            response = c.get(f'/posts/{self.post1.id}')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test Post', response.data)
            self.assertIn(b'Test Content', response.data)

    def test_edit_post(self):
        """Test the /posts/<int:post_id>/edit route."""
        with self.client as c:
            with self.app.app_context():
                self.post1 = Post.query.get(self.post1.id)

            response = c.post(f'/posts/{self.post1.id}/edit', data={
                "title": "Updated Post",
                "content": "Updated Content"
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Updated Post', response.data)
            self.assertIn(b'Updated Content', response.data)

    def test_delete_post(self):
        """Test the /posts/<int:post_id>/delete route."""
        with self.client as c:
            with self.app.app_context():
                self.post1 = Post.query.get(self.post1.id)

            response = c.post(f'/posts/{self.post1.id}/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn(b'Test Post', response.data)

            # Ensure the post is deleted from the database
            with self.app.app_context():
                self.assertIsNone(Post.query.get(self.post1.id))


if __name__ == '__main__':
    unittest.main()

    # def test_show_post(self):
    #     """Test the /posts/<int:post_id> route."""
    #     with self.client as c:
    #         response = c.get('/posts/1')
    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn(b'First Post', response.data)

    # def test_add_post(self):
    #     """Test the /post/<int:post_id>/new route."""
    #     with self.client as c:
    #         user = User.query.first()
    #         response = c.post(f'/users/{user.id}/posts/new', data={
    #              "title"="Test Post",
    #              "content"="This is a test post."
    #         }, follow_redirects=True)
    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn(b'Test Post', response.data)

    # def test_edit_post(self):
    #     """Test the /post/<int:post_id>edit route."""
    #     with self.client as c:
    #         user = User.query.first()
    #         post = Post(title='Test Post', content='This is a test post.', user_id=user.id)
    #         db.session.add(post)
    #         db.session.commit()

    #         response = c.post(f'/posts/{post.id}/edit', data=dict(
    #             title='Updated Post',
    #             content='This is an updated test post.'
    #         ), follow_redirects=True)
    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn(b'Updated Post', response.data)

    # def test_delete_post(self):
    #     with self.client as c:
    #         user = User.query.first()
    #         post = Post(title='Test Post', content='This is a test post.', user_id=user.id)
    #         db.session.add(post)
    #         db.session.commit()

    #         response = c.post(f'/posts/{post.id}/delete', follow_redirects=True)
    #         self.assertEqual(response.status_code, 200)
    #         self.assertNotIn(b'Test Post', response.data)



