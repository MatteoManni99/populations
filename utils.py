def normalize_coords(coord_x, coord_y, width, height):
    normalized_x = coord_x / width
    normalized_y = coord_y / height
    return normalized_x, normalized_y

def normalize_coord(coord, max_value):
    return coord / max_value

def denormalize_coords(coord_x, coord_y, width, height):
    denormalized_x = coord_x * width
    denormalized_y = coord_y * height
    return denormalized_x, denormalized_y