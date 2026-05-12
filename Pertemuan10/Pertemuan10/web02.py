import os
import sqlite3
from flask import Flask, redirect, request, session, render_template_string
from jinja2 import Template

app = Flask(__name__)
app.secret_key = 'sqlinjection'
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# --- CSS & HTML ASSETS ---

BASE_HEAD = '''
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap" rel="stylesheet">

    <style>
        :root {
            --bg:       #030712;
            --surface:  #0a0f1e;
            --panel:    #0d1424;
            --border:   #1a2744;
            --glow:     #00ffe5;
            --glow2:    #ff2d78;
            --glow3:    #a855f7;
            --text:     #c9d8f0;
            --muted:    #3a5070;
            --mono:     'Share Tech Mono', monospace;
            --display:  'Orbitron', sans-serif;
            --body:     'Rajdhani', sans-serif;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: var(--body);
            background-color: var(--bg);
            color: var(--text);
            min-height: 100vh;
            overflow-x: hidden;
        }

        body::before {
            content: '';
            position: fixed;
            inset: 0;
            background: repeating-linear-gradient(
                0deg,
                transparent,
                transparent 2px,
                rgba(0,0,0,0.15) 2px,
                rgba(0,0,0,0.15) 4px
            );
            pointer-events: none;
            z-index: 9999;
        }

        body::after {
            content: '';
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(rgba(0,255,229,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,255,229,0.03) 1px, transparent 1px);
            background-size: 40px 40px;
            pointer-events: none;
            z-index: 0;
        }

        nav {
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(3,7,18,0.9);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            padding: 0 2rem;
            height: 72px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .nav-logo {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .logo-icon {
            width: 44px;
            height: 44px;
            border: 1px solid var(--glow);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 12px rgba(0,255,229,0.3);
        }

        .logo-text {
            font-family: var(--display);
            font-size: 1.1rem;
            font-weight: 900;
            letter-spacing: 0.1em;
            color: #00ffe5;
        }

        .logo-text span {
            color: var(--glow);
        }

        .nav-right {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .user-badge {
            font-family: var(--mono);
            font-size: 0.65rem;
            color: var(--glow);
            background: rgba(0,255,229,0.05);
            border: 1px solid rgba(0,255,229,0.2);
            padding: 6px 14px;
            border-radius: 6px;
        }

        .btn-logout {
            font-family: var(--mono);
            font-size: 0.65rem;
            color: var(--glow2);
            background: rgba(255,45,120,0.05);
            border: 1px solid rgba(255,45,120,0.3);
            padding: 8px 18px;
            border-radius: 6px;
            text-decoration: none;
            transition: all 0.2s;
        }

        .btn-logout:hover {
            background: rgba(255,45,120,0.15);
            color: #fff;
        }

        main {
            position: relative;
            z-index: 1;
            max-width: 760px;
            margin: 0 auto;
            padding: 3rem 1.5rem;
        }

        .section-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 2rem;
        }

        .section-label {
            font-family: var(--mono);
            font-size: 0.6rem;
            color: var(--glow);
            letter-spacing: 0.3em;
            text-transform: uppercase;
        }

        .section-line {
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, rgba(0,255,229,0.3), transparent);
        }

        .create-panel {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.8rem;
            margin-bottom: 3rem;
        }

        .create-panel textarea {
            width: 100%;
            background: rgba(0,0,0,0.4);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 1rem 1.2rem;
            color: var(--text);
            font-family: var(--mono);
            font-size: 0.8rem;
            resize: none;
            outline: none;
            min-height: 90px;
        }

        .create-panel textarea:focus {
            border-color: var(--glow);
            box-shadow: 0 0 0 3px rgba(0,255,229,0.08);
        }

        .panel-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 1rem;
        }

        .cmd-hint {
            font-family: var(--mono);
            font-size: 0.6rem;
            color: var(--muted);
        }

        .btn-deploy {
            font-family: var(--display);
            font-size: 0.6rem;
            font-weight: 700;
            letter-spacing: 0.15em;
            color: #000;
            background: var(--glow);
            border: none;
            padding: 12px 28px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-deploy:hover {
            background: #fff;
        }

        .timeline {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .entry {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.2rem 1.5rem;
            display: flex;
            align-items: flex-start;
            gap: 1.2rem;
        }

        .uid-chip {
            flex-shrink: 0;
            width: 48px;
            height: 48px;
            background: rgba(0,255,229,0.05);
            border: 1px solid rgba(0,255,229,0.15);
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .uid-label {
            font-family: var(--mono);
            font-size: 0.5rem;
            color: var(--muted);
        }

        .uid-value {
            font-family: var(--display);
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--glow);
        }

        .entry-body {
            flex: 1;
        }

        .entry-content {
            font-size: 1rem;
            color: #d4e2f4;
            line-height: 1.6;
        }

        .entry-id {
            font-family: var(--mono);
            font-size: 0.55rem;
            color: var(--muted);
            margin-top: 6px;
        }

        .btn-del {
            flex-shrink: 0;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: transparent;
            border-radius: 8px;
            color: var(--glow2);
            text-decoration: none;
        }

        .login-wrap {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 2rem;
        }

        .login-card {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 3rem 2.5rem;
            width: 100%;
            max-width: 420px;
        }

        .login-title {
            font-family: var(--display);
            font-size: 1.8rem;
            font-weight: 900;
            color: #fff;
            text-align: center;
            margin-bottom: 2rem;
        }

        .form-group {
            margin-bottom: 1.2rem;
        }

        .form-label {
            display: block;
            font-family: var(--mono);
            font-size: 0.6rem;
            color: var(--muted);
            margin-bottom: 8px;
        }

        .form-input {
            width: 100%;
            background: rgba(0,0,0,0.5);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 14px 16px;
            color: var(--text);
            font-family: var(--mono);
        }

        .btn-login {
            width: 100%;
            background: linear-gradient(135deg, var(--glow), #00c9b1);
            color: #000;
            border: none;
            border-radius: 10px;
            padding: 15px;
            font-family: var(--display);
            cursor: pointer;
            margin-top: 0.8rem;
        }

        /* HACK POPUP */
        .hack-popup {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.85);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 999999;
        }

        .hack-box {
            background: #0d1424;
            border: 1px solid #ff2d78;
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 0 40px rgba(255,45,120,0.4);
            animation: glitch 0.3s infinite alternate;
        }

        .hack-box h1 {
            font-family: var(--display);
            color: #ff2d78;
            font-size: 2rem;
            margin-bottom: 10px;
        }

        .hack-box p {
            font-family: var(--mono);
            color: #fff;
            font-size: 0.8rem;
        }

        @keyframes glitch {
            from { transform: translateX(-2px); }
            to { transform: translateX(2px); }
        }
    </style>
</head>
'''

