from fastapi import FastAPI
from routes.index import playersRouter, organizerRouter, adminRouter, userRouter,tournamentRouter, generalRouter, fixturesRouter
from config.db import get_db, engine
import models.index as models
# from fastapi_pagination import add_pagination

models.Base.metadata.create_all(bind=engine)


app = FastAPI()
# add_pagination(app)

@app.get('/')
def backend_testing():
    return {'msg', 'backend is running'}

app.include_router(userRouter, prefix="/users", tags=["Users"])
app.include_router(playersRouter, prefix='/players', tags=["Players"])
app.include_router(organizerRouter, prefix='/organizer', tags=["Organizer"])
app.include_router(tournamentRouter, prefix='/tournaments', tags=["Tournament"])
app.include_router(generalRouter, prefix='/general', tags=["General"])
app.include_router(fixturesRouter, prefix='/fixtures', tags=["Fixtures"])

app.include_router(adminRouter, prefix='/admin', tags=["Admin"])
