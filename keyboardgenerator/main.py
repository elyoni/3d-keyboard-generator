import pykle_serial as kle_serial
import os


# from keyboardgenerator.base import Keyboard
from keyboardgenerator.keyboard import Keyboard


#
def main():
    keyboard_json = get_arcade_print()
    keyboard_plate = Keyboard.from_kle_obj(keyboard_json)
    keyboard_pcb = Keyboard.from_kle_obj(keyboard_json)
    keyboard_bottom = Keyboard.from_kle_obj(keyboard_json)

    pcb = keyboard_pcb.draw_pcb()
    plate = keyboard_plate.draw_plate()
    bottom = keyboard_bottom.draw_bottom()

    os.makedirs("output", exist_ok=True)

    pcb.save_as_scad(os.path.join("output", "pcb.scad"))
    plate.save_as_scad(os.path.join("output", "plate.scad"))
    bottom.save_as_scad(os.path.join("output", "bottom.scad"))

    # pcb.save_as_stl("pcb.stl")
    # plate.save_as_stl("plate.stl")
    # bottom.save_as_stl("bottom.stl")

    # (pcb + plate + bottom).save_as_scad("keyboard.scad")
    # .save_as_scad("pcb.scad")
    # keyboard_bottom.draw_bottom().save_as_scad("bottom.scad")

    (pcb.color("gray") + plate.down(40) + bottom.up(40).color("aqua")).save_as_scad(
        os.path.join("output", "keyboard.scad")
    )
    print("Created new scad files")

    print("\tPcb scad file", os.path.abspath(os.path.join("output", "pcb.scad")))
    print("\tPlate scad file", os.path.abspath(os.path.join("output", "plate.scad")))
    print("\tBottom scad file", os.path.abspath(os.path.join("output", "bottom.scad")))
    print()
    print(
        "\tKeyboard scad file", os.path.abspath(os.path.join("output", "keyboard.scad"))
    )

    print("done")


def get_json_const_ergodox() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        """[
[{x:3.5},"#\\n3",{x:10.5},"*\\n8"],
[{y:-0.875,x:2.5},"@\\n2",{x:1},"$\\n4",{x:8.5},"&\\n7",{x:1},"(\\n9"],
[{y:-0.875,x:5.5},"%\\n5","LS0",{x:4.5},"RS0","^\\n6"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"!\\n1",{x:14.5},")\\n0",{a:7,w:1.5},""],
[{y:-0.375,x:3.5,a:4},"E",{x:10.5},"I"],
[{y:-0.875,x:2.5},"W",{x:1},"R",{x:8.5},"U",{x:1},"O"],
[{y:-0.875,x:5.5},"T",{h:1.5},"LS1",{x:4.5,h:1.5},"RS1","Y"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"Q",{x:14.5},"P",{a:7,w:1.5},""],
[{y:-0.375,x:3.5,a:4},"D",{x:10.5},"K"],
[{y:-0.875,x:2.5},"S",{x:1},"F",{x:8.5},"J",{x:1},"L"],
[{y:-0.875,x:5.5},"G",{x:6.5},"H"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"A",{x:14.5},":\\n;",{a:7,w:1.5},""],
[{y:-0.625,x:6.5,a:4,h:1.5},"LS2",{x:4.5,h:1.5},"RS2"],
[{y:-0.75,x:3.5},"C",{x:10.5},"<\\n,"],
[{y:-0.875,x:2.5},"X",{x:1},"V",{x:8.5},"M",{x:1},">\\n."],
[{y:-0.875,x:5.5},"B",{x:6.5},"N"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"Z",{x:14.5},"?\\n/",{a:7,w:1.5},""],
[{y:-0.375,x:3.5},"",{x:10.5},""],
[{y:-0.875,x:2.5},"",{x:1},"",{x:8.5},"",{x:1},""],
[{y:-0.75,x:0.5},"","",{x:14.5},"",""],
[{r:30,rx:6.5,ry:4.25,y:-1,x:1,a:4},"LU0","LU1"],
[{h:2},"LB0",{h:2},"LB1","LB2"],
[{x:2},"LB3"],
[{r:-30,rx:13,y:-1,x:-3},"RU1","RU0"],
[{x:-3},"RB2",{h:2},"RB1",{h:2},"RB0"],
[{x:-3},"RB3"]
]"""
    )
    return keyboard


