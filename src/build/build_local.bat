echo Starting Build

echo Drop and create database
python build/scripts/drop_create_database.py

echo Run public migrations
python manage.py migrate

echo Remove and rebuild CDN folder
rmdir /S /Q ../static-cdn-local
python manage.py collectstatic --noinput

echo Create User
python build/scripts/create_user.py

echo All Complete!
