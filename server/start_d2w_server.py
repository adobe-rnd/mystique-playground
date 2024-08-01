from server.d2w_server import Doc2Web


def main():
    print("Starting Doc2Web...")
    doc2web_server = Doc2Web()
    doc2web_server.run(host='0.0.0.0', port=4003)


if __name__ == "__main__":
    print("Starting server...")
    main()
