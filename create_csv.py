import matplotlib.pyplot as plt
import tqdm
import os
import numpy as np
import glob
import json
import pandas as pd
import random
import string
import argparse
import pathlib
import shapely.wkt as wkt
import numpy as np
import matplotlib.pyplot as plt
from itertools import chain


def generate_annotations(filename):
    with open(filename, "r") as outf:
        buildings_poly = outf.readlines()
    buildings_poly = [wkt.loads(w) for w in buildings_poly]
    
    XY_points = []
    for each in buildings_poly:
        try:
            xy = np.array(each.exterior.coords)
            XY_points.append(xy)
        except:
            xy = np.array(list(chain.from_iterable(list(each_poly.exterior.coords)[:-1] for each_poly in each)))
        XY_points.append(xy)
    return XY_points


def create_csv():
    parser = argparse.ArgumentParser('create_csv', description='Create Caesar-compatible CSV for PRN data upload')

    parser.add_argument('-d', '--data_folder', type=pathlib.Path, required=True)
    parser.add_argument('-m', '--subject_manifest', type=argparse.FileType('r'), required=True)
    parser.add_argument('--extractor_key', type=str, default='ml_annotation')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default='PRN_automated_annotation.csv')

    args = parser.parse_args()

    masks = sorted(glob.glob(os.path.join(args.data_folder, '*.wkt')))

    manifest = pd.read_csv(args.subject_manifest)

    fileIDs = np.asarray([os.path.splitext(f)[0] for f in manifest.filename])
    subjectIDs = np.asarray(manifest.subject_id)

    assert len(masks) == len(manifest), f"Number of mask images ({len(masks)}) and length of manifest ({len(manifest)}) are different!"

    json_data = []
    for img in tqdm.tqdm(masks, ascii=True, dynamic_ncols=True, desc="Generating annotations"):
        anno = generate_annotations(img)
        subject_id = subjectIDs[np.where(fileIDs == os.path.splitext(os.path.basename(img))[0])[0]][0]
        rowi = {
            'subject_id': subject_id,
            'extractor_key': args.extractor_key
        }
        data = []
        for line in anno:
            markId = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))

            data.append({'pathX': [], 'pathY': [], 'stepKey': 'S0', 'taskIndex': 0, 'taskKey': 'T0', 'toolType': 'freehandLine', 'toolIndex': 0, 'taskType': 'drawing', 'frame': 0, 'markId': markId})

            data[-1]['pathX'] = line[:, 0].tolist()
            data[-1]['pathY'] = line[:, 1].tolist()
        rowi['data'] = json.dumps({"data": data})

        json_data.append(rowi)

    table = pd.DataFrame.from_records(json_data)
    table.to_csv(args.output)
    
if __name__ == '__main__':
    create_csv()