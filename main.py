'''
def main():
    print("Hello from expense-tracker!")


if __name__ == "__main__":
    main()
'''

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

