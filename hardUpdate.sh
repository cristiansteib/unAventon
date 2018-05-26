rm -rf unAventonApp/migrations/00*.py
rm -rf db.sqlite3
pip install -r requirements.txt
sudo chgrp -R www-data media/
./manage.py makemigrations --no-input
./manage.py migrate --no-input
echo "Choose password for admin user"
./manage.py createsuperuser --username admin --email admin@admin.com
