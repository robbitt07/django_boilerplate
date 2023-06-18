echo Starting Build, output logged to logs/build.log
mkdir -p logs
exec 1> logs/build.log 2>&1

echo Drop and create database
python build/scripts/drop_create_database.py

echo Run public migrations
python manage.py migrate

echo Remove and rebuild CDN folder
rm -r -f ../static-cdn-local
python manage.py collectstatic --noinput

echo Create User
python build/scripts/create_user.py

echo All Complete!
