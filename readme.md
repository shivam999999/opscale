#install pipenv for reunning in virtual environment
pip install --user pipenv
#install requirement.txt
pip install -r requirements.txt
#run celery in backgroung
celery -A celery_example.celery worker loglevel=info
#run python api.py
