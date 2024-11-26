from werkzeug.security import generate_password_hash

password = "123456"  # Mật khẩu mới
hashed_password = generate_password_hash(password)
print("Mật khẩu băm:", hashed_password)