def get_json_const_ergodox_arduino() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        """[
[{x:3.5},"#\\n3",{x:10.5},"*\\n8"],
[{y:-0.875,x:2.5},"@\\n2",{x:1},"$\\n4",{x:8.5},"&\\n7",{x:1},"(\\n9"],
[{y:-0.875,x:5.5},"%\\n5","LS0",{x:0.25,a:7,w:1.5,h:2.75},"\\n\\n\\n\\nArduino",{x:2.75,a:4},"RS0","^\\n6"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"!\\n1",{x:14.5},")\\n0",{a:7,w:1.5},""],
[{y:-0.495,x:10.25,w:1.5,h:2.75},"\\n\\n\\n\\nArduino"],
[{y:-0.88,x:3.5,a:4},"E",{x:10.5},"I"],
[{y:-0.875,x:2.5},"W",{x:1},"R",{x:8.5},"U",{x:1},"O"],
[{y:-0.875,x:5.5},"T",{h:1.5},"LS1",{x:4.5,h:1.5},"RS1","Y"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"Q",{x:14.5},"P",{a:7,w:1.5},""],
[{y:-0.375,x:3.5,a:4},"D",{x:10.5},"K"],
[{y:-0.875,x:2.5},"S",{x:1},"F",{x:8.5},"J",{x:1},"L"],
[{y:-0.875,x:5.5},"G",{x:6.5},"H"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"A",{x:14.5},":\\n;",{a:7,w:1.5},""],
[{y:-0.625,x:6.5,a:4,h:1.5},"LS2",{x:4.5,h:1.5},"RS2"],
[{y:-0.75,x:3.5},"C",{x:10.5},"<\\n,"],
[{y:-0.875,x:2.5},"X",{x:1},"V",{x:8.5},"M",{x:1},">\\n."],
[{y:-0.875,x:5.5},"B",{x:6.5},"N"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"Z",{x:14.5},"?\\n/",{a:7,w:1.5},""],
[{y:-0.375,x:3.5},"",{x:10.5},""],
[{y:-0.875,x:2.5},"",{x:1},"",{x:8.5},"",{x:1},""],
[{y:-0.75,x:0.5},"","",{x:14.5},"",""],
[{r:30,rx:6.5,ry:4.25,y:-1,x:1,a:4},"LU0","LU1"],
[{h:2},"LB0",{h:2},"LB1","LB2"],
[{x:2},"LB3"],
[{r:-30,rx:13,y:-1,x:-3},"RU1","RU0"],
[{x:-3},"RB2",{h:2},"RB1",{h:2},"RB0"],
[{x:-3},"RB3"]

]"""
    )
    return keyboard


def get_json_const_ergodox_arduino02() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        """[
{ name: "tez", switchType:"CherryMx", notes: 10},
[{x:3.5},"#\\n3",{x:10.5},"*\\n8"],
[{y:-0.875,x:2.5},"@\\n2",{x:1},"$\\n4",{x:8.5},"&\\n7",{x:1},"(\\n9"],
[{y:-0.875,x:5.5},"%\\n5","LS0",{x:0.25,a:7,w:1.5,h:2.75},"\\n\\n\\n\\nArduino",{x:2.75,a:4},"RS0","^\\n6"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"!\\n1",{x:14.5},")\\n0",{a:7,w:1.5},""],
[{y:-0.495,x:10.25,w:1.5,h:2.75},"\\n\\n\\n\\nArduino"],
[{y:-0.88,x:3.5,a:4},"E",{x:10.5},"I"],
[{y:-0.875,x:2.5},"W",{x:1},"R",{x:8.5},"U",{x:1},"O"],
[{y:-0.875,x:5.5},"T",{h:1.5},"LS1",{x:4.5,h:1.5},"RS1","Y"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"Q",{x:14.5},"P",{a:7,w:1.5},""],
[{y:-0.375,x:3.5,a:4},"D",{x:10.5},"K"],
[{y:-0.875,x:2.5},"S",{x:1},"F",{x:8.5},"J",{x:1},"L"],
[{y:-0.875,x:5.5},"G",{x:6.5},"H"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"A",{x:14.5},":\\n;",{a:7,w:1.5},""],
[{y:-0.625,x:6.5,a:4,h:1.5},"LS2",{x:4.5,h:1.5},"RS2"],
[{y:-0.75,x:3.5},"C",{x:10.5},"<\\n,"],
[{y:-0.875,x:2.5},"X",{x:1},"V",{x:8.5},"M",{x:1},">\\n."],
[{y:-0.875,x:5.5},"B",{x:6.5},"N"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"Z",{x:14.5},"?\\n/",{a:7,w:1.5},""],
[{y:-0.375,x:3.5},"",{x:10.5},""],
[{y:-0.875,x:2.5},"",{x:1},"",{x:8.5},"",{x:1},""],
[{y:-0.75,x:0.5},"","",{x:14.5},"",""],
[{r:30,rx:6.5,ry:4.25,y:-1,x:1,a:4},"LU0","LU1"],
[{h:2},"LB0",{h:2},"LB1","LB2"],
[{x:2},"LB3"],
[{r:-30,rx:13,y:-1,x:-3},"RU1","RU0"],
[{x:-3},"RB2",{h:2},"RB1",{h:2},"RB0"],
[{x:-3},"RB3"]
]"""
    )
    return keyboard


