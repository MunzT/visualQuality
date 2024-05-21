REM Start when no venv exists
CALL cd ..
CALL virtualenv env
CALL env\Scripts\activate
CALL pip3 install -r requirements.txt
