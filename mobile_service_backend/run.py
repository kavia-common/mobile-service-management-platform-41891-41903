from app import app

if __name__ == "__main__":
    # Must match work item: backend on port 3001
    app.run(host="0.0.0.0", port=3001, debug=True)
