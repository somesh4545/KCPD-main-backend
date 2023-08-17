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

app.include_router(userRouter, prefix="/users")
app.include_router(playersRouter, prefix='/players')
app.include_router(organizerRouter, prefix='/organizer')
app.include_router(tournamentRouter, prefix='/tournaments')
app.include_router(generalRouter, prefix='/general')
app.include_router(fixturesRouter, prefix='/fixtures')

app.include_router(adminRouter, prefix='/admin')