def get_json_const_ergodox_arduino_pin01() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        """[
[{x:3.5},"#/3",{x:10.5},"*/8"],
[{y:-0.875,x:2.5},"@/2",{x:1},"$/4",{x:8.5},"&/7",{x:1},"(/9"],
[{y:-0.875,x:5.5},"%/5","LS0",{x:0.25,a:7,w:1.5,h:2.75},"\\n\\n\\n\\nArduino",{x:2.75,a:4},"RS0","^/6"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"!/1",{x:14.5},")/0",{a:7,w:1.5},""],
[{y:-0.495,x:5.25,a:4,w:0.5,h:0.5},"pin\\n\\n\\n\\nPinPlate",{x:4.5,a:7,w:1.5,h:2.75},"\\n\\n\\n\\nArduino",{x:4,a:4,w:0.5,h:0.5},"pin\\n\\n\\n\\nPinPlate"],
[{y:-0.88,x:3.5},"E",{x:10.5},"I"],
[{y:-0.875,x:2.5},"W",{x:1},"R",{x:8.5},"U",{x:1},"O"],
[{y:-0.995,x:2.25,w:0.5,h:0.5},"pin\\n\\n\\n\\nPinPlate",{x:10,w:0.5,h:0.5},"pin\\n\\n\\n\\nPinPlate"],
[{y:-0.88,x:5.5},"T",{h:1.5},"LS1",{x:4.5,h:1.5},"RS1","Y"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"Q",{x:14.5},"P",{a:7,w:1.5},""],
[{y:-0.375,x:3.5,a:4},"D",{x:10.5},"K"],
[{y:-0.875,x:2.5},"S",{x:1},"F",{x:8.5},"J",{x:1},"L"],
[{y:-0.875,x:5.5},"G",{x:6.5},"H"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"A",{x:14.5},":\\\\n;",{a:7,w:1.5},""],
[{y:-0.625,x:5.25,a:4,w:0.5,h:0.5},"\\n\\n\\n\\nPinPlate",{x:0.75,h:1.5},"LS2",{x:4.5,h:1.5},"RS2",{x:2.75,w:0.5,h:0.5},"\\n\\n\\n\\nPinPlate"],
[{y:-0.75,x:2.25,w:0.5,h:0.5},"\\n\\n\\n\\nPinPlate",{x:0.75},"C",{x:8.25,w:0.5,h:0.5},"\\n\\n\\n\\nPinPlate",{x:1.75},"<\\\\n,"],
[{y:-0.875,x:2.5},"X",{x:1},"V",{x:8.5},"M",{x:1},">/."],
[{y:-0.875,x:5.5},"B",{x:6.5},"N"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"Z",{x:14.5},"?//",{a:7,w:1.5},""],
[{y:-0.375,x:3.5},"",{x:10.5},""],
[{y:-0.875,x:2.5},"",{x:1},"",{x:8.5},"",{x:1},""],
[{y:-0.75,x:0.5},"","",{x:14.5},"",""],
[{r:30,rx:6.5,ry:4.25,y:-1,x:1,a:4},"LU0","LU1"],
[{h:2},"LB0",{h:2},"LB1","LB2"],
[{x:2},"LB3"],
[{r:-30,rx:13,y:-1,x:-3},"RU1","RU0"],
[{x:-3},"RB2",{h:2},"RB1",{h:2},"RB0"],
[{x:-3},"RB3"]
]"""
    )
    return keyboard


