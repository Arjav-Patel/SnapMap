import sys

from os import listdir, remove
from os.path import isfile, join

import argparse
from tqdm import tqdm

import cv2
import numpy as np

#######################################

def overlap(pt, width, height, other_pt):
    # other_pt is inside the rectangle with pt as its top-left corner
    if (pt[0] < other_pt[0] and
        other_pt[0] < pt[0] + width and
        pt[1] < other_pt[1] and
        other_pt[1] < pt[1] + height):
        return True
    # pt and other point have the same x-coord
    elif (pt[0] == other_pt[0] and
        pt[1] < other_pt[1] and
        other_pt[1] < pt[1] + height):
        return True
    # pt and other point have the same y-coord
    elif (pt[1] == other_pt[1] and
        pt[0] < other_pt[0] and
        other_pt[0] < pt[0] + width):
        return True
    else:
        return False



def template_match(img, template, method, threshold):
    # Get template properties
    template_height, template_width = template.shape[:2]

    # Match template to img
    res = cv2.matchTemplate(img, template, method)
    
    # Select all locations which have a template-match-likelihood greater than threshold
    loc = np.where( res >= threshold)
    # loc is a list of pts (x, y), sorted by their x-coords
    loc = [pt for pt in zip(loc[1], loc[0])]
    
    # Remove overlapping template matches (this occurs when template is uniform)
    remove = set()
    for i, pt in enumerate(loc):
        
        if i in remove:
            continue
            
        for j, other_pt in enumerate(loc):
            if j > i and overlap(pt, template_width, template_height, other_pt):
                remove.add(j)            
    
    return [pt for i, pt in enumerate(loc) if not i in remove]



def multiscale_template_match(img, template, method, threshold):
    # Get img, template properties
    img_height, img_width = img.shape[:2]
    template_height, template_width = template.shape[:2]
    
    locs = []
    # 16 is the lowest pixel height/width that template will be resized to, and img_width is the greatest
    for i in tqdm(range(16, img_width)):
        scale = i / template_width
        if scale < 1:
            # cv2.INTER_AREA is better when scale < 1
            resized_template = cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        else:
            # cv2.INTER_CUBIC is better when scale > 1
            resized_template = cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        # Get resized_template properties
        resized_template_height, resized_template_width = resized_template.shape[:2]
        
        # Template is bigger than img
        if (resized_template_width >= img_width or
            resized_template_height >= img_height):
            break

        # Select all locations which have a template-match-likelihood greater than threshold
        loc = template_match(img, resized_template, method, threshold)

        locs.append(
            (len(loc),
             scale,
             resized_template,
             loc)
        )
    
    # Return loc with most pts (greatest len)
    return max(locs)



def save_matched_template_as_img(img, template, loc, save, color, thickness):
    template_height, template_width = template.shape[:2]
    
    for pt in loc:
        cv2.rectangle(img, pt, (pt[0] + template_width, pt[1] + template_height), color, thickness)

    cv2.imwrite(save, img)


def save_matched_template_as_txt(img, template, template_file, loc, save):
    # Get img, template properties
    img_height, img_width = img.shape[:2]
    template_height, template_width = template.shape[:2]

    # Save to file
    with open(save, 'a') as f:
        for pt in loc:
            # Extra variables for compatability with Unity
            f.write('{} {} {} {} {} {} {} {} {} {}\n'.format(
                template_file,                          # file
                pt[0],                                  # x
                img_height - template_height - pt[1],   # y
                0,                                      # z
                0,                                      # x_rot
                90,                                     # y_rot
                0,                                      # z_rot
                template_width,                         # width
                template_height,                        # height
                template_width,                         # depth
            ))

def main(levels_path, sprites_path, data_path, multiscale):
    # Acceptable image types
    image_types = set(['jpg', 'jpeg', 'png', 'tif', 'gif'])

    # Get all level images, ignore .meta files (they are for Unity)
    levels = [level for level in listdir(levels_path) 
                   if isfile(join(levels_path, level))
                   and level.split('.')[-1] in image_types]
    
    # Get all sprite images, ignore .meta files (they are for Unity)
    sprites = [sprite for sprite in listdir(sprites_path) 
               if isfile(join(sprites_path, sprite)) 
               and sprite.split('.')[-1] in image_types]
    
    for level in levels:
        # Load level image
        level_name = level.split('.')[0]
        level_img = cv2.imread(join(levels_path, level))
        
        # Remove saved data if it exists
        if isfile(join(data_path, level_name + '.txt')):
            remove(join(data_path, level_name + '.txt'))

        # Keep track of min sprite width to allow rescaling of GameObjects in Unity
        min_sprite_width = float('inf')
        for sprite in tqdm(sprites):
            # Load sprite image
            sprite_img = cv2.imread(join(sprites_path, sprite))
            # Get sprite properties
            sprite_height, sprite_width = sprite_img.shape[:2]

            if sprite_width < min_sprite_width:
                min_sprite_width = sprite_width
            
            loc = template_match(level_img, sprite_img, cv2.TM_CCOEFF_NORMED, 0.8)
            if loc:
                save_matched_template_as_txt(level_img, sprite_img, sprite, loc, join(data_path, level_name + '.txt'))

                save_matched_template_as_img(level_img, sprite_img, loc, join(levels_path, 'Templates', level), (0, 0, 255), 1)
            elif multiscale:
                _, scale, sprite_img, loc = multiscale_template_match(level_img, sprite_img, cv2.TM_CCOEFF_NORMED, 0.8)

                if loc:
                    save_matched_template_as_txt(level_img, sprite_img, sprite, loc, join(data_path, level_name + '.txt'))

                    save_matched_template_as_img(level_img, sprite_img, loc, join(levels_path, 'Templates', level), (0, 0, 255), 1)
        




def entrypoint(levels_path, sprites_path, data_path, multiscale):
    main(levels_path, sprites_path, data_path, multiscale)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--levels_path", default='./Assets/Resources/Levels/')
    parser.add_argument("--sprites_path", default='./Assets/Resources/Sprites/')
    parser.add_argument('--data_path', default='./Assets/Data/')
    parser.add_argument('--multiscale', default=False)


    args = parser.parse_args()
    
    entrypoint(args.levels_path, args.sprites_path, args.data_path, args.multiscale)


