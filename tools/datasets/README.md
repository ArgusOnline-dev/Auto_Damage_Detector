Dataset tools
=============

Supervisely → YOLOv8 (detection) converter
------------------------------------------

Input (your uploaded dataset structure):
- data/datasets/archive/Car damages dataset/File1/{img, ann, masks_*}
- data/datasets/archive/Car parts dataset/File1/{img, ann, masks_*} (optional)

Output (YOLOv8-ready detection dataset):
- data/datasets/processed/yolov8_detection/
  - images/{train,val,test}
  - labels/{train,val,test}
  - data.yaml
  - classes.txt

Usage
1) Activate your Python env
2) Run the converter:

```bash
python tools/datasets/convert_supervisely_to_yolov8_detection.py --dataset "Car damages dataset"
```

Options:
- --source: default data/datasets/archive
- --dataset: folder name under --source (e.g., "Car damages dataset")
- --out: default data/datasets/processed
- --split: default "0.7,0.2,0.1"
- --seed: default 42

Notes
- The converter reads polygon annotations and exports bounding boxes for YOLOv8 detection.
- Images with no valid objects are skipped.
- Class ids are assigned alphabetically; see classes.txt and names in data.yaml.


