"""
Entry point — start the Flask development server.
Usage: python run.py
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    print("\n--- AI Nutrition API Server ---")
    print("=" * 40)
    print("  Running on http://0.0.0.0:5000")
    print("  Health check: http://localhost:5000/api/health")
    print("=" * 40 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
