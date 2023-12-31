import os

import uvicorn

if __name__ == "__main__":
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run(
        "game_of_life:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[parent_dir],
        reload_includes=["*.py", "*.html", "*.js", "*.css"],
        log_level="info",
    )
