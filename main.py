import os
import uvicorn
from server import app

def main():
    port = int(os.environ.get("PORT", 8000))  # local default
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Para ejecución local
    main()
