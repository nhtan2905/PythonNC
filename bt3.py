from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Thông tin kết nối cơ sở dữ liệu PostgreSQL
DB_CONFIG = {
    "dbname": "QuanLySach",
    "user": "postgres",
    "password": "2111",
    "host": "localhost",
    "port": "5432"
}

# Kết nối cơ sở dữ liệu
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("Kết nối cơ sở dữ liệu thành công!")
except Exception as e:
    print(f"Lỗi khi kết nối cơ sở dữ liệu: {e}")

# Decorator kiểm tra trạng thái đăng nhập
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Vui lòng đăng nhập trước!", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Trang chủ (yêu cầu đăng nhập)

@app.route('/')
def index():
    return render_template('index.html')  # Một trang giới thiệu chung


# Trang đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not (username and password and confirm_password):
            flash("Vui lòng điền đầy đủ thông tin!", "danger")
            return redirect(url_for('register'))

        if password != confirm_password:
            flash("Mật khẩu không khớp!", "danger")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            flash("Đăng ký thành công! Hãy đăng nhập.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Lỗi khi đăng ký: {e}", "danger")
            return redirect(url_for('register'))

    return render_template('register.html')

#Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Lấy thông tin tài khoản từ cơ sở dữ liệu
        cursor.execute("SELECT id, username, password, role FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[2], password):
            # Lưu thông tin vào session
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]

            flash(f"Đăng nhập thành công! Chào mừng {user[1]}.", "success")

            # Chuyển hướng dựa trên vai trò
            if user[3] == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('user'))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng.", "danger")

    return render_template('login.html')