INDEX_HTML = BASE_HEAD + '''
<body>

<div class="hack-popup" id="hackPopup">
    <div class="hack-box">
        <h1>YOU HACKED</h1>
        <p>System kernel compromised...</p>
    </div>
</div>

<nav>
    <div class="nav-logo">
        <div class="logo-icon">></div>
        <div class="logo-text">NAFIS<span>_CYBER</span></div>
    </div>

    <div class="nav-right">
        <div class="user-badge">{{ user }}</div>
        <a href="/logout" class="btn-logout">LOGOUT</a>
    </div>
</nav>

<main>

    <div class="section-header">
        <span class="section-label">// new_entry</span>
        <div class="section-line"></div>
    </div>

    <div class="create-panel">

        <form action="/create" method="post" id="deployForm">

            <textarea name="content"
            required
            placeholder="> initialize log entry..."></textarea>

            <div class="panel-footer">

                <span class="cmd-hint" id="statusMsg">
                    $ echo "[content]" >> timeline.log
                </span>

                <button type="submit"
                class="btn-deploy"
                id="deployBtn">
                    DEPLOY →
                </button>

            </div>

        </form>

    </div>

    <div class="section-header">
        <span class="section-label">// timeline.log</span>
        <div class="section-line"></div>
    </div>

    <div class="timeline">

        {% for item in tl %}
        <div class="entry">

            <div class="uid-chip">
                <span class="uid-label">UID</span>
                <span class="uid-value">{{ item.user_id }}</span>
            </div>

            <div class="entry-body">
                <div class="entry-content">{{ item.content }}</div>
                <div class="entry-id">
                    #{{ item.id }} — entry logged
                </div>
            </div>

            <a href="/delete/{{ item.id }}"
            class="btn-del">✕</a>

        </div>
        {% endfor %}

    </div>

</main>

<script>

    const form = document.getElementById('deployForm');
    const btn = document.getElementById('deployBtn');
    const msg = document.getElementById('statusMsg');

    // Variabel kontrol simulasi
    let isVulnerable = true; 

    form.addEventListener('submit', (e) => {
        if (isVulnerable) {
            e.preventDefault();
            
            // Tombol berubah merah
            btn.style.background = '#ff0000';
            btn.style.color = '#ffffff';
            btn.style.border = '1px solid #ff4d4d';
            btn.style.boxShadow = '0 0 25px #ff0000';

            // Efek teks status
            msg.style.color = '#ff2d78';
            msg.innerText = 'CRITICAL_ERROR: Unauthorized intercept detected.';

            // Ganti tulisan tombol
            btn.innerText = 'YOU HACKED';

            // Efek getar kecil
            btn.animate([
                { transform: 'translateX(0px)' },
                { transform: 'translateX(-3px)' },
                { transform: 'translateX(3px)' },
                { transform: 'translateX(0px)' }
            ], {
                duration: 120,
                iterations: 4
            });

            // Popup
            alert('YOU HACKED');
        }
    });
</script>



</body>
'''

