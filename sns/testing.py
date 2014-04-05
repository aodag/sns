from dogpile.cache.backends.file import AbstractFileLock


class FakeLock(AbstractFileLock):
    def __init__(self, *args, **kwargs):
        pass

    def acquire_write_lock(self, *args, **kwargs):
        pass

    def release_write_lock(self, *args, **kwargs):
        pass

    def acquire_read_lock(self, *args, **kwargs):
        pass

    def release_read_lock(self, *args, **kwargs):
        pass
