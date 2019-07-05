import os
import logging
import threading
import shutil
import time


class ActionItem:
    def __init__(self, a_class, a_desc):
        self.a_class = a_class
        self.a_desc = a_desc


class BaseAction:
    def __init__(self, args=[]):
        self.args = args

    def invoke(self, fullpath: str, event_type: str, is_directory: bool = False):
        item_type = "dir" if is_directory else "file"
        logging.info(f'[{item_type:>4s} {event_type}] path: <watch_path>\\{os.path.split(fullpath)[1]}')


# returns file size in KB or MB depending on file size
# if file size is less than 900KB, return size in KB; MB otherwise
def get_size_auto(file: str):
    size = os.path.getsize(file) / (1 << 10)
    if size < 900:
        return f'{size:6.2f}KB'
    size = size / (1 << 10)
    return f'{size:6.2f}MB'


# copy a source file to a destination
# destination must represent a file
def copyfile(src: str, dest: str):
    if os.path.isdir(dest):
        return
    with open(src, 'rb') as fin:
        with open(dest, 'wb') as fout:
            shutil.copyfileobj(fin, fout, 128*1024)


class CopyAction(BaseAction):
    def __init__(self, args):
        super().__init__(args)
        dest = self.args[0]
        self.dst_path = os.path.abspath(dest)
        logging.info(
            f"[{self.__class__.__name__}] Matched files will be copied to {self.dst_path}")

    def copy_file(self, fullpath):
        dirname, filename = os.path.split(fullpath)
        # quiet time
        time.sleep(1)
        path_ok = True
        if not os.path.exists(self.dst_path):
            logging.error(
                f"[{self.__class__.__name__}] Destination path ({self.dst_path}) does not exist.")
            path_ok = False
        if path_ok and not os.path.isdir(self.dst_path):
            logging.error(
                f"[{self.__class__.__name__}] Destination path ({self.dst_path}) is not a directory.")
            path_ok = False

        if not path_ok:
            logging.warning(f"[{self.__class__.__name__}] File '{filename}' will not be copied due to errors.")
            return 1

        logging.info(
            f"Copy START: <watch_path>\\{filename:40s} -> {self.dst_path}...")
        t1 = time.perf_counter()
        dest_filename = os.path.join(self.dst_path, filename)
        copyfile(fullpath, dest_filename)
        t2 = time.perf_counter()
        time_total = t2 - t1

        size_auto = get_size_auto(fullpath)
        logging.info(
            f" Copy DONE: <watch_path>\\{filename:40s} [{size_auto} in {time_total:.3f}s]")

    def invoke(self, fullpath: str, event_type: str, is_directory: bool = False):
        if not is_directory:
            t = threading.Thread(target=self.copy_file, args=(fullpath,))
            t.start()
            logging.debug(f"Thread (tid:{t.ident}) created")


ACTION_LIST = {
    'default': ActionItem(BaseAction, "echoes file path"),
    'copy': ActionItem(CopyAction, "copy files to the directory specified by <action_arg>")
}
