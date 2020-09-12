import threading


def get_thread_id():
    return '[Thread-' + str(threading.currentThread().ident) + ']'

def get_thread_id_order(thread_order):
    return '[Thread Order-' + thread_order + ' id-' + str(threading.currentThread().ident) + ']'