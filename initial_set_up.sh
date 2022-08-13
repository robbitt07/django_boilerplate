pip3 install virtualenv
rm -r -f venv
python3 -m venv venv
source venv\Scripts\activate
python3 -m pip install --upgrade pip
pip3 install -r requirements/requirements.txt
git rm -rf .git
git init
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"