import bcrypt

# example password
password = input("Enter your password: ")

# converting password to array of bytes
pw_bytes = password.encode('utf-8')

# generating the salt
salt = bcrypt.gensalt()

# Hashing the password
pw_hash = bcrypt.hashpw(pw_bytes, salt)

print(pw_hash)
