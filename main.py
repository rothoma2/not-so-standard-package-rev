import json
import os
from util import Util
from machine_learning.ml_model import Model
from pprint import pprint

def main():
    #processing file
    util = Util()
    util.folder_exists()

    top_python_files = util.list_python_files()

    for python_file in top_python_files:

        results = util.generate_features([python_file])

        #ML model
        ml_results = []
        for result in results:
            model = Model(json.dumps(result))
            print(model.predict())
        

if __name__ == "__main__":
    main()