CALL cd ..
CALL env\Scripts\activate
echo venv started
set FLASK_APP=exploreData.py
set FLASK_DEBUG=0
flask run --host=0.0.0.0 -p 2000
pause
