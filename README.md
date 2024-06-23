# Django Boilerplate Template

Quick start Django 4.2 project template.

# Usage

```bash
git clone https://github.com/robbitt07/django_boilerplate
```

Replace `yabpt` in `.gitignore` and the two folders `/yabpt/` and `/yabpt/yabpt/` with the project name.

Add .env file with following format.
```
SECRET_KEY=

DEBUG=True
ALLOWED_HOSTS=127.0.0.1

DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

Run the initial set up, including creating the virtual enviroment and secret key.
```bash
initial_set_up.bat
```

Take response from secret key output on last command and paste the key following the `SECRET_KEY` enviroment variable in the `.env` file.

You are off to the races!