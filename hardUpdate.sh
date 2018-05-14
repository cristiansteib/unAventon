rm -rf unAventonApp/migrations/00*.py
rm -rf db.sqlite3
pip install -r requirements.txt
./manage.py makemigrations --no-input
./manage.py migrate --no-input
echo "now create super user"
#./manage.py createsuperuser --username admin --email a@a.com
