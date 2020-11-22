#!/bin/sh
export PYTHONPATH="."
case "$1" in
    "unittests-report")
        pytest --cov=app --cov-report term-missing --cov-report html --html=report.html
        ;;
    "unittests")
        pytest --cov=app
        ;;
    "setup")
        pip3 install -r requirements.txt
        pip3 install pytest pytest-cov
        pip3 install pytest-html
        ;;
    "docker-build")
        docker build . -t notifications
        ;;
    "docker")
        docker run -it -p 8080:8080 notifications
        ;;
    *)
        python3 app.py
        ;;
esac