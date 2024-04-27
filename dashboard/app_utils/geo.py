from pyproj import Transformer

def project_bbox(bbox, from_crs, to_crs):
    """
    Project a bounding box from one CRS to another.

    Parameters:
    bbox (tuple or list): The bounding box to project, in the format (minx, miny, maxx, maxy).
    from_crs (str): The current CRS of the bounding box.
    to_crs (str): The CRS to project the bounding box to.

    Returns:
    tuple: The projected bounding box, in the format (minx, miny, maxx, maxy).
    """
    transformer = Transformer.from_crs(from_crs, to_crs)

    minx, miny = transformer.transform(bbox[0], bbox[1])
    maxx, maxy = transformer.transform(bbox[2], bbox[3])

    return (minx, miny, maxx, maxy)