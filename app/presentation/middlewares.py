from fastapi.middleware.cors import CORSMiddleware

ORIGENES_PERMITIDOS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def configurar_middlewares(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGENES_PERMITIDOS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
