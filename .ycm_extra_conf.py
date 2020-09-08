from os.path import join


def Settings(**kwargs):
    faasm_interpreter = join("usr", "local", "code", "faasm", "venv", "bin", "python")
    return {"interpreter_path": faasm_interpreter}
