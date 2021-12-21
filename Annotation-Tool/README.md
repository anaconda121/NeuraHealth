[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![forthebadge](https://forthebadge.com/images/badges/uses-html.svg)]()
[![forthebadge](https://forthebadge.com/images/badges/uses-css.svg)]()
[![forthebadge](https://forthebadge.com/images/badges/uses-js.svg)]()
[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)]()

# NLP Annotator Tool
The NLP Annotator Tool is a clinical annotation tool designed to facilitate rapid and thorough labelling of clinical notes.

# Setup
1. Install [Python 3.7](https://www.python.org/) and [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/index.html)
2. Clone this repository
3. In the repository root (where `Pipfile` is located): run `pipenv install --dev`
4. Make a copy of `.env.example` named `.env`

# Usage

To activate your virtual environment, in the repository root run `pipenv shell`.

To start the server, in the `annotator_gui` directory run `python manage.py runserver`.

To add new data, first update the `.csv` files in the `load_data/data` directory. Then:
```python
python manage.py shell
> %run load_data/load_data.py
```
At this time, it is advisable to delete all existing data in the database before replacing with new data. Duplicate records (by `PatientID`) will not be updated. 

To delete all data in the database:
```python
python manage.py shell
> from gui.models import PatientDemographic, PatientYear, Note
> PatientDemographic.objects.all().delete()
> PatientYear.objects.all().delete()
> Note.objects.all().delete()
```

# Adding Dependencies (Packages)

To add a package required by the application, run `pipenv install <package-name>`

To add a package only needed for local development, run `pipenv install --dev <package-name>`

# Team
The NLP Annotator Tool was developed by the [MIND Data Science Lab](https://www.massgeneral.org/neurology/research/mind-data-science-lab) at Massachusetts General Hospital.