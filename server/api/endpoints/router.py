from server.api.endpoints.exercises import router as exercise_router
from server.api.endpoints.users import router as users_router
from server.api.endpoints.submit import router as submit_router
from server.api.endpoints.run_pytests import router as run_pytests_router

# Aqui, incluímos todos os routers em um único arquivo
def include_routes(app):
    app.include_router(exercise_router)
    app.include_router(users_router)
    app.include_router(submit_router)
    app.include_router(run_pytests_router)