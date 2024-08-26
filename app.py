"""Blogly application."""

from flask import Flask, redirect, render_template, request, url_for
from models import db, connect_db, User, Post

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True

    connect_db(app)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

# call this only if/when testing app
# app = create_app(test_config=True)

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/')
def home():
    """Redirect to list of users."""
    return redirect(url_for('list_users'))

@app.route('/users')
def list_users():
    """List all users."""
    users = User.query.all()
    return render_template('users_list.html', users=users)

@app.route('/users/new', methods=["GET", "POST"])
def add_user():
    """Add a new user."""
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        image_url = request.form['image_url']

        new_user = User(first_name=first_name, last_name=last_name, image_url=image_url)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('list_users'))
    
    return render_template('new_user.html')

@app.route('/users/<int:user_id>')
def show_user(user_id):
    """Show information about the given user."""
    user = User.query.get_or_404(user_id)
    return render_template('user_detail.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=["GET", "POST"])
def edit_user(user_id):
    """Show edit page for a user and allow existing user to make edits."""
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.image_url = request.form['image_url']

        db.session.commit()
        return redirect(url_for('show_user', user_id=user.id))
    
    return render_template('edit_user.html', user=user)

@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    """Delete the user."""
    user = User.query.get_or_404(user_id)

    Post.query.filter_by(user_id=user.id).delete()

    # posts = Post.query.filter_by(user_id=user.id).all()
    # for post in posts:
    #     post.user_id = None

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('list_users'))


@app.route('/users/<int:user_id>/posts/new', methods=["GET", "POST"])
def add_post(user_id):
    """Show form to add a post for that user and handle form submission."""
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']

        new_post = Post(title=title, content=content, user_id = user.id)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('show_user', user_id=user.id))
    
    return render_template('new_post.html', user=user)


@app.route('/posts/<int:post_id>')
def show_post(post_id):
    """Show a single post."""
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

@app.route('/posts/<int:post_id>/edit', methods=["GET", "POST"])
def edit_post(post_id):
    """Show form to edit a post, cancel back to user page, and handle edit submission"""
    post = Post.query.get_or_404(post_id)

    if request.method == "POST":
        post.title = request.form['title']
        post.content = request.form['content']

        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))
    
    return render_template('edit_post.html', post=post)

@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def delete_post(post_id):
    """Delete a post."""
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('show_user', user_id=post.user_id))



