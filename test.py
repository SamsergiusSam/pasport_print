from werkzeug.security import generate_password_hash
result = generate_password_hash('12345')
print(result)
