# LXCloud Database Configuration
# Copy this file to .env or set these environment variables

# Database host (default: localhost)
export DB_HOST=localhost

# Database user (default: lxcloud)
export DB_USER=lxcloud

# Database password (default: lxcloud123)
export DB_PASS=lxcloud123

# Database name (default: lxcloud)
export DB_NAME=lxcloud

# Example for different database setups:

# MariaDB with custom credentials:
# export DB_HOST=localhost
# export DB_USER=myuser
# export DB_PASS=mypassword
# export DB_NAME=myapp

# Remote MySQL database:
# export DB_HOST=mysql.example.com
# export DB_USER=remote_user
# export DB_PASS=remote_password
# export DB_NAME=lxcloud_prod

# To use this file, run:
# source /path/to/this/file
# python3 app.py