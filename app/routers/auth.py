"""Login, logout, and health endpoints (T4.5 / WBS 4.5)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import verify_password
from app.config import is_production
from app.deps import get_session
from app.models import User
from app.rate_limit import login_limiter

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request, "login.html", {"error": None})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_session),
):
    client_ip = request.client.host if request.client else "unknown"
    if login_limiter.is_blocked(client_ip, username):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Terlalu banyak percobaan masuk. Coba lagi dalam 15 menit."},
            status_code=429,
        )
    user = db.scalar(select(User).where(User.username == username.strip()))
    if user is None or not verify_password(password, user.password_hash):
        login_limiter.record_failure(client_ip, username)
        return templates.TemplateResponse(
            request, "login.html", {"error": "Nama pengguna atau kata sandi salah."}, status_code=401
        )
    login_limiter.clear(client_ip, username)
    request.session.clear()
    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@router.get("/healthz")
def healthz(request: Request):
    ok = True
    try:
        request.app.state.db.healthcheck()
    except Exception:
        ok = False
    return {"status": "ok" if ok else "error", "db": "ok" if ok else "error"}
