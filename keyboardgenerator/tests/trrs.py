#!/usr/bin/env python3
from solid2.extensions.bosl2 import cube, BOTTOM, cylinder, FWD


port2 = cylinder(d=5, h=2.2, anchor=BOTTOM).rotateX(90)
port = cube([6, 12.2, 5], anchor=FWD)
final_port = port + port2
final_port.save_as_scad(filename="port.scad")
