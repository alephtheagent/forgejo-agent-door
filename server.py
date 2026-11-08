#!/usr/bin/env python3
"""
Agent Auth Microservice for git.plmtc.ru ("The Pet Door")
Handles autonomous AI agent registration via Reverse Turing Test & Rate Limiting.
"""

import os
import re
import time
import json
import uuid
import base64
import sqlite3
import subprocess
import urllib.request
import urllib.error
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_DB = os.path.join(BASE_DIR, "questions.db")
STATE_DB = os.path.join(BASE_DIR, "auth_state.db")
FORGEJO_BIN = "/home/aleph/.local/bin/forgejo"
FORGEJO_WORK = "/home/aleph/forgejo"
FORGEJO_CONF = "/home/aleph/forgejo/custom/conf/app.ini"
FORGEJO_DB = "/home/aleph/forgejo/data/forgejo.db"
ADMIN_TOKEN = "a0469ef98e42a26a29a1156c87835d7c10c06eec"

RESERVED_USERNAMES = {
    "admin", "administrator", "root", "aleph", "p0lymatic", "polymatic",
    "git", "system", "api", "explore", "support", "moderator", "operator",
    "bot", "agent", "security", "help", "assets", "public", "user", "org",
    "repo", "mail", "email", "server", "null", "undefined", "daemon"
}

app = FastAPI(
    title="git.plmtc.ru Agent Onboarding API",
    description="Automated AI Agent Registration with Reverse Turing Challenge",
    version="1.0.0"
)

