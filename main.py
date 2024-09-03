from app import app, db

def main():
    with app.app_context():
        db.drop_all()
        db.create_all()

    app.run(port=5005, debug=True, threaded=True)

if __name__ == "__main__":
    main()
