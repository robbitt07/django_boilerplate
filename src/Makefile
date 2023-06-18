server:
	python manage.py runserver

static:
	python manage.py collectstatic --no-input

db-build:
	build\build_local.bat

db-build-unix:
	sh build/build_local.sh

clear-cache:
	python manage.py clearcache

clear-obj-cache:
	python manage.py clear_cache_keys key=cached_obj:*

sass-build:
	sass --style=expanded staticfiles/sass/style.scss:staticfiles/css/style.css && sass --style=expanded staticfiles/sass/style.scss:app/src/assets/css/style.css

sass-listen:
	sass --style=expanded --watch staticfiles/sass/style.scss staticfiles/css/style.css 
	
sass-react-listen:
	sass --style=expanded --watch staticfiles/sass/style.scss:app/src/assets/css/style.css