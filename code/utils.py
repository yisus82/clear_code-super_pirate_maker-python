from os import path, walk

import pygame


def import_folder(folder):
    pathname = path.normpath(folder)
    image_surfaces = []
    for dirpath, _, filenames in walk(pathname):
        for filename in sorted(filenames):
            full_path = path.join(dirpath, filename)
            try:
                image_surface = pygame.image.load(full_path).convert_alpha()
                image_surfaces.append(image_surface)
            except pygame.error:
                pass
    return image_surfaces


def import_folder_as_dict(folder):
    pathname = path.normpath(folder)
    image_surfaces = {}
    for dirpath, __, img_files in walk(pathname):
        for image in img_files:
            full_path = path.join(dirpath, image)
            image_surface = pygame.image.load(full_path).convert_alpha()
            image_surfaces[image.split(".")[0]] = image_surface

    return image_surfaces
