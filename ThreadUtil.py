import threading


def get_thread_id():
    return '[Thread Id: ' + str(threading.currentThread().ident) + ']'
