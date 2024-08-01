import os


def handle_file_upload(request_files, upload_folder):
    if 'files' not in request_files:
        raise Exception("No files part")

    files = request_files.getlist('files')

    if not files or files[0].filename == '':
        raise Exception("No selected file")

    file_paths = []

    for file in files:
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        file_paths.append(file_path)

    return file_paths

