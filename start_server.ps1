Stop-Process -Name python -Force -ErrorAction SilentlyContinue
cd $PSScriptRoot
python -c "import uvicorn; from main import app; uvicorn.run(app, host='0.0.0.0', port=8080)"
