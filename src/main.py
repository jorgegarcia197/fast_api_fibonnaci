from fastapi import FastAPI, Depends
from routers import auth, fib
from starlette.staticfiles import StaticFiles


app = FastAPI(
    debug=True,
    title="Fibonacci API",
    description="This is a simple API for calculating the fibonacci series up to a given value, with simple integrations with Firebase",
    version="0.1",
)


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(fib.router, prefix="/fibonacci", tags=["fibonnaci"])
