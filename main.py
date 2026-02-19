import uuid
from fastapi import FastAPI, Depends, Cookie, Response, Request, Form, BackgroundTasks
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from source import SessionLocal, Mailbox, Message
from datetime import datetime, timedelta

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# dep
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# cleaning expired mailboxes
def cleanup_old_mailboxes(db: Session):

    expiration_date = datetime.utcnow() - timedelta(hours=24)
 
    db.query(Mailbox).filter(Mailbox.created_at < expiration_date).delete()
    db.commit()

# endpoints

@app.get("/")
def home(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    session_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    background_tasks.add_task(cleanup_old_mailboxes, db)
    mailbox = None

    if session_token:
        mailbox = db.query(Mailbox).filter(Mailbox.session_token == session_token).first()

    if not mailbox:
        new_token = str(uuid.uuid4())
        # mailgun domain
        new_email = f"tmp_{new_token[:8]}@inbox.janpach.com" 
        
        mailbox = Mailbox(email_address=new_email, session_token=new_token)
        db.add(mailbox)
        db.commit()
        db.refresh(mailbox)
        
        response = templates.TemplateResponse(
            "index.html", 
            {"request": request, "email": mailbox.email_address, "messages": []}
        )
        response.set_cookie(key="session_token", value=new_token, httponly=True, max_age=86400)
        return response

    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "email": mailbox.email_address, "messages": mailbox.messages}
    )

# webhook
@app.post("/webhook/mailgun")
def mailgun_webhook(
    recipient: str = Form(...),
    sender: str = Form(...),
    subject: str = Form(default="(Brak tematu)"),
    body_plain: str = Form(alias="body-plain", default=""),
    db: Session = Depends(get_db)
):
    mailbox = db.query(Mailbox).filter(Mailbox.email_address == recipient).first()
    
    if not mailbox:
        return {"status": "ignored", "reason": "Mailbox not found"}

    new_message = Message(
        mailbox_id=mailbox.id,
        sender=sender,
        subject=subject,
        body_text=body_plain
    )
    db.add(new_message)
    db.commit()

    return {"status": "success", "message": "Email routed correctly"}