from server.assistant_server import AssistantServer


def main():
    print("Starting Assistant...")
    assistant_server = AssistantServer()
    assistant_server.run(host='0.0.0.0', port=4001)


if __name__ == "__main__":
    print("Starting server...")
    main()
