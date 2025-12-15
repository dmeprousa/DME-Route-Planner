"""
Password Hash Generator for DME Route Planner
Run this script to generate password hashes for .env file
"""

import hashlib

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

print("=" * 60)
print("PASSWORD HASH GENERATOR")
print("=" * 60)
print()
print("Enter passwords for each user:")
print()

# Get passwords
sofia_pass = input("Sofia's password: ")
cyrus_pass = input("Cyrus's password: ")
admin_pass = input("Admin's password: ")

# Generate hashes
sofia_hash = hash_password(sofia_pass)
cyrus_hash = hash_password(cyrus_pass)
admin_hash = hash_password(admin_pass)

print()
print("=" * 60)
print("ADD THESE LINES TO YOUR .env FILE:")
print("=" * 60)
print()
print(f"PASSWORD_SOFIA={sofia_hash}")
print(f"PASSWORD_CYRUS={cyrus_hash}")
print(f"PASSWORD_ADMIN={admin_hash}")
print()
print("=" * 60)
print("✅ Done! Copy these lines to your .env file")
print("=" * 60)
