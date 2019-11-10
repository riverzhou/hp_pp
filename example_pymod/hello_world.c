#include <Python.h>

#include "myhello.h"

static PyObject* add_function(PyObject *self, PyObject *args)
{
	int num1, num2;
	PyObject *result=NULL;
	if (!PyArg_ParseTuple(args, "ii", &num1, &num2)) {
		printf("传入参数错误！\n");
		return NULL;
	}
	result = Py_BuildValue("i", num1+num2);
	return result;
}

static PyObject* hello_function(PyObject *self, PyObject *args)
{
	int n;
	PyObject *result=NULL;
	if (!PyArg_ParseTuple(args, "i", &n)) {
		printf("传入参数错误！\n");
		return NULL;
	}
	myhello(n);
	result = PyLong_FromLong(n);
	return result;
}

static PyObject* test_function(PyObject *self)
{
	PyObject_Print(self, stdout, 0);
	printf("hello_world test\n");
	Py_INCREF(Py_True);
	return Py_True;
}

static PyMethodDef hello_world_methods[] = {
	{"test",  (PyCFunction)test_function, METH_NOARGS, "hello_world extending test"},
	{"add",   (PyCFunction)add_function, METH_VARARGS, NULL},
	{"hello", (PyCFunction)hello_function, METH_VARARGS, NULL},
	{NULL, NULL, 0, NULL}
};

static struct PyModuleDef hello_world_module = {
	PyModuleDef_HEAD_INIT,
	"hello_world",        	 /* name of module */
	NULL,                    /* module documentation, may be NULL */
	-1,                      /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
	hello_world_methods   	 /* A pointer to a table of module-level functions, described by PyMethodDef values. Can be NULL if no functions are present. */
};

PyMODINIT_FUNC PyInit_hello_world(void)
{
	PyObject *m;
	m = PyModule_Create(&hello_world_module);
	if (m == NULL)
		return NULL;
	printf("init hello_world module\n");
	return m;
}