def get_json_const_ergodox_arduino_pin02() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        """[
        [{x:3.5},"#/3"],
[{y:-0.875,x:2.5},"@/2",{x:1},"$/4"],
[{y:-0.875,x:5.5},"%/5","LS0",{x:0.25,a:7,w:1.5,h:2.75},"\\n\\n\\n\\nArduino"],
[{y:-0.875,w:1.5},"",{a:4},"!/1"],
[{y:-0.495,x:5.25,w:0.5,h:0.5},"\\n\\n\\n\\npinplate"],
[{y:-0.88,x:3.5},"E"],
[{y:-0.875,x:2.5},"W",{x:1},"R"],
[{y:-0.995,x:2.25,w:0.5,h:0.5},"\\n\\n\\n\\npinpcb"],
[{y:-0.88,x:5.5},"T",{h:1.5},"LS1"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"Q"],
[{y:-0.375,x:3.5},"D"],
[{y:-0.875,x:2.5},"S",{x:1},"F"],
[{y:-0.875,x:5.5},"G"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"A"],
[{y:-0.625,x:5.25,w:0.5,h:0.5},"\\n\\n\\n\\npinplate",{x:0.75,h:1.5},"LS2"],
[{y:-0.75,x:2.25,w:0.5,h:0.5},"\\n\\n\\n\\npinpcb",{x:0.75},"C"],
[{y:-0.875,x:2.5},"X",{x:1},"V"],
[{y:-0.875,x:5.5},"B"],
[{y:-0.875,a:7,w:1.5},"",{a:4},"Z"],
[{y:-0.375,x:3.5,a:7},""],
[{y:-0.875,x:2.5},"",{x:1},""],
[{y:-0.75,x:0.5},"",""]
]"""
    )
    return keyboard


def get_json_const_02() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        """[
["Num Lock","/"],
["7\\nHome"],
[{r:45,rx:1,ry:1,y:-0.5},"8\\n↑"]
]"""
    )
    return keyboard


def get_json_const_03() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        """[
    [{r:45,rx:1,ry:1,y:-0.5},"8\\n↑"]
    ]"""
    )

    return keyboard


def get_json_const_04() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        """[
["Num Lock"],
[{r:45,rx:1,ry:1,y:-0.5},"8\\n↑"]
    ]"""
    )
    return keyboard


def get_json_const_05() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        """[
[{x:0.15,a:7,w:0.5,h:0.5},"PinPlate",{x:-0.4},"A",{x:-0.1,w:0.5,h:0.5},"PinPlate",{x:-0.4},"B",{x:-0.1,w:0.5,h:0.5},"PinPlate"],
[{y:-0.75,x:0.15,w:0.5,h:0.5},"PinPcb",{x:0.5,w:0.5,h:0.5},"PinPcb",{x:0.5,w:0.5,h:0.5},"PinPcb"],
[{y:-0.45,x:0.15,w:0.5,h:0.5},"PinPlate",{x:0.5,w:0.5,h:0.5},"PinPlate",{x:0.5,w:0.5,h:0.5},"PinPlate"]




    ]"""
    )
    return keyboard


def arduino_only() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        """[
[{y:0.5,x:0.25,a:7,w:0.5,h:0.5},"PinPlate",{x:-0.25,w:0.75,h:2.25},"Arduino",{x:0.25,w:0.5,h:0.5},"PinPcb"],
[{y:0.75,x:0.25,w:0.5,h:0.5},"PinPcb",{x:0.75,w:0.5,h:0.5},"PinPlate"]

    ]"""
    )
    return keyboard


