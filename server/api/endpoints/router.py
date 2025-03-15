from server.api.endpoints.exercises import router as exercise_router
from server.api.endpoints.users import router as users_router

# Aqui, incluímos todos os routers em um único arquivo
def include_routes(app):
    app.include_router(exercise_router)
    app.include_router(users_router)