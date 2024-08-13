from server.web_creator_server import WebCreator


def main():
    print("Starting Web Creator...")
    web_creator_server = WebCreator()
    web_creator_server.run(host='0.0.0.0', port=4003)


if __name__ == "__main__":
    print("Starting server...")
    main()
