import fileinput
import re
import copy

__all__ = ["parse_listof_regions"]

def parse_listof_regions(txt_file) -> dict[str, list[int, int, int, int]]:
    """
    @output Four columns of: [x1, x2, w, h]
    Keys are DYNAMIC and FIXED
    """

    mode: str = ""
    previous_value: list[int] = [None, None, None, None]
    my_keywords: set[str] = {
            "DYNAMIC",
            "FIXED",
            }
    regions: dict[str, list[int]] = {
            kwd: [] for kwd in my_keywords
            }

    for line in fileinput.input(files=[txt_file]):
        cols = line.split()

        # comment?
        if len(cols) == 0 or cols[0][0] == "#":
            continue

        # change mode
        if cols[0][0:2] == "__" and cols[0][-2:] == "__":
            mode = cols[0][2:-2]

            if mode not in my_keywords:
                raise KeyError(f"{txt_file}, line {fileinput.lineno()}: got {mode}, mode keyword must be one of {my_keywords}")

            continue

        # finally actual value
        value = copy.deepcopy(previous_value)
        for idx, val in enumerate(cols[:4]):
            value[idx] = int(val)
        regions[mode].append(value)

        # last but not least
        previous_value = value

    return regions

