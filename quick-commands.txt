# Initiate and enter dev environment, ensure you are in the top level directory for this repo
.\initenv.ps1

# Clone the repository
git clone https://github.com/Itstherealmeokay/CSIT-314-Capybara.git

# Run the server
python manage.py runserver

# Update SQL if you made any model changes
python manage.py makemigrations; python manage.py migrate