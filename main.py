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
    template_height, template_width = template.shape[:2]

    res = cv2.matchTemplate(img, template, method)
    
    loc = np.where( res >= threshold)
    loc = [pt for pt in zip(loc[1], loc[0])]
    
    remove = set()
    for i, pt in enumerate(loc):
        
        if i in remove:
            continue
            
        for j, other_pt in enumerate(loc):
            if j > i and overlap(pt, template_width, template_height, other_pt):
                remove.add(j)            
    
    return [pt for i, pt in enumerate(loc) if not i in remove]



def multiscale_template_match(img, template, method, threshold):
    img_height, img_width = img.shape[:2]
        
    template_height, template_width = template.shape[:2]
    
    locs = []
    for i in tqdm(range(16, img_width)):
        scale = i / template_width
        if scale < 1:
            resized_template = cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        else:
            resized_template = cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        resized_template_height, resized_template_width = resized_template.shape[:2]
        
        if (resized_template_width >= img_width or
            resized_template_height >= img_height):
            break

        loc = template_match(img, resized_template, method, threshold)

        locs.append(
            (len(loc),
             scale,
             resized_template,
             loc)
        )
    
    return max(locs)



def save_matched_template_as_img(img, template, loc, save, color, thickness):
    template_height, template_width = template.shape[:2]
    
    for pt in loc:
        cv2.rectangle(img, pt, (pt[0] + template_width, pt[1] + template_height), color, thickness)

    cv2.imwrite(save, img)


def save_matched_template_as_txt(img, template, template_name, loc, save):
    img_height, img_width = img.shape[:2]
    template_height, template_width = template.shape[:2]

    with open(save, 'a') as f:
        for pt in loc:
            f.write('{} {} {} {} {}\n'.format(
                template_name,
                pt[0],
                img_height - template_height - pt[1],
                template_width,
                template_height
            ))

def main(levels_path, sprites_path, data_path, multiscale):
    image_types = set(['jpg', 'jpeg', 'png', 'tif', 'gif'])

    levels = [level for level in listdir(levels_path) 
                   if isfile(join(levels_path, level))
                   and level.split('.')[-1] in image_types]
    
    sprites = [sprite for sprite in listdir(sprites_path) 
               if isfile(join(sprites_path, sprite)) 
               and sprite.split('.')[-1] in image_types]
    
    for level in levels:
        level_name = level.split('.')[0]
        level_img = cv2.imread(join(levels_path, level))
        
        if isfile(join(data_path, level_name + '.txt')):
            remove(join(data_path, level_name + '.txt'))

        for sprite in tqdm(sprites):
            sprite_img = cv2.imread(join(sprites_path, sprite))
            
            loc = template_match(level_img, sprite_img, cv2.TM_CCOEFF_NORMED, 0.8)
            if loc:
                save_matched_template_as_txt(level_img, sprite_img, sprite, loc, join(data_path, level_name + '.txt'))

                save_matched_template_as_img(level_img, sprite_img, loc, join(levels_path, 'Templates', level), (255, 0, 0), 1)
            elif multiscale:
                _, scale, sprite_img, loc = multiscale_template_match(level_img, sprite_img, cv2.TM_CCOEFF_NORMED, 0.8)

                if loc:
                    save_matched_template_as_txt(level_img, sprite_img, sprite, loc, join(data_path, level_name + '.txt'))
                    



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


