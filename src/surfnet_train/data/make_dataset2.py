from data_processing import get_annotations_from_files, get_annotations_from_db
from data_processing import generate_yolo_files, get_train_valid, build_yolo_annotations_for_images
from pathlib import Path
from sklearn.model_selection import KFold
import pandas as pd
import psycopg2


def main(args):
    data_dir = Path(args.data_dir)
    if args.bbox_filename and args.images_filename:
        df_bboxes, df_images = get_annotations_from_files(data_dir,
                                                        args.bbox_filename,
                                                        args.images_filename)
    elif args.password:
        print("getting annotations from db")
        df_bboxes, df_images = get_annotations_from_db(args.password)
    else:
        print("either a password must be set, or bbox and images filenames")
        return

    yolo_filelist, cpos, cneg = build_yolo_annotations_for_images(data_dir, args.images_dir, df_bboxes, df_images, args.limit_data)
    print(f"found {cpos} valid annotations with images and {cneg} unmatched annotations")
    train_files, val_files = get_train_valid(yolo_filelist, args.split)

    generate_yolo_files(data_dir, train_files, val_files)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Build dataset')
    parser.add_argument('--data-dir', type=str, help="path to main data folder")
    parser.add_argument('--images-dir', type=str, help="path to image folder")
    parser.add_argument('--password', type=str, help="password for connection to DB")
    parser.add_argument('--bbox-filename', type=str, default="")
    parser.add_argument('--images-filename', type=str, default="")
    parser.add_argument('--split', type=float, default=0.85)
    parser.add_argument('--limit-data', type=int, default=0)
    args = parser.parse_args()

    main(args)
