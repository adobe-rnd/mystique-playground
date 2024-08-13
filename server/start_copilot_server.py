from server.copilot_server import CopilotServer


def main():
    print("Starting Assistant...")
    assistant_server = CopilotServer()
    assistant_server.run(host='0.0.0.0', port=4001)


if __name__ == "__main__":
    print("Starting server...")
    main()
