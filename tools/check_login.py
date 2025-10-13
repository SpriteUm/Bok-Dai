from app import create_app
from urllib.parse import urlencode

app = create_app()
app.testing = True
with app.test_client() as c:
    rv = c.post('/auth/login', data={'username':'doesnotexist','password':'x'}, follow_redirects=True)
    print('status', rv.status_code)
    print(rv.data.decode('utf-8', errors='replace')[:2000])
