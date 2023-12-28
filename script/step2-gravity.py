#!/usr/bin/env python

# Usage: $0 SPRITES_DIR LIST_OF_REGIONS_TXT BACKGROUND
# SPRITES_DIR shall have 
# - dynamic_%d.png
# - fixed_%d.png

import sys
from dataclasses import dataclass
from pathlib import Path
import builtins
import math

# HACK?
from PIL import (
        Image,
        ImageFilter)
import numpy as np

import pygame
import pymunk
import pymunk.autogeometry
import pymunk.pygame_util

from lib.parse_listof_regions import *
from lib.generate_geometry import *

# PARAMS
THRESHOLD = 130
GRAVITY = (0.0, 9.8*100*1e-1) # top-left is (0, 0) x>0 when go right, y>0 when go down
FPS: float = 30
LETTER_MASS: float = 1
#DEBUG: bool = True
DEBUG: bool = False
DURATION_S: float = 10
DO_SAVE_IMAGE: bool = True

OUTPUT_DIR: Path = Path("VideoFrames")

# lazy argument
_, sprites_dir, list_regions_file, background_file, *_ = sys.argv

# Background plz.
background_img = pygame.image.load(background_file)
background_size = background_img.get_size()

# Pygame init.
pygame.init()
screen = pygame.display.set_mode(background_size)
clock = pygame.time.Clock()
running = True

# Pymunk init.
space = pymunk.Space()
space.gravity = GRAVITY
space.sleep_time_threshold = 0.3

draw_options = pymunk.pygame_util.DrawOptions(screen)
pymunk.pygame_util.positive_y_is_up = False

# Text file plz.
regions = parse_listof_regions(list_regions_file)
dynamic_regions = regions["DYNAMIC"]
fixed_regions = regions["FIXED"]

# And now what should I do?

fixed_sprites = []

# For each image, let's make fixed body.
digits = fixed_regions.__len__().__sub__(1).__str__().__len__()
for idx, [x1, y1, w, h] in enumerate(fixed_regions):
    if not DEBUG:
        print = lambda *_, **__: None

    # Load image.
    image_filename = f"fixed_{idx:0{digits}}.png"
    #print(f"{sys.argv[0]}: opening {image_filename!r}", file=sys.stderr)
    image = pygame.image.load(Path(sprites_dir, image_filename))

    fixed_sprites.append((image, x1, y1))

    line_set: pymunk.autogeometry.PolylineSet = generate_line_set(image)

    for line in line_set:
        line = pymunk.autogeometry.simplify_curves(line, 0.7)

        for (a, b) in zip(line, line[1:]):
            body = pymunk.Body(0, 0, pymunk.Body.STATIC)
            body.position = x1, y1 # In pygame they need to be int.
            body.position = pymunk.pygame_util.to_pygame(body.position, screen)

            shape = pymunk.Segment(body, a, b, radius=1)
            shape.friction = 0.5
            #shape.color = 255, 255, 255, 255

            # finally
            space.add(body, shape)

if not DEBUG:
    print = builtins.print

@dataclass
class RigidWithSprite:
    body: pymunk.Body
    shape: pymunk.Shape
    image: pygame.image

rigids_with_sprite: list[RigidWithSprite] = []

# For each image, let's make RigidWithSprite.
digits = dynamic_regions.__len__().__sub__(1).__str__().__len__()
for idx, [x1, y1, w, h] in enumerate(dynamic_regions):
    if not DEBUG:
        print = lambda *_, **__: None

    # Load image.
    image_filename = f"dynamic_{idx:0{digits}}.png"
    print(f"{sys.argv[0]}: opening {image_filename!r}", file=sys.stderr)
    image = pygame.image.load(Path(sprites_dir, image_filename))

    line_set: pymunk.autogeometry.PolylineSet = generate_line_set(image)

    # needs to be put the vertices around (0, 0) or glitches.
    # URL: https://www.pymunk.org/en/latest/pymunk.html#pymunk.Poly.__init__
    move_to_0_0 = pymunk.Transform(tx=-image.get_width()/2.0, ty=-image.get_height()/2.0)
    #move_to_0_0 = pymunk.Transform(tx=0, ty=0)

    # The shapes are polygons.
    polygons = [pymunk.Poly(None, vs, transform=move_to_0_0)
                for vs in line_set]

    # Things to calculate for bodies.
    areas = [polygon.area for polygon in polygons]
    sum_areas = sum(areas)
    masses = [LETTER_MASS*(area/sum_areas) for area in areas]
    moments = [pymunk.moment_for_poly(LETTER_MASS, vs) for vs in line_set]

    # Yes, bodies are there.
    bodies = [pymunk.Body(mass, moment) for mass, moment in zip(masses, moments)]
    [[body.__setattr__("position", (x1, y1)),
      polygon.__setattr__("body", body)]
     for polygon, body in zip(polygons, bodies)]

    # I want parts of one letter should be treated as one body and shape,
    # like "で", which is a PolylineSet of "て" and "゛".
    constraints = [
            pymunk.constraints.PinJoint(a, b, anchor, anchor)
            for a, b in zip(bodies, bodies[1:])
            for anchor in [(0, 0), (w, h)]]

    space.add(*bodies, *polygons, *constraints)


    if not DEBUG:
        print = builtins.print

    # Finally.
    my_rigit_with_sprite = RigidWithSprite(bodies[0], polygons[0], image)
    rigids_with_sprite.append(my_rigit_with_sprite)

#exit(0)

# Video output property
necessary_frames = FPS * DURATION_S
digits = necessary_frames.__str__().__len__()

if not OUTPUT_DIR.is_dir():
    print(f"mkdir {OUTPUT_DIR}", file=sys.stderr)
    OUTPUT_DIR.mkdir()

# Finally pygame loop

for i_frame in range(necessary_frames):
#while True:
    for event in pygame.event.get():
        # exiter
        if any([
                event.type == pygame.QUIT,
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE,
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
                ]):
            sys.exit(0)

    space.step(1.0 / FPS)

    # == View of MVC.
    # background.
    screen.blit(background_img, (0, 0))
    
    # HELP
    if DEBUG:
        space.debug_draw(draw_options)

    [screen.blit(fixed_img, (x, y)) for fixed_img, x, y in fixed_sprites]
    [screen.blit(dynamic_img, (x, y))
     for rigid_with_sprite in rigids_with_sprite
     for _img in [rigid_with_sprite.image]
     for body in [rigid_with_sprite.body]
     for dynamic_img in [pygame.transform.rotate(_img, math.degrees(body.angle))]
     for offset in [pymunk.Vec2d(*dynamic_img.get_size())/2]
     for p in [body.position - offset]
     for x, y in [p]]

    # Finally of view.
    pygame.display.flip()

    # and saving the frame.
    if DO_SAVE_IMAGE:
        output_file = Path(OUTPUT_DIR, f"frame{i_frame:0{digits}}.png")
        pygame.image.save(screen, output_file)

    # Finally
    clock.tick(FPS)
