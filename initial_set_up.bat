call pip install virtualenv
rmdir venv /S /Q
call python -m venv venv
call venv\Scripts\activate
call python -m pip install --upgrade pip
call pip install -r requirements/requirements.txt
git rm -rf .git
git init
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"