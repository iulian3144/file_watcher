import os
import logging


class BaseAction:
    def __init__(self, arg):
        pass
    def invoke(self, fullpath: str, event_type: str, is_directory: bool=False):
        item_type = "dir" if is_directory else "file"
        logging.info(f'[{item_type:>4s} {event_type}] path: {fullpath}')


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
        with open(f'{dest}\\{filename}', 'wb') as fout:
            shutil.copyfileobj(fin, fout, 128*1024)

class CopyAction(BaseAction):
    def __init__(self, dest: str):
        if not (os.path.exists(dest) and os.path.isdir(dest)):
            logging.error(f"[CopyAction] Passed argument ({dest}) is not a directory.")
            exit(1)
        self.destination = os.path.abspath(dest)
        logging.info(f"[ACTION] Matched files will be copied to {self.destination}")

    def copy_file(self, fullpath, event_type):
        dirname, filename = os.path.split(fullpath)
        # quiet time
        time.sleep(1)
        logging.info(
            f"Copy: <watch_path>\\{filename} to {self.destination}...")
        t1 = time.time()
        copyfile(fullpath, f'{self.destination}\\{filename}')
        t2 = time.time()
        time_total = t2 - t1

        size_auto = get_size_auto(fullpath)
        logging.info(
            f"Done: <watch_path>\\{filename:40s} [{size_auto}] in {time_total:.3f}ms")


    def invoke(self, fullpath: str, event_type: str, is_directory: bool=False):
        if not is_directory:
            t = threading.Thread(target=self.copy_file, args=(fullpath, event_type))
            t.start()
            logging.debug(f"Thread (tid:{t.ident}) created")