import uvicorn

# Uruchom aplikację na porcie 8002 dla panelu webowego
if __name__ == "__main__":
    # Przekazujemy aplikację jako string importu, aby umożliwić opcję 'reload'
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
