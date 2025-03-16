from server.api.endpoints.exercises import router as exercise_router
from server.api.endpoints.run_pytests import router as run_pytests_router
from server.api.endpoints.auth import router as auth_router
from server.api.endpoints.run_code import router as run_code_router

# Aqui, incluímos todos os routers em um único arquivo
def include_routes(app):
    app.include_router(exercise_router)
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(run_pytests_router)
    app.include_router(run_code_router)