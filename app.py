from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from flaskext.markdown import Markdown
import sqlite3
import os

app = Flask(__name__)
Markdown(app)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



def init_db():
    conn = sqlite3.connect("blog.db")
    conn.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,content TEXT NOT NULL, image TEXT)')
    conn.close()
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
@app.route("/")
def home():
    conn = sqlite3.connect('blog.db')
    posts = conn.execute('SELECT id, title, content FROM posts').fetchall()
    conn.close()
    previews = [(p[0], p[1], p[2][:100] + "....") for p in posts]
    return render_template('home.html', posts=previews)

@app.route('/post/<int:post_id>')
def blog_details(post_id):
    
    conn = sqlite3.connect('blog.db')
    post = conn.execute('SELECT * FROM posts where id = ?', (post_id,)).fetchone()
    conn.close()
    return render_template('blog_detail.html', post=post)

@app.route('/add', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image_filename = None
        
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename):
                image_filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        conn = sqlite3.connect('blog.db')
        conn.execute('INSERT INTO posts (title, content, image) VALUES (?, ?, ?)', (title, content, image_filename))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    return render_template('add_post.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
    