import os


def handle_file_upload(files, upload_folder):
    if not files or files[0].filename == '':
        raise Exception("No selected file")

    file_paths = []

    for file in files:
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        file_paths.append(file_path)

    return file_paths

