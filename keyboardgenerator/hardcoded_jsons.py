import pykle_serial as kle_serial


def support_parts() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        """[
[{y:0.18,x:0.2,p:"Key",sm:"platetext",w:1.4,h:0.5},"Keys",{x:0.3,p:"Conn",w:1.4,h:0.5},"Connectors",{x:1.1,p:"Pins",h:0.5},"Pins"],
[{y:-0.98,x:5.9,p:"TEZ3\\n  Y.E",sm:"arduino",a:5,h:2},"Arduino"],
[{y:-0.7,x:2.3,sm:"trrs",w:0.5},"trrs"],
[{y:-0.95,x:0.4,sm:"cherry",a:4},"MX"],
[{y:-0.92,x:4.55,sm:"pinpcb",w:0.5,h:0.5},"PinPcb"],
[{y:-0.75,x:5.7,p:"MCU",sm:"platetext",h:0.5},"MCU"],
[{y:-0.68,x:4.55,p:"TEZ3\\n  Y.E",sm:"pinplate",w:0.5,h:0.5},"PPlate"]
]"""
    )
    return keyboard


def ergodox_full_keyboard() -> kle_serial.Keyboard:
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


def get_arcade_print() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        """[
[{y:0.25,x:3.5,a:7},"Arduino",{x:2.5},"",{x:-0.25,w:0.5,h:0.5},"trrs"],
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


def one_board_ergo() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        """[
[{x:2},"E",{x:7.5},"I"],
[{y:-0.87,x:1},"W",{x:1},"R",{x:5.5},"U",{x:1},"O"],
[{y:-0.88,x:4},"T",{x:3.5},"Y"],
[{y:-0.87},"Q",{x:11.5},"P"],
[{y:-0.38,x:2},"D",{x:7.5},"K"],
[{y:-0.87,x:1},"S",{x:1},"F",{x:5.5},"J",{x:1},"L"],
[{y:-0.88,x:4},"G",{x:3.5},"H"],
[{y:-0.87},"A",{x:11.5},":\\n;"],
[{y:-0.38,x:2},"C",{x:7.5},"<\\n,"],
[{y:-0.87,x:1},"X",{x:1},"V",{x:5.5},"M",{x:1},">\\n."],
[{y:-0.88,x:4},"B",{x:3.5},"N"],
[{y:-0.87},"Z",{x:11.5},"?\\n/"],
[{r:30,rx:5,ry:3.25,a:7,h:1.5},"",{h:1.5},""],
[{y:-0.5,x:-1},""],
[{r:-30,rx:8.5,x:-2,h:1.5},"",{h:1.5},""],
[{y:-0.5},""]
]"""
    )
    return keyboard


def one_board_tez_v4() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        """[
[{x:1.9,sm:"pinplate",w:0.5,h:0.5},"PPlate",{x:-0.4,sm:"cherry"},"E",{x:2.3,sm:"arduino",a:5,h:2},"Arduino"],
[{y:-0.97,x:0.75,sm:"pinpcb",a:4,w:0.5,h:0.5},"PinPcb",{x:3.5,w:0.5,h:0.5},"PinPcb"],
[{y:-0.9,x:1,sm:"cherry"},"W",{x:1},"R",{x:-0.1,sm:"pinplate",w:0.5,h:0.5},"PPlate"],
[{y:-0.9,w:0.5,h:0.5},"PPlate"],
[{y:-0.98,x:4,sm:"cherry"},"T"],
[{y:-0.87},"Q"],
[{y:-0.38,x:2},"D"],
[{y:-0.87,x:1},"S",{x:1},"F"],
[{y:-0.98,x:1.9,sm:"pinplate",w:0.5,h:0.5},"PPlate",{x:0.5,sm:"pinpcb",w:0.5,h:0.5},"PinPcb"],
[{y:-0.9,x:4,sm:"cherry"},"G"],
[{y:-0.97,x:5,p:"TEZ3\\n  Y.E",sm:"platetext",a:7},""],
[{y:-0.9,sm:"cherry",a:4},"A"],
[{y:-0.95,x:3.9,sm:"pinplate",w:0.5,h:0.5},"PPlate"],
[{y:-0.43,x:2,sm:"cherry"},"C"],
[{y:-0.87,x:1},"X",{x:1},"V"],
[{y:-0.88,x:4},"B"],
[{y:-0.87},"Z"],
[{y:-0.5,x:1.9,sm:"pinplate",w:0.5,h:0.5},"PPlate"],
[{y:-0.73,x:3.9,w:0.5,h:0.5},"PPlate"],
[{y:-0.87,w:0.5,h:0.5},"PPlate",{x:0.5,sm:"pinpcb",w:0.5,h:0.5},"PinPcb"],
[{y:0.25,x:5.75,w:0.5,h:0.5},"PinPcb"],
[{y:-0.75,x:3.75,w:0.5,h:0.5},"PinPcb"],
[{r:30,rx:5,ry:3.25,y:1,x:-1,sm:"cherry",a:7},"","",""],
[{y:-0.8,x:-0.1,sm:"pinplate",a:4,w:0.5,h:0.5},"PPlate",{x:0.5,w:0.5,h:0.5},"PPlate"],
[{r:90,rx:5.25,ry:1.2,y:-1.1,x:1.85,sm:"trrs",a:5,w:0.5},"trrs"]
]"""
    )
    return keyboard


def left_side_gez_v1() -> kle_serial.Keyboard:
    keyboard = kle_serial.parse(
        r"""[
[{y:0.25,x:3,sm:"cherry"},"3"],
[{y:-0.97,x:5.4,sm:"pinb2t",w:0.5,h:0.5},"PB2T"],
[{y:-0.93,x:6.2,sm:"arduino",a:5,h:2},"Arduino"],
[{y:-0.97,x:2,sm:"cherry",a:4},"2",{x:1},"4"],
[{y:-0.88,sm:"pinb2t",w:0.5,h:0.5},"PB2T",{x:4.5,sm:"cherry"},"5"],
[{y:-0.87,x:1},"1"],
[{y:-0.95},"Esc"],
[{y:-0.43,x:3},"E"],
[{y:-0.87,x:2},"W",{x:1},"R"],
[{y:-0.9,x:0.85,sm:"pinplate",w:0.5,h:0.5},"PinPlate"],
[{y:-0.98,x:5,sm:"cherry"},"T"],
[{y:-0.87,x:1},"Q"],
[{y:-0.95},"Tab"],
[{y:-0.43,x:3},"D"],
[{y:-0.87,x:2},"S",{x:1},"F"],
[{y:-0.88,x:5},"G"],
[{y:-0.97,x:5.9,p:"GEZ1\n  Y.E",sm:"platetext"},"Text"],
[{y:-0.9,x:1,sm:"cherry"},"A"],
[{y:-0.95},"Ctrl"],
[{y:-0.48,x:4.8,p:"",sm:"pinplate",w:0.5,h:0.5},"PinPlate"],
[{y:-0.95,x:3,p:"GEZ1\\n  Y.E",sm:"cherry"},"C"],
[{y:-0.87,x:2},"X",{x:1},"V"],
[{y:-0.88,x:5},"B"],
[{y:-0.87,x:1},"Z"],
[{y:-0.95},"Shift"],
[{y:-0.15,x:0.8,sm:"pinb2t",w:0.5,h:0.5},"PB2T"],
[{y:0.17,x:6.4,w:0.5,h:0.5},"PB2T"],
[{r:30,rx:6,ry:4.5,y:1,x:-1,sm:"cherry",a:7},"","",""],
[{r:90,rx:6.25,ry:2.5,y:-1.05,x:1.95,p:"TEZ4\\n  Y.E",sm:"trrs",a:5,w:0.5},"trrs"]
]"""
    )
    # keyboard.meta.split = True
    return keyboard


def almost_there() -> kle_serial.Keyboard:
    Keyboard = kle_serial.parse(
        """[
[{y:1,x:0.75,sm:"pinplate",w:0.5,h:0.5},"PPlate",{x:0.5,sm:"pinpcb",w:0.5,h:0.5},"PinPcb",{x:0.75,sm:"pinplate",w:0.5,h:0.5},"PPlate",{x:-0.2,sm:"arduino",a:5,h:2},"Arduino"],
[{y:-0.62,x:1,p:"TEZ3\\nY.N",sm:"cherry",a:4},"A","S"],
[{y:-0.35,x:0.75,sm:"pinpcb",w:0.5,h:0.5},"PinPcb"],
[{y:-0.75,x:3,w:0.5,h:0.5},"PinPcb"],
[{y:-0.9,x:1,sm:"cherry"},"Z","X"],
[{y:0.12,x:0.75,sm:"pinplate",w:0.5,h:0.5},"PPlate",{x:0.5,sm:"pinpcb",w:0.5,h:0.5},"PinPcb",{x:0.5,sm:"pinplate",w:0.5,h:0.5},"PPlate"],
[{r:90,rx:5.25,ry:1.2,y:1.05,x:2,sm:"trrs",a:5,w:0.5},"trrs"]
            ]"""
    )
    return Keyboard
