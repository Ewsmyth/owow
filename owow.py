from website import create_owow

owow = create_owow()

if __name__ == "__main__":
    owow.run(debug=True, host="0.0.0.0", port=6876)