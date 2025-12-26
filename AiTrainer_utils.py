"""Utility functions for AI Trainer.

This module provides helper functions for image processing and calculations.
"""

import cv2


def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    """Resize image while maintaining aspect ratio.
    
    Args:
        image: Input image
        width (int): Target width. If None, calculated from height
        height (int): Target height. If None, calculated from width
        inter: Interpolation method (default: cv2.INTER_AREA)
        
    Returns:
        Resized image
    """
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized


def distanceCalculate(p1, p2):
    """Calculate Euclidean distance between two points.
    
    Args:
        p1 (tuple): Point 1 coordinates (x1, y1)
        p2 (tuple): Point 2 coordinates (x2, y2)
        
    Returns:
        float: Distance between the two points
    """
    dis = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    return dis
