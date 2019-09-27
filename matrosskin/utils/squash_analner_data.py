import os
from analner.utils.dropbox_sync import DropboxSync
from analner.utils.squash import Squasher

if __name__ == "__main__":
    data_path = os.environ.get('DATA_PATH')
    if not data_path:
        raise Exception("Please setup path to storing data [data_path] var")

    token = os.environ.get('DROPBOX_TOKEN')
    if not token:
        raise Exception("Please add DROPBOX_TOKEN to environment vars")
    db_sync = DropboxSync(token)

    squasher = Squasher(data_path, db_sync)
    squasher.run()
