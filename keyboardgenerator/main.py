# import os
from pathlib import Path
from keyboardgenerator.keyboard import Keyboard
import pykle_serial as kle_serial
from solid2.core.object_base import OpenSCADObject
from solid2.extensions.bosl2 import RIGHT
from keyboardgenerator import hardcoded_jsons

import logging as log

FORMAT = "%(message)s"
log.basicConfig(level=log.INFO, format=FORMAT)

OUTPUT_DIR = Path("output")


def _generate_keyboard(
    keyboard_json: kle_serial.Keyboard, mirror: bool = False
) -> (OpenSCADObject, OpenSCADObject, OpenSCADObject):
    log.info("\tGenerate Keyboard Plate")
    keyboard_plate = Keyboard.from_kle_obj(keyboard_json)
    log.info("\tGenerate Keyboard PCB")
    keyboard_pcb = Keyboard.from_kle_obj(keyboard_json)
    log.info("\tGenerate Keyboard Bottom")
    keyboard_bottom = Keyboard.from_kle_obj(keyboard_json)
    log.info("Done creating keyboard\n")
    plate = (
        keyboard_plate.draw_plate()
        if not mirror
        else keyboard_plate.draw_plate().mirror(RIGHT)
    )

    pcb = (
        keyboard_pcb.draw_pcb() if not mirror else keyboard_pcb.draw_pcb().mirror(RIGHT)
    )
    bottom = (
        keyboard_bottom.draw_bottom()
        if not mirror
        else keyboard_bottom.draw_bottom().mirror(RIGHT)
    )

    return plate, pcb, bottom


def _generate_keyboard_openscad_files(
    plate: OpenSCADObject,
    pcb: OpenSCADObject,
    bottom: OpenSCADObject,
    mirror: bool = False,
):
    OUTPUT_DIR.mkdir(exist_ok=True)
    log.info("Saving scad files")

    suffix = ""
    if mirror:
        suffix = "-mirror"

    # PCB
    pcb_openscad_path = (OUTPUT_DIR / f"pcb{suffix}.scad").absolute()
    log.info(f"\tPcb scad file {pcb_openscad_path}")
    pcb.save_as_scad(pcb_openscad_path)

    # Plate
    plate_openscad_path = (OUTPUT_DIR / f"plate{suffix}.scad").absolute()
    log.info(f"\tPlate scad file {plate_openscad_path}")
    plate.save_as_scad(plate_openscad_path)

    # Bottom
    bottom_openscad_path = (OUTPUT_DIR / f"bottom{suffix}.scad").absolute()
    log.info(f"\tBottom scad file {bottom_openscad_path}")
    bottom.save_as_scad(bottom_openscad_path)

    # Keyboard
    keyboard_openscad_path = (OUTPUT_DIR / f"keyboard{suffix}.scad").absolute()
    log.info(
        f"\tKeyboard scad file {keyboard_openscad_path}",
    )
    (pcb.color("gray") + plate.down(40) + bottom.up(40).color("aqua")).save_as_scad(
        keyboard_openscad_path
    )


def _generate_keyboard_stl_files(
    plate: OpenSCADObject, pcb: OpenSCADObject, bottom: OpenSCADObject
):
    OUTPUT_DIR.mkdir(exist_ok=True)
    log.info("Saving stl files")

    # PCB
    pcb_stl_path = (OUTPUT_DIR / "pcb.stl").absolute()
    log.info(f"\tPcb stl file {pcb_stl_path}")
    pcb.save_as_stl(pcb_stl_path)

    # Plate
    plate_stl_path = (OUTPUT_DIR / "plate.stl").absolute()
    log.info(f"\tPlate stl file {plate_stl_path}")
    plate.save_as_stl(plate_stl_path)

    # Bottom
    bottom_stl_path = (OUTPUT_DIR / "bottom.stl").absolute()
    log.info(f"\tBottom stl file {bottom_stl_path}")
    bottom.save_as_stl(bottom_stl_path)

    log.info("Created new scad files")

    print("done")


def main():
    log.info("Creating new keyboard")
    # keyboard_json = hardcoded_jsons.almost_there()
    # keyboard_json = hardcoded_jsons.arduino_only()  # one_board_tez_v4()
    # keyboard_json = hardcoded_jsons.one_board_tez_v4()  # one_board_tez_v4()
    keyboard_json = hardcoded_jsons.one_board_tez_v3()  # one_board_tez_v4()
    plate, pcb, bottom = _generate_keyboard(keyboard_json)
    _generate_keyboard_openscad_files(plate, pcb, bottom)
    if hasattr(keyboard_json.meta, "split") and keyboard_json.meta.split:
        plate, pcb, bottom = _generate_keyboard(keyboard_json, mirror=True)
        _generate_keyboard_openscad_files(plate, pcb, bottom, mirror=True)
    # _generate_keyboard_stl_files(plate, pcb, bottom)

    print("done")


if __name__ == "__main__":
    main()
