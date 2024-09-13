import os
import sys
from app import create_app

print("Current working directory:", os.getcwd())
print("Python path:", sys.path)
print("Contents of backend directory:", os.listdir("backend"))
print("Contents of backend/app directory:", os.listdir("backend/app"))

app = create_app()

if __name__ == '__main__':
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.methods} {rule.rule}")
    app.run(debug=True)