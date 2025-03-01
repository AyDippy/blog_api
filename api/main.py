from api.routes.users import router
from api.routes import auth
from api.routes import password_reset
from fastapi import FastAPI
from api.routes import blog


app = FastAPI()

app.include_router(router)
app.include_router(auth.router)
app.include_router(password_reset.router)
app.include_router(blog.router)