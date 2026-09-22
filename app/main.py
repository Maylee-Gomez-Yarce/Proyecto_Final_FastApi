from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from app.exceptions.handlers import (
    generic_exception_handler,
    integrity_error_handler,
    validation_error_handler,
)

from app.routes.auth_routes import router as auth_router
from app.routes.usuario_routes import router as usuario_router
from app.routes.paciente_routes import router as paciente_router
from app.routes.medico_routes import router as medico_router
from app.routes.disponibilidad_routes import router as disponibilidad_router
from app.routes.cita_routes import router as cita_router


app = FastAPI(
    title="Plataforma de Citas",
    description="API REST para la gestión de citas",
    version="1.0.0"
)


# =========================
# Manejo global de errores
# =========================

app.add_exception_handler(
    IntegrityError,
    integrity_error_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_error_handler,
)

app.add_exception_handler(
    Exception,
    generic_exception_handler,
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Routers
# =========================

app.include_router(auth_router)
app.include_router(usuario_router)
app.include_router(paciente_router)
app.include_router(medico_router)
app.include_router(disponibilidad_router)
app.include_router(cita_router)


# =========================
# Middleware personalizado
# =========================

@app.middleware("http")
async def middleware_info(request, call_next):
    response = await call_next(request)

    response.headers["X-App-Name"] = "Plataforma de Citas"
    response.headers["X-API-Version"] = "1.0.0"

    return response


# =========================
# Ruta principal
# =========================

@app.get("/")
def root():
    return {
        "message": "API de la Plataforma de Citas funcionando correctamente"
    }