from app import create_app
import traceback

app = create_app()
app.testing = True
with app.test_client() as c:
    try:
        rv = c.get('/')
        print('STATUS', rv.status_code)
        print(rv.data.decode('utf-8', errors='replace')[:2000])
    except Exception:
        traceback.print_exc()