def get_first_keyboard_print() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        """[
[{a:7,w:0.5,h:0.5},"\\n\\n\\n\\nPinPlate",{x:1.25,w:0.5,h:0.5},"\\n\\n\\n\\nPinPcb",{x:1,w:0.5,h:0.5},"\\n\\n\\n\\nPinPlate"],
[{y:-0.75,x:0.25},"",""],
[{y:-0.5,x:2.25},"\\n\\n\\n\\nArduino"],
[{y:-0.75,w:0.5,h:0.5},"\\n\\n\\n\\nPinPcb",{x:2.75,w:0.5,h:0.5},"\\n\\n\\n\\nPinPcb"],
[{y:-0.75,x:0.25},"",""],
[{w:0.5,h:0.5},"\\n\\n\\n\\nPinPlate",{x:1.25,w:0.5,h:0.5},"\\n\\n\\n\\nPinPcb",{x:1,w:0.5,h:0.5},"\\n\\n\\n\\nPinPlate"]

    ]"""
    )
    return keyboard


def get_arcade_print() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        """[
[{y:0.25,x:3.5,a:7},"Arduino",{x:2.5},"",{x:-0.25,w:0.5,h:0.5},"split_keyboard_connector"],
[{y:-0.75,x:0.15,w:0.5,h:0.5},"PinPcb",{x:-0.4},"","","",{x:-0.1,w:0.5,h:0.5},"PinPcb",{x:2.35},""],
[{y:-0.75,x:4.9,w:0.5,h:0.5},"PinPcb",{x:-0.4},""],
[{y:-0.65,x:6.9,w:0.5,h:0.5},"PinPlate"],
[{y:-0.85,x:7},""],
[{y:-0.9,x:5.9,w:0.5,h:0.5},"PinPlate"],
[{y:-0.95,x:1.15,w:0.5,h:0.5},"PinPlate",{x:0.5,w:0.5,h:0.5},"PinPlate"],
[{y:-0.9,x:0.25},"","","",{x:2.75},""],
[{y:-0.75,x:5},""],
[{y:-0.75,x:7.75,w:0.5,h:0.5},"PinPcb"],
[{y:-0.75,x:0.15,w:0.5,h:0.5},"PinPcb",{x:2.5,w:0.5,h:0.5},"PinPcb"],
[{y:-0.75,x:4.9,w:0.5,h:0.5},"PinPcb"]
    ]"""
    )
    return keyboard


def get_minimal_keyboard() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        """[
[{y:0.25,x:2,c:"#ff0000",a:7,w:0.5,h:0.5},"\\n\\n\\n\\nPinPlate",{x:-0.5,c:"#cccccc"},""],
[{y:-0.75,x:1},"",{x:1},"",{c:"#ff0000",w:0.5,h:0.5},"\\n\\n\\n\\nPinPlate",{x:-0.5,c:"#cccccc"},""],
[{y:-0.75},"",{x:-1,c:"#ff0000",w:0.5,h:0.5},"\\n\\n\\n\\nPinPlate"],
[{y:-0.5,x:2,c:"#cccccc"},""],
[{y:-0.75,x:1},"",{x:1},"","","\\n\\n\\n\\nArduino"],
[{y:-0.75},""],
[{y:-0.5,x:2},""],
[{y:-0.75,x:1},"",{x:1},"",""],
[{y:-0.75},"",{x:1,c:"#ff0000",w:0.5,h:0.5},"\\n\\n\\n\\nPinPlate"],
[{y:-0.75,x:4,w:0.5,h:0.5},"\\n\\n\\n\\nPinPlate"],
[{y:-0.75,w:0.5,h:0.5},"\\n\\n\\n\\nPinPlate"],
[{y:-0.75,x:3,c:"#cccccc"},""],
[{r:15,y:-2.25,x:5},"",""]



    ]"""
    )
    return keyboard


# [{y: 0.25, x: 2, a: 7}, ""],
# [{y: -0.75, x: 1}, "", {x: 1}, "", ""],
# [{y: -0.75}, ""],
# [{y: -0.5, x: 2}, ""],
# [{y: -0.75, x: 1}, "", {x: 1}, "", "", "\\n\\n\\n\\nArduino"],
# [{y: -0.75}, ""],
# [{y: -0.5, x: 2}, ""],
# [{y: -0.75, x: 1}, "", {x: 1}, "", ""],
# [{y: -0.75}, ""],
# [{y: -0.25, x: 3}, ""],
# [{r: 15, y: -2.25, x: 5}, "", ""]


if __name__ == "__main__":
    main()
