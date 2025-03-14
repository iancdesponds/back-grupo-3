from server.api.endpoints.exercises import router as index_router

# Aqui, incluímos todos os routers em um único arquivo
def include_routes(app):
    app.include_router(index_router)