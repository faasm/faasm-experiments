#include <Python.h>

int main()
{
    wchar_t* program = Py_DecodeLocale("hello.py", NULL);
    Py_SetProgramName(program);

    Py_Initialize();
    PyRun_SimpleString("from time import time,ctime\n"
                       "print('Today is', ctime(time()))\n");

    if (Py_FinalizeEx() < 0) {
        exit(120);
    }

    PyMem_RawFree(program);
    return 0;
}