# Trang dành cho user
@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    if session.get('role') != 'user':
        flash("Bạn không có quyền truy cập trang này!", "danger")
        return redirect(url_for('login'))

    # Xử lý đóng góp ý kiến
    if request.method == 'POST':
        feedback = request.form.get('feedback')
        if feedback:
            try:
                cursor.execute("INSERT INTO feedback (user_id, content) VALUES (%s, %s)", (session['user_id'], feedback))
                conn.commit()
                flash("Cảm ơn bạn đã đóng góp ý kiến!", "success")
            except Exception as e:
                flash(f"Lỗi khi gửi ý kiến: {e}", "danger")

    # Xử lý tìm kiếm sách
    search = request.args.get('search')
    if search:
        cursor.execute("SELECT id, title, author, genre, publish_date, quantity FROM books WHERE title ILIKE %s OR author ILIKE %s", 
                       (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("SELECT id, title, author, genre, publish_date, quantity FROM books")

    books = cursor.fetchall()
    return render_template('user.html', books=books)



# Đăng xuất
@app.route('/logout')
def logout():
    session.clear()
    flash("Bạn đã đăng xuất.", "info")
    return redirect(url_for('login'))

# Thêm sách (chỉ dành cho admin)
@app.route('/add', methods=['POST'])
@login_required
def add_book():
    if session.get('role') != 'admin':
        flash("Bạn không có quyền thực hiện hành động này!", "danger")
        return redirect(url_for('index'))

    title = request.form['title']
    author = request.form['author']
    genre = request.form['genre']
    publish_date = request.form['publish_date']
    quantity = request.form['quantity']

    if not (title and author and genre and publish_date and quantity):
        flash("Vui lòng nhập đầy đủ thông tin!", "danger")
        return redirect(url_for('index'))

    try:
        cursor.execute(
            "INSERT INTO books (title, author, genre, publish_date, quantity) VALUES (%s, %s, %s, %s, %s)",
            (title, author, genre, publish_date, int(quantity))
        )
        conn.commit()
        flash("Thêm sách thành công!", "success")
    except Exception as e:
        flash(f"Lỗi khi thêm sách: {e}", "danger")
    return redirect(url_for('index'))

# Xóa sách (chỉ dành cho admin)
@app.route('/delete/<int:book_id>')
@login_required
def delete_book(book_id):
    if session.get('role') != 'admin':
        flash("Bạn không có quyền thực hiện hành động này!", "danger")
        return redirect(url_for('index'))

    try:
        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        conn.commit()
        flash("Xóa sách thành công!", "success")
    except Exception as e:
        flash(f"Lỗi khi xóa sách: {e}", "danger")
    return redirect(url_for('index'))
# Trang admin (chỉ dành cho admin)
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if session.get('role') != 'admin':
        flash("Bạn không có quyền truy cập trang này!", "danger")
        return redirect(url_for('login'))

    # Xử lý thêm sách
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        publish_date = request.form['publish_date']
        quantity = request.form['quantity']

        if not (title and author and genre and publish_date and quantity):
            flash("Vui lòng nhập đầy đủ thông tin!", "danger")
        else:
            try:
                cursor.execute(
                    "INSERT INTO books (title, author, genre, publish_date, quantity) VALUES (%s, %s, %s, %s, %s)",
                    (title, author, genre, publish_date, int(quantity))
                )
                conn.commit()
                flash("Thêm sách thành công!", "success")
            except Exception as e:
                flash(f"Lỗi khi thêm sách: {e}", "danger")

    # Lấy danh sách sách
    cursor.execute("SELECT id, title, author, genre, publish_date, quantity FROM books")
    books = cursor.fetchall()

    # Lấy danh sách phản hồi
    cursor.execute("SELECT id, user_id, content, created_at FROM feedback")
    feedbacks = cursor.fetchall()

    return render_template('admin.html', books=books, feedbacks=feedbacks)


    # Xử lý tìm kiếm
    search = request.args.get('search')
    if search:
        cursor.execute("SELECT id, title, author, genre, publish_date, quantity FROM books WHERE title ILIKE %s OR author ILIKE %s", 
                       (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("SELECT id, title, author, genre, publish_date, quantity FROM books")
    
    books = cursor.fetchall()
    return render_template('admin.html', books=books)
# Trang sửa sách
@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if 'role' not in session or session['role'] != 'admin':
        flash("Bạn cần đăng nhập với quyền admin để truy cập trang này!", "danger")
        return redirect(url_for('login'))

    # Lấy thông tin sách
    if request.method == 'GET':
        cursor.execute("SELECT id, title, author, genre, publish_date, quantity FROM books WHERE id = %s", (book_id,))
        book = cursor.fetchone()
        if not book:
            flash("Không tìm thấy sách!", "danger")
            return redirect(url_for('admin'))
        return render_template('edit_book.html', book=book)

    # Cập nhật thông tin sách
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        publish_date = request.form['publish_date']
        quantity = request.form['quantity']

        if not (title and author and genre and publish_date and quantity):
            flash("Vui lòng nhập đầy đủ thông tin!", "danger")
        else:
            try:
                cursor.execute(
                    "UPDATE books SET title = %s, author = %s, genre = %s, publish_date = %s, quantity = %s WHERE id = %s",
                    (title, author, genre, publish_date, int(quantity), book_id)
                )
                conn.commit()
                flash("Cập nhật sách thành công!", "success")
                return redirect(url_for('admin'))
            except Exception as e:
                flash(f"Lỗi khi cập nhật sách: {e}", "danger")
        return redirect(url_for('edit_book', book_id=book_id))
@app.route('/admin/users', methods=['GET'])
@login_required
def manage_users():
    if session.get('role') != 'admin':
        flash("Bạn không có quyền truy cập trang này!", "danger")
        return redirect(url_for('login'))

    # Lấy danh sách tất cả user
    try:
        cursor.execute("SELECT id, username, role FROM users")
        users = cursor.fetchall()
        return render_template('manage_users.html', users=users)
    except Exception as e:
        flash(f"Lỗi khi lấy danh sách tài khoản: {e}", "danger")
        return redirect(url_for('admin'))
 #Xóa tài khoản user       
@app.route('/admin/users/delete/<int:user_id>', methods=['GET'])
@login_required
def delete_user(user_id):
    if session.get('role') != 'admin':
        flash("Bạn không có quyền thực hiện hành động này!", "danger")
        return redirect(url_for('login'))

    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        flash("Xóa tài khoản thành công!", "success")
    except Exception as e:
        flash(f"Lỗi khi xóa tài khoản: {e}", "danger")

    return redirect(url_for('manage_users'))
#Sửa tài khoản user
@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if session.get('role') != 'admin':
        flash("Bạn không có quyền thực hiện hành động này!", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']

        if not (username and role):
            flash("Vui lòng nhập đầy đủ thông tin!", "danger")
            return redirect(url_for('edit_user', user_id=user_id))

        try:
            cursor.execute("UPDATE users SET username = %s, role = %s WHERE id = %s", (username, role, user_id))
            conn.commit()
            flash("Cập nhật tài khoản thành công!", "success")
            return redirect(url_for('manage_users'))
        except Exception as e:
            flash(f"Lỗi khi cập nhật tài khoản: {e}", "danger")

    # Lấy thông tin user
    cursor.execute("SELECT id, username, role FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        flash("Không tìm thấy tài khoản!", "danger")
        return redirect(url_for('manage_users'))

    return render_template('edit_user.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
