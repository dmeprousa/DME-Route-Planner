#!/bin/bash
# Setup script for host - updates .env with password hashes

echo "🔧 Setting up password authentication on host..."

# Function to hash passwords
hash_password() {
    echo -n "$1" | sha256sum | cut -d' ' -f1
}

# Generate hashes
SOFIA_HASH=$(hash_password "123456Ss")
CYRUS_HASH=$(hash_password "123456Cc")
ADMIN_HASH=$(hash_password "1234567Hh")

# Remove old password entries if they exist
sed -i '/^PASSWORD_/d' .env 2>/dev/null || true
sed -i '/# User Password Hashes/d' .env 2>/dev/null || true

# Add new password hashes
cat >> .env << EOF

# User Password Hashes (SHA256)
PASSWORD_SOFIA=${SOFIA_HASH}
PASSWORD_CYRUS=${CYRUS_HASH}
PASSWORD_ADMIN=${ADMIN_HASH}
EOF

echo "✅ Password hashes added to .env file!"
echo ""
echo "📝 Passwords:"
echo "  - Sofia: 123456Ss"
echo "  - Cyrus: 123456Cc"
echo "  - Admin: 1234567Hh"
echo ""
echo "🔄 Please restart Streamlit for changes to take effect"
