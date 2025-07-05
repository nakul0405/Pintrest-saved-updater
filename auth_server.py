from flask import Flask, redirect

app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Pinterest Cookie Extractor is Running!'

@app.route('/login')
def login():
    return redirect("https://www.pinterest.com/login/")

if __name__ == '__main__':
    # BIND to Railway-compatible host and port
    import os
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
