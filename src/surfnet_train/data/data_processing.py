from matplotlib import image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
from pycocotools.coco import COCO
from PIL import Image, ImageDraw, ImageFont, ExifTags
import os
import cv2
import pandas as pd



def coco2yolo(bbox:list, image_height:int=1080, image_width:int=1080):
    
    """Function to normalize the representation of the bounding box, such that there are in the yolo format (normalized)

    Args:
        bbox (list): Coordinates of the bounding box : x, y, w and h coordiates.
        image_height (int, optional): Height of the image. Defaults to 1080.
        image_width (int, optional): Width of the image. Defaults to 1080.

    Returns: Normalized bounding box coordinates : values between 0-1.
        _type_: array 
    """
    
    bbox = bbox.copy().astype(float) # otherwise all value will be 0 as voc_pascal dtype is np.int

    bbox[[0, 2]] = bbox[[0, 2]]/ image_width
    bbox[[1, 3]] = bbox[[1, 3]]/ image_height
    
    bbox[[0, 1]] = bbox[[0, 1]] + bbox[[2, 3]]/2
    
    return bbox




def plot_image_and_bboxes(img, anns, ratio:float):

    """ Plots the image and the bounding box(es) associated to the detected object(s). 

    Args:
        img (): Image, from the instance file.
        anns (): Annotations linked to the specified image, from instance file. 
        ratio (float): Ratio - most often defined at the (1080/height of the image). 
    """
    fig, ax = plt.subplots(1, figsize=(12, 10))
    ax.imshow(img) 
    
    for ann in anns:
        
        [bbox_x, bbox_y, bbox_w, bbox_h] = (ratio*np.array(ann['bbox'])).astype(int)
        # Obtains the new coordinates of the bboxes - normalized via the ratio. 
        rect = patches.Rectangle((bbox_x, bbox_y), bbox_w, bbox_h, linewidth=2, edgecolor='r', facecolor="none")
        ax.add_patch(rect)
    
    plt.show()
    # Prints out a 12 * 10 image with bounding box(es). 




def get_df_train_val(annotation_file, data_dir, df_images):

    """Transforms the labels and images to the same format in order to be used by the Yolov5 algorithm. 
  
    Args: 
        annotation_file (json instances file): Annotation file which contains information on the images, 
        the annotations (labels) and categories of the labels. 
        data_dir (file): File with the images. Default to images2labels.
        df_images (data frame): = pd.read_csv("images_for_labelling_202201241120.csv"))

    Returns:
        my_df (data frame): Data frame with columns : old_path, date, view, quality, context, img_name,
        label_name, image and bounding box. 
    """
    
    coco = COCO(annotation_file) # transform the file using a coco function where the COCO function 
                                 # loads a coco annotation file and prepares data structures 
    # gives the annotations into a coco api form ; helps the user in extracting annotations conveniently

    img_ids = np.array(coco.getImgIds()) # creates an array with the images IDs processed by coco
    
    my_df = path_existance(img_ids, data_dir, coco, df_images) # calls function

    return (my_df)




def image_orientation (image:image):

    """ Function which gives the images that have a specified orientation the same orientation.
        If the image does not have an orientation, the image is not altered. 

     Args:
        image (image): Image that is in the path data_directory as well as in the instance json files. 

    Returns: Image, with the proper orientation. 
            _type_: image
    """

    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        exif = image._getexif()
        if exif is not None:
            if exif[orientation] == 3:
                image=image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image=image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image=image.rotate(90, expand=True)

    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass

    return (image)




def shaping_bboxes(anns:list, ratio:float, target_h:float, target_w:int):

    """Function in charge of shaping the bounding boxes, normalized via the coco2yolo function.

    Args:
        anns (list): List with ID of the label, ID of the image, bounding box coordinates and the category ID
        ratio (float): Ratio of the target (1080) and the actual height of the image. (defined in path_existance)
        target_h (float): The target height of the image. (defined in path_existance)
        target_w (float): The target width of the image: (ratio*width of actual image). (defined in path_existance)
    
    Returns: yolo_annot a list with the coordinates of the bboxes and their associated label. 
        _type_: list
    """
    yolo_annot = []

    for ann in anns:
        cat = ann['category_id'] - 1 # gets the actual categories, according to the initial yaml 
        [bbox_x, bbox_y, bbox_w, bbox_h] = (ratio*np.array(ann['bbox'])).astype(int) 
        # gets the bboxes coordinates * the ratio = (1080 /height of the image)
        bbox = np.array([bbox_x, bbox_y, bbox_w, bbox_h]) # creates array with the bboxes coordinates 
        yolo_bbox = coco2yolo(bbox, target_h, target_w) # calls coco2yolo function to normalize the coordinates 
        yolo_str  = str(cat) + " " + " ".join(yolo_bbox.astype(str)) 
        # gives the category of the label and the coordinates of the bboxes 
        yolo_annot.append(yolo_str)

    return(yolo_annot)
    # list with the coordinates of the bboxes and their associated label



def get_date(df_train_valid):

    """_summary_

    Args: 
        df_train_valid (data frame): dataframe obtained using the get_df_train_val 
    Returns:
        _type_: _description_
    """
    d = df_train_valid.iloc[0]["date"] # we take the date column 
                                        # of shape YYYY-MM-DD HH:MM:SS
    d = d.date() # puts our d into a date instance
    day =  int("".join(str(d).split("-"))) # seperates at the - and then joins the rest : YYYYMMDD
    df_train_valid["day"] = day

    return(df_train_valid)