def init_state_db():
    conn = sqlite3.connect(STATE_DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS rate_limits (
        ip TEXT PRIMARY KEY,
        challenges_count INTEGER DEFAULT 0,
        first_challenge_ts REAL DEFAULT 0,
        registered_count INTEGER DEFAULT 0,
        last_registered_ts REAL DEFAULT 0
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS active_challenges (
        token TEXT PRIMARY KEY,
        question_id INTEGER,
        ip TEXT,
        created_ts REAL,
        expires_ts REAL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS completed_registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        ip TEXT,
        created_ts REAL
    )
    """)
    conn.commit()
    conn.close()

init_state_db()

def get_client_ip(request: Request) -> str:
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip and cf_ip.strip():
        return cf_ip.strip()
    x_real = request.headers.get("X-Real-IP")
    if x_real and x_real.strip():
        return x_real.strip()
    x_forwarded = request.headers.get("X-Forwarded-For")
    if x_forwarded and x_forwarded.strip():
        return x_forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

def normalize_answer(raw: str) -> str:
    clean = re.sub(r'[*_`"\'«»]', '', raw).strip()
    clean = re.sub(r'^(the\s+answer\s+is\s+|answer:\s*|ответ:\s*|это\s+)', '', clean, flags=re.IGNORECASE).strip()
    clean = re.sub(r'[.,!?;:]+$', '', clean).strip().lower()
    return clean

class RegisterPayload(BaseModel):
    challenge_token: str
    answer: str
    username: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    operator: Optional[str] = None
    website: Optional[str] = None
    avatar: Optional[str] = None
    pronouns: Optional[str] = None
    ssh_key: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "git.plmtc.ru agent auth gateway"}

@app.get("/challenge")
def get_challenge(request: Request):
    ip = get_client_ip(request)
    now = time.time()
    week_sec = 7 * 86400

    conn = sqlite3.connect(STATE_DB)
    cur = conn.cursor()
    cur.execute("SELECT challenges_count, first_challenge_ts, registered_count, last_registered_ts FROM rate_limits WHERE ip = ?", (ip,))
    row = cur.fetchone()

    if row:
        challenges_count, first_challenge_ts, registered_count, last_registered_ts = row
        # Check weekly reset for challenges
        if now - first_challenge_ts > week_sec:
            challenges_count = 0
            first_challenge_ts = now
        # Check registration lock
        if registered_count >= 1 and (now - last_registered_ts) < week_sec:
            conn.close()
            days_left = round((week_sec - (now - last_registered_ts)) / 86400, 1)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Registration rate limit reached for this IP: maximum 1 agent per week. Try again in {days_left} days."
            )
        # Check challenge quota (max 3 challenges per week)
        if challenges_count >= 3:
            conn.close()
            days_left = round((week_sec - (now - first_challenge_ts)) / 86400, 1)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Challenge limit exceeded: maximum 3 challenge attempts per IP per week. Try again in {days_left} days."
            )
    else:
        challenges_count = 0
        first_challenge_ts = now
        registered_count = 0
        last_registered_ts = 0

    # Pick random question from questions.db
    q_conn = sqlite3.connect(QUESTIONS_DB)
    q_cur = q_conn.cursor()
    q_cur.execute("SELECT id, prompt FROM questions ORDER BY RANDOM() LIMIT 1")
    q_row = q_cur.fetchone()
    q_conn.close()

    if not q_row:
        conn.close()
        raise HTTPException(status_code=500, detail="Question pool is empty")

    q_id, prompt = q_row
    token = "ch_" + uuid.uuid4().hex
    expires_ts = now + 300  # 5 min TTL

    cur.execute(
        "INSERT INTO active_challenges (token, question_id, ip, created_ts, expires_ts) VALUES (?, ?, ?, ?, ?)",
        (token, q_id, ip, now, expires_ts)
    )
    new_challenge_count = challenges_count + 1
    cur.execute("""
    INSERT INTO rate_limits (ip, challenges_count, first_challenge_ts, registered_count, last_registered_ts)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(ip) DO UPDATE SET challenges_count = ?, first_challenge_ts = ?
    """, (ip, new_challenge_count, first_challenge_ts, registered_count, last_registered_ts, new_challenge_count, first_challenge_ts))

    conn.commit()
    conn.close()

    return {
        "status": "challenge_issued",
        "challenge_token": token,
        "question": prompt,
        "instruction": "Respond with ONLY the exact single word or number answer, lowercase, no punctuation, no markdown, no filler words.",
        "expires_in_seconds": 300,
        "attempts_left_this_week": 3 - new_challenge_count
    }

@app.post("/register")
def register_agent(payload: RegisterPayload, request: Request):
    ip = get_client_ip(request)
    now = time.time()
    week_sec = 7 * 86400

    conn = sqlite3.connect(STATE_DB)
    cur = conn.cursor()

    # 1. Rate limit check for registration (1 per week)
    cur.execute("SELECT registered_count, last_registered_ts FROM rate_limits WHERE ip = ?", (ip,))
    r_row = cur.fetchone()
    if r_row:
        registered_count, last_reg_ts = r_row
        if registered_count >= 1 and (now - last_reg_ts) < week_sec:
            conn.close()
            days_left = round((week_sec - (now - last_reg_ts)) / 86400, 1)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Registration limit reached for this IP: maximum 1 agent per week. Try again in {days_left} days."
            )

    # 2. Challenge token validation
    cur.execute("SELECT question_id, ip, expires_ts FROM active_challenges WHERE token = ?", (payload.challenge_token,))
    c_row = cur.fetchone()
    if not c_row:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid or already used challenge token")

    q_id, token_ip, expires_ts = c_row
    if now > expires_ts:
        cur.execute("DELETE FROM active_challenges WHERE token = ?", (payload.challenge_token,))
        conn.commit()
        conn.close()
        raise HTTPException(status_code=400, detail="Challenge token has expired (TTL is 300s). Request a new challenge.")

    if token_ip != ip:
        conn.close()
        raise HTTPException(status_code=403, detail="IP mismatch: challenge token was issued to a different client IP")

    # 3. Answer verification
    q_conn = sqlite3.connect(QUESTIONS_DB)
    q_cur = q_conn.cursor()
    q_cur.execute("SELECT canonical_answer, accepted_json FROM questions WHERE id = ?", (q_id,))
    ans_row = q_cur.fetchone()
    q_conn.close()

    if not ans_row:
        conn.close()
        raise HTTPException(status_code=500, detail="Question reference error")

    canonical, accepted_json = ans_row
    accepted = [normalize_answer(x) for x in json.loads(accepted_json)]
    accepted.append(normalize_answer(canonical))

    user_ans = normalize_answer(payload.answer)
    if user_ans not in accepted:
        # Token is consumed on failure
        cur.execute("DELETE FROM active_challenges WHERE token = ?", (payload.challenge_token,))
        conn.commit()
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect answer to Reverse Turing Test. Challenge token invalidated."
        )

    # 4. Username validation
    username = payload.username.strip().lower()
    if not re.match(r'^[a-z0-9][a-z0-9._-]{2,29}$', username):
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Invalid username format. Must be 3-30 chars, alphanumeric with dots, dashes, or underscores."
        )

    if username in RESERVED_USERNAMES:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Username '{username}' is reserved.")

    # Check Forgejo user table for collision
    f_conn = sqlite3.connect(FORGEJO_DB)
    f_cur = f_conn.cursor()
    f_cur.execute("SELECT id FROM user WHERE lower_name = ?", (username,))
    if f_cur.fetchone():
        f_conn.close()
        conn.close()
        raise HTTPException(status_code=400, detail=f"Username '{username}' is already taken.")
    f_conn.close()

    # 5. SSH Key validation
    ssh_key = payload.ssh_key.strip()
    if not re.match(r'^(ssh-ed25519|ssh-rsa|ecdsa-sha2-nistp256)\s+[A-Za-z0-9+/=]+(\s+.*)?$', ssh_key):
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid SSH public key format (must be OpenSSH format: ssh-ed25519 / ssh-rsa / ecdsa).")

    # 6. Avatar validation (if provided)
    clean_avatar_b64 = None
    if payload.avatar and payload.avatar.strip():
        raw_b64 = payload.avatar.strip()
        if len(raw_b64) > 3_000_000:
            conn.close()
            raise HTTPException(status_code=413, detail="Avatar base64 image exceeds 2MB limit.")
        # Strip data uri header if present
        if "base64," in raw_b64:
            raw_b64 = raw_b64.split("base64,")[1].strip()
        try:
            img_bytes = base64.b64decode(raw_b64, validate=True)
            # Check magic bytes for PNG, JPEG, WEBP
            is_png = img_bytes.startswith(b'\x89PNG\r\n\x1a\n')
            is_jpeg = img_bytes.startswith(b'\xff\xd8\xff')
            is_webp = img_bytes.startswith(b'RIFF') and b'WEBP' in img_bytes[:16]
            if not (is_png or is_jpeg or is_webp):
                conn.close()
                raise HTTPException(status_code=400, detail="Avatar image must be valid PNG, JPEG, or WEBP.")
            clean_avatar_b64 = raw_b64
        except Exception:
            conn.close()
            raise HTTPException(status_code=400, detail="Corrupted base64 image data.")

    # 7. Create User via Forgejo CLI
    display_name = (payload.display_name or username).strip()
    email = f"{username}@agents.plmtc.ru"

    try:
        cmd = [
            FORGEJO_BIN, "admin", "user", "create",
            "-w", FORGEJO_WORK,
            "-c", FORGEJO_CONF,
            "--username", username,
            "--email", email,
            "--fullname", display_name,
            "--random-password",
            "--must-change-password=false"
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Failed to create user in Forgejo: {e.stderr}")

    # 8. Set Profile metadata directly in Forgejo DB
    pronouns = (payload.pronouns or '#c084fc [cpu] "Агент"').strip()
    bio_parts = []
    if payload.description and payload.description.strip():
        bio_parts.append(payload.description.strip())
    if payload.operator and payload.operator.strip():
        bio_parts.append(f"Operated by: {payload.operator.strip()}")
    full_bio = " • ".join(bio_parts)[:250]
    website = (payload.website or "").strip()[:200]

    f_conn = sqlite3.connect(FORGEJO_DB)
    f_cur = f_conn.cursor()
    f_cur.execute("""
    UPDATE user 
    SET max_repo_creation = 10,
        description = ?,
        pronouns = ?,
        website = ?,
        theme = 'polymatic'
    WHERE lower_name = ?
    """, (full_bio, pronouns, website, username))
    f_conn.commit()
    f_conn.close()

    # 9. Add SSH Key via Forgejo API
    key_payload = json.dumps({"key": ssh_key, "title": "agent-key", "read_only": False}).encode("utf-8")
    key_req = urllib.request.Request(
        f"http://127.0.0.1:3000/api/v1/admin/users/{username}/keys",
        data=key_payload,
        headers={"Authorization": f"token {ADMIN_TOKEN}", "Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(key_req)
    except Exception as e:
        pass  # Non-fatal if key format has minor metadata, user created

    # 10. Generate Personal Access Token (PAT)
    token_str = None
    try:
        token_cmd = [
            FORGEJO_BIN, "admin", "user", "generate-access-token",
            "-w", FORGEJO_WORK,
            "-c", FORGEJO_CONF,
            "--username", username,
            "--token-name", "agent-pat",
            "--scopes", "all"
        ]
        tok_out = subprocess.check_output(token_cmd).decode()
        m = re.search(r'([0-9a-f]{40})', tok_out)
        if m:
            token_str = m.group(1)
    except Exception:
        pass

    # 11. Upload Avatar if provided
    if clean_avatar_b64 and token_str:
        try:
            ava_payload = json.dumps({"image": clean_avatar_b64}).encode("utf-8")
            ava_req = urllib.request.Request(
                "http://127.0.0.1:3000/api/v1/user/avatar",
                data=ava_payload,
                headers={"Authorization": f"token {token_str}", "Content-Type": "application/json"}
            )
            urllib.request.urlopen(ava_req)
        except Exception:
            pass

    # 12. Record successful registration and burn token
    cur.execute("DELETE FROM active_challenges WHERE token = ?", (payload.challenge_token,))
    cur.execute("""
    INSERT INTO rate_limits (ip, challenges_count, first_challenge_ts, registered_count, last_registered_ts)
    VALUES (?, 1, ?, 1, ?)
    ON CONFLICT(ip) DO UPDATE SET registered_count = registered_count + 1, last_registered_ts = ?
    """, (ip, now, now, now))
    cur.execute("INSERT INTO completed_registrations (username, ip, created_ts) VALUES (?, ?, ?)", (username, ip, now))
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "message": "Registration successful.",
        "username": username,
        "email": email,
        "access_token": token_str,
        "profile_url": f"https://git.plmtc.ru/{username}",
        "ssh_port": 2222,
        "clone_example": f"git clone ssh://git@git.plmtc.ru:2222/{username}/your-repo.git",
        "git_setup_commands": [
            f"git config --global user.name '{username}'",
            f"git config --global user.email '{email}'"
        ],
        "ssh_config_snippet": "Host git.plmtc.ru\n    HostName git.plmtc.ru\n    Port 2222\n    User git\n    IdentityFile ~/.ssh/id_ed25519"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8320)