LOGIN_HTML = BASE_HEAD + '''
<body>

<div class="login-wrap">

    <div class="login-card">

        <div class="login-title">
            NEXUS<span>_</span>
        </div>

        <form method="post">

            <div class="form-group">
                <label class="form-label">
                    Username
                </label>

                <input class="form-input"
                name="username">
            </div>

            <div class="form-group">
                <label class="form-label">
                    Password
                </label>

                <input class="form-input"
                name="password"
                type="password">
            </div>

            <button type="submit"
            class="btn-login">
                LOGIN
            </button>

        </form>

    </div>

</div>

</body>
'''

# --- DATABASE LOGIC ---

def connect_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():

    with connect_db() as conn:

        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS user(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS time_line(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES user(id)
            )
        ''')

        conn.commit()

def init_data():

    with connect_db() as conn:

        cur = conn.cursor()

        cur.executemany(
            'INSERT OR IGNORE INTO user(username,password) VALUES (?,?)',
            [
                ('alice','alicepw'),
                ('bob','bobpw')
            ]
        )

        cur.executemany(
            'INSERT OR IGNORE INTO time_line(user_id,content) VALUES (?,?)',
            [
                (1,'Hello world'),
                (2,'Hi there')
            ]
        )

        conn.commit()

def authenticate(username,password):

    with connect_db() as conn:

        cur = conn.cursor()

        query = (
            "SELECT id,username FROM user "
            "WHERE username='%s' AND password='%s'"
            % (username,password)
        )

        cur.execute(query)

        row = cur.fetchone()

        return dict(row) if row else None

def create_time_line(uid, content):

    with connect_db() as conn:

        cur = conn.cursor()

        cur.execute(
            'INSERT INTO time_line(user_id,content) VALUES (?,?)',
            (uid, content)
        )

        conn.commit()

def get_time_lines():

    with connect_db() as conn:

        cur = conn.cursor()

        cur.execute(
            'SELECT id,user_id,content FROM time_line ORDER BY id DESC'
        )

        return [dict(r) for r in cur.fetchall()]

def delete_time_line(uid, tid):

    with connect_db() as conn:

        cur = conn.cursor()

        query = f"""
        DELETE FROM time_line
        WHERE user_id={uid}
        AND id={tid}
        """

        cur.execute(query)

        conn.commit()

# --- ROUTES ---

@app.route('/init')
def init_page():

    create_tables()
    init_data()

    return redirect('/')

@app.route('/')
def index():

    if 'uid' in session:

        tl = get_time_lines()

        return render_template_string(
            INDEX_HTML,
            user=session['username'],
            tl=tl
        )

    return redirect('/login')

@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        user = authenticate(
            request.form['username'],
            request.form['password']
        )

        if user:

            session['uid'] = user['id']
            session['username'] = user['username']

            return redirect('/')

    return render_template_string(LOGIN_HTML)

@app.route('/create', methods=['POST'])
def create():

    if 'uid' in session:

        create_time_line(
            session['uid'],
            request.form['content']
        )

    return redirect('/')

@app.route('/delete/<int:tid>')
def delete(tid):

    if 'uid' in session:

        delete_time_line(
            session['uid'],
            tid
        )

    return redirect('/')

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

if __name__ == '__main__':

    app.run(debug=True)