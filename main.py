from automata.tm.dtm import DTM
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi_mail import ConnectionConfig, MessageSchema, MessageType, FastMail
from sqlalchemy.orm import Session

from sql_app import crud, models, schemas
from sql_app.database import engine, SessionLocal
from util.email_body import EmailSchema

from prometheus_fastapi_instrumentator import Instrumentator
from rabbitmq_service import RabbitmqService

import json

models.Base.metadata.create_all(bind=engine)

conf = ConnectionConfig(
    MAIL_USERNAME="1077fe991ea5ec",
    MAIL_PASSWORD="3f4bc994951607",
    MAIL_FROM="from@example.com",
    MAIL_PORT=587,
    MAIL_SERVER="sandbox.smtp.mailtrap.io",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

app = FastAPI()

Instrumentator().instrument(app).expose(app)

# Patter Singleton
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/batch_dtm")
async def batch_dtm(info: Request, rabbitmq_service: RabbitmqService = Depends()):
    info = await info.json()
    await rabbitmq_service.publish_messages(info)
    return {"code": "200", "msg": "Batch has been sent to the queue"}

@app.get("/get_history/{id}")
async def get_history(id: int, db: Session = Depends(get_db)):
    history = crud.get_history(db=db, id=id)
    if history is None:
        return {
            "code": "404",
            "msg": "not found"
        }
    return history


@app.get("/get_all_history")
async def get_all_history(db: Session = Depends(get_db)):
    history = crud.get_all_history(db=db)
    return history

db = SessionLocal()

@app.post("/dtm")
async def dtm(info: Request):
    info_json = json.loads(info)

    for field in ["states", "input_symbols", "tape_symbols", "initial_state", "blank_symbol", "final_states", "transitions", "input"]:
            if field not in info_json:
                raise HTTPException(status_code=400, detail=f"{field} cannot be empty")

    dtm = DTM(
        states=set(info_json["states"]),
        input_symbols=set(info_json["input_symbols"]),
        tape_symbols=set(info_json["tape_symbols"]),
        transitions=info_json["transitions"],
        initial_state=info_json["initial_state"],
        blank_symbol=info_json["blank_symbol"],
        final_states=set(info_json["final_states"]),
    )

    if dtm.accepts_input(info_json["input"]):
        print('accepted')
        result = "accepted"
    else:
        print('rejected')
        result = "rejected"

    history = schemas.History(query=str(info), result=result)
    crud.create_history(db=db, history=history)

    email_shema = EmailSchema(email=["to@example.com"])

    await simple_send(email_shema, result=result, configuration=str(info))

    return {
        "code": result == "accepted" and "200" or "400",
        "msg": result
    }


async def simple_send(email: EmailSchema, result: str, configuration: str):
    html = """
    <p>Thanks for using Fastapi-mail</p>
    <p> The result is: """ + result + """</p>
    <p> We have used this configuration: """ + configuration + """</p>
    """
    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=email.dict().get("email"),
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message)
    return "OK"