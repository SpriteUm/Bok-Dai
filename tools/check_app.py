from app import create_app
app = create_app()
with app.test_client() as c:
    rv = c.get('/')
    print('status_code', rv.status_code)
    print(rv.data.decode()[:2000])
