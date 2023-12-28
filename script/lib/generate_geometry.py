import sys

import pygame
import pymunk
import pymunk.autogeometry

__all__ = ["generate_line_set"]

def generate_line_set(image: pygame.Surface) -> pymunk.autogeometry.PolylineSet:
    bb = pymunk.BB(0, 0, *image.get_size())

    # param for march_soft
    width, height = image.get_size()
    threshold = 99
    def sample_func(point):
        try:
            p = pymunk.pygame_util.to_pygame(point, image)
            color = image.get_at(p)
            return color.a
        except:
            return 0

    image.lock()
    line_set = pymunk.autogeometry.march_hard(
            bb, width, height, threshold, sample_func)
    image.unlock()

    #print([pymunk.autogeometry.is_closed(vs) for vs in line_set]) # True for every image for every item in given item
    #print(pymunk.autogeometry.is_closed([[float(x) for x in v] for vs in line_set for v in vs])) # -> False for some images

    return line_set


'''
def generate_geometry(surface, space):
    for s in space.shapes:
        if hasattr(s, "generated") and s.generated:
            space.remove(s)

    # params for march_soft
    x_samples, y_samples = 60, 60
    threshold = 90

    # also param for march_soft
    def sample_func(point):
        try:
            p = [int(x_i) for x_i in point]
            color = surface.get_at(p)
            return color.hsla[2] # use lightness
        except Exception as e:
            print(e, file=sys.stderr)
            return 0

    # finally
    line_set = pymunk.autogeometry.march_soft(
            BB(0, 0, 599, 599), x_samples, y_samples, threshold, sample_func)

    # Now generating.
    for polyline in line_set:
        line = pymunk.autogeometry.symplify_curves(polyline, 1.0)

        # Adding segments.
        for i in range(len(line) - 1):
            p1, p2 = line[i:i+2]
            shape = pymunk.Segment(space.static_body, p1, p2, 1)
            shape.friction = 0.5
            shape.color = pygame.Color("red")
            shape.generated = True
            space.add(shape)
'''
