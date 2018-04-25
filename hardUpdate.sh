rm -rf unAventonApp/migrations/00*.py
rm -rf db.sqlite3
./manage.py makemigrations --no-input
./manage.py migrate --no-input
