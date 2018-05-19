import  json
from pprint import pprint
from pathlib import Path



def loadJsonFile(location="local", path=None):
    if (location == "local"):
        file_path = Path(path)
        if (file_path.exists()):
            json_template = json.loads(file_path.open().read())
            return json_template
        else:
            print("file {} not found".format(file_path))

