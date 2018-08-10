# djmsgparser (Django .MSG Parser)
A Django Pluggable Web App Which Parses Outlook's .MSG File. This will be useful for non-Windows users (like me)
when the only requirement is to see the .msg file content without uploading to 3rd-party non-secured web sites.

## Installation & Deployment Guide -

### 1. Install global dependencies

     sudo apt-get install virtualenv python-pip git

### 2. Upgrade `pip` and `setuptools` that are bundled with the OS to the latest stable versions.

     sudo -H pip install pip -U

     sudo -H pip install setuptools -U

### 3. Clone the djmsgparser from github to your preferred directory.

    git clone https://github.com/sauravmahuri2007/djmsgparser.git

    cd djmsgparser

### 4. Create virtualenv and install project dependencies

    virtualenv --python=python3 venv

    source venv/bin/activate

    pip install -r requirements.txt

### 5. Create `uploads` directory where the .msg files will be temporary uploaded for parsing

    mkdir uploads

### 6. Run the app using the default lightweight Django web server (until this app is not part of a big application)

    python manage.py runserver

## Or, Install and Run the App using `install` script (Only for Ubuntu) -

    ./install


The app should have started running at http://127.0.0.1:8000.
To start the djmsgparser application at any time below command can be executed in terminal:

    djmsgparser # run in default address or,
    djmsgparser 127.0.0.1:8008  # to run the app in any specific ip and port

Execute below command to uninstall the application:

    ./uninstall