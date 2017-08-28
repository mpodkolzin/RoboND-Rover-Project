import numpy as np
import cv2

np.set_printoptions(threshold=np.nan)
dst_size = 5
bottom_offset = 6
source = np.float32([[14, 140], [301, 140], [200, 96], [118, 96]])

img_size = (160, 320)

destination = np.float32([[img_size[1]/2 - dst_size, img_size[0] - bottom_offset],
                  [img_size[1]/2 + dst_size, img_size[0] - bottom_offset],
                  [img_size[1]/2 + dst_size, img_size[0] - 2 * dst_size - bottom_offset], 
                  [img_size[1]/2 - dst_size, img_size[0] - 2 * dst_size - bottom_offset],
                  ])


# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only

def color_thresh(img, low_thresh=(160, 160, 160), high_thresh=(255, 255, 255)):

    color_select = np.zeros_like(img[:, :, 0])

    thresh = ((img[:, :, 0] >= low_thresh[0]) & (img[:, :, 0] <= high_thresh[0]))\
                & ((img[:, :, 1] >= low_thresh[1]) & (img[:, :, 1] <= high_thresh[1])) \
                & ((img[:, :, 2] >= low_thresh[2]) & (img[:, :, 2] <= high_thresh[2]))
    color_select[thresh] = 1
    return color_select


# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

def to_cartesian_coords(dists, angles):
    x_pix = dists * np.cos(angles)
    y_pix = dists * np.sin(angles)
    return x_pix, y_pix


# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale):
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped

def rotate_image(image, angle):
    center = tuple(np.array(image.shape[0:2])/2)
    rot_mat = cv2.getRotationMatrix2D(center,angle,1.0)
    return cv2.warpAffine(image, rot_mat,
             image.shape[0:2],flags=cv2.INTER_LINEAR)


def get_visited_map(fidelity):
    visited = np.zeros_like(fidelity)
    weights = fidelity > 30
    visited[weights] = 1
    return visited
    


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):



    warped_navigable = perspect_transform(Rover.img, source, destination)
    threshed_navigable = color_thresh(warped_navigable, (160, 160, 160))
    #if Rover.roll > 0:
    #    print('rotating image')
    #    angle = Rover.roll % 360-360
    #    Rover.img = rotate_image(Rover.img, -angle)
    #if Rover.roll > 0:
    #    print('rotating image')
    #    threshed_navigable = rotate_image(threshed_navigable, -Rover.roll)
    threshed_rock = color_thresh(warped_navigable, (120, 100, 0), (250, 200, 90))
    threshed_rock = color_thresh(warped_navigable, (100, 100, 20), (255, 255, 30))
    threshed_obstacle = np.logical_not(threshed_navigable).astype(np.int)


    #Update rover vision

    Rover.vision_image[:, :, 0] = threshed_obstacle * 200
    Rover.vision_image[:, :, 1] = threshed_rock * 200
    Rover.vision_image[:, :, 2] = threshed_navigable * 200

    xpix, ypix = rover_coords(threshed_navigable)
    x_obst_pix, y_obst_pix = rover_coords(threshed_obstacle)
    x_rock_pix, y_rock_pix = rover_coords(threshed_rock)
    

    
    x_world_obst, y_world_obst = pix_to_world(x_obst_pix, y_obst_pix, Rover.pos[0], Rover.pos[1], Rover.yaw, 200, 10)
    x_world_rock, y_world_rock = pix_to_world(x_rock_pix, y_rock_pix, Rover.pos[0], Rover.pos[1], Rover.yaw, 200, 10)
    x_world, y_world = pix_to_world(xpix, ypix, Rover.pos[0], Rover.pos[1], Rover.yaw, 200, 10)

    
    x_vis = np.floor_divide(Rover.pos[0],10).astype(np.int)
    y_vis = np.floor_divide(Rover.pos[1],10).astype(np.int)
    
    Rover.visited_map[y_vis, x_vis] += 1
    Rover.worldmap[y_world_rock, x_world_rock, 1] += 1
    #Update rover worldmap
    if((-1 <= (Rover.roll % 360-360) <= 1) and (-1 <= (Rover.pitch % 360-360) <= 1)):
    #if -1 <= (Rover.pitch % 360-360) <= 1:
        Rover.worldmap[y_world, x_world, 2] += 1
        Rover.worldmap[y_world_obst, x_world_obst, 0] += 1




    dists, angles = to_polar_coords(xpix, ypix)
    fidelity = Rover.worldmap[y_world, x_world, 2]
    #visited = get_visited_map(fidelity)
    #print(visited)

    weights = np.dstack((dists, angles, fidelity))
    Rover.direction_weights = weights[0,:,:]
    #res = weights[0,:,:]
    #res2 = res[res[:,1].argsort()]
    #print(res2)

    rock_dists, rock_angles = to_polar_coords(x_rock_pix, y_rock_pix)

    Rover.sample_angles = rock_angles
    Rover.sample_dists = rock_dists
    


    Rover.nav_dists = dists
    Rover.nav_angles = angles

 
    
    
    return Rover
