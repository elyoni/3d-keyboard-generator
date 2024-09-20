# 3D Keyboard Builder

## Motivation (Short Version)

After experimenting with various custom keyboards, including the Ergodox and my own hand-built designs, I realized I wanted something more flexible and hot-swappable. My journey led me to a project that inspired me to create my own fully customizable keyboard, allowing me to test different layouts and components. This project not only solves my ergonomic needs but also provides the creative freedom to explore new features.
## Motivation (Full Version)

In 2020, my brother gave me his Ergodox keyboard [here’s a picture of the Ergodox](Documents/ergodox.jpg). At first, I struggled to find a comfortable configuration, constantly tweaking the settings every 10 minutes. I limited myself to using the Ergodox for 30 minutes daily since it reduced my work performance. After a few weeks, however, I became comfortable and switched to using the Ergodox full-time.

When my job announced that we needed to return to the office, I decided to build my own keyboard—one for home and one for the office. I wanted to keep it as affordable as possible, so I bought a bamboo cutting board from IKEA, a plate, keys, and keycaps from AliExpress. I carved out space in the cutting board for the plate and keys, which took over 4 hours. Then, I hand-wired all the keys and called the keyboard "TEZ" (Travel Easy). After using it for a few months, I realized I didn’t really like it and went back to carrying my Ergodox everywhere.

During this time, I learned a few things:
1. I prefer fewer keys and now use just 36.
2. To comfortably use the three thumb keys, I needed to shift them slightly to the right (on the left side of the keyboard).
3. I wanted the keys to be hot-swappable.

After a lot of research, I found a project called 3D-Printable Hotswap Keyboard PCB Generator. The creator, 50an6xy06r6n, came up with a clever way to achieve hot-swappability by using diodes and column wires. I printed and soldered the parts and started using it. At first, I really liked it, but after a few months, some keys would stop working unless I pressed them hard, which became frustrating. Eventually, I gave up on it and returned to the Ergodox at home and work.

At this point, I realized I had two options:

1. Learn how to create a PCB and design the keyboard I wanted.
2. Start a new project similar to 50an6xy06r6n’s, but instead of using diodes and wires to connect the columns, use a proper hot-swappable connector.

Long story short, I decided to create my own project. There were several reasons: I wasn’t sure which layout I wanted, and I didn’t want to waste money on unwanted PCBs. By creating my own project, I could easily try different components like an LCD or a joystick. I chose Python and pythonsolid2 for my project because I don’t really like OpenSCAD and enjoy the flexibility Python provides.


## Project Description

This application takes a JSON file output from KLE and generates three STL files that are ready for 3D printing:
1. **Plate**: The top layer that holds the switches.
2. **PCB**: The layer designed to house the electronic components.
3. **Bottom**: The bottom layer, which encloses the keyboard.

The script processes each element of the KLE JSON to create a precise, functional 3D model for your custom keyboard.

## Supported Parts

### Keys
- **Cherry MX switches**
```json
[{sm:"cherry",a:7},"Q","W","E","R"],
["A",{w:2},"S","F"],
["Z","X","C"],
[{r:30,y:-3,x:4.25},"V"]
```
![Keys](Documents/Keys.png)

### Arduino
- **Arduino** with Type C connection support
```json
[{y:0.2,x:5.9,sm:"arduino",a:5,h:2},"Arduino"]
```
![Mcu](Documents/MCU.png)

### Pins (Layer Connectors)
- Pins act as placeholders for screws, providing modular assembly of keyboard layers.
- **Pin Types**:
  - **PinPcb**: Connects the Bottom layer to the PCB.
  - **PinPlate**: Connects the PCB to the Plate.
  - **PinB2P**: Direct connection between the Bottom layer and the Plate.

### Split Keyboard Connector
- **TRRS Connector**: Support for split keyboard designs with TRRS connections.

### Text
- Custom text can be engraved onto the plate.

## Components Example

Here is an example of a KLE JSON input with all components listed:


To configure the JSON file of your keyboard you need to provide the key type of your keyboard.
The key type is used to determine the spacing between the parts in the keyboard.

```json
{ name: "tez", switchType:"carry"},
[{x:3.5},"#\\n3",{x:10.5},"*\\n8"],
[{y:-0.875,x:2.5},"@\\n2",{x:1},"$\\n4",{x:8.5},"&\\n7",{x:1},"(\\n9"],
[{y:-0.875,x:5.5},"%\\n5","LS0",{x:0.25,a:7,w:1.5,h:2.75},"\\n\\n\\n\\nArduino",{x:2.75,a:4},"RS0","^\\n6"],
```

When you add a new part make sure to add the key type to the get_part_obj


## Pins
Plate pins on top of a key can be in 0.15 units on top of a key


## Todo
Replace all the function "draw_pcb_part_******" to "_draw_pcb_part_******" and on the main function "draw_pcb_part_******" to do the rotation and the translation of the part



To Chat GPT:
Create me a README file for my Project. The Readme file will be presented in my personal Github. I would to show my motivation, how I build it and why I have deiced to go this way. If you need more information for me please ask and don't assume you know the answer. Prepare places to put example with code and pictures

Project description: My application is using [KLE|http://www.keyboard-layout-editor.com/] JSON output as an input. The script take every element in the JSON file and convert it into three STL files for you 3d printer. Plate, PCB, and Bottom.

## Supported Parts:
* Keys:
    * Cherry MX
* Arduino With Type C connection
* Pins to connect beteen the different layers
    * Pins are a placement for scraws
    * Pins type:
        * PinPcb: Connect between the Bottom layer to the PCB
        * PinPlate: Connect between the PCB and the Plate
        * PinB2P: Connect between the Bottom layer to the Plate
* Split keyboard connector:
    * TRRS Connector
* Text: Will be presented on the plate

### Components Example:

```json All Components
{ name: "tez", switchType:"carry"},
[{x:3.5},"#\\n3",{x:10.5},"*\\n8"],
[{y:-0.875,x:2.5},"@\\n2",{x:1},"$\\n4",{x:8.5},"&\\n7",{x:1},"(\\n9"],
[{y:-0.875,x:5.5},"%\\n5","LS0",{x:0.25,a:7,w:1.5,h:2.75},"\\n\\n\\n\\nArduino",{x:2.75,a:4},"RS0","^\\n6"],
```


### How to add new part:
WIP


## Left Over:
* Support Kailh switch (Low Profile)
* JSON input


## Motivation:
Before 2020 my brother gave me his Ergodox keyboard (Add link for the keyboard picture). At first I really had an hard time to find the right configuration I felt comfort with, and every 10 minute I found my self twiking the settings. I have limit my work with the ergodox for 30 minute a day becase I reduce my performance at work. After couple of weeks I startd to fill very computable with it and moved to ergodox for full time. When my job announst, that we need to return to work from the office I decied to build my own keyboard. One for the my home and one for the office, but I really wanted to keep it cheep as possible. I bought a bambo cutting board from Ikea, plate, keys and keycaps from AliExpress. I cut into the cutting board to put the plate and keys. Only the curving took around 4+ hours. I have hand wire all the keys. I called this keyboard TEZ, Travel Easy, and start to use this keyboard after couple of mount I have realize I really don't like it and start to take my Ergodox everywhere.
I tried to find a good solution for my problem, I really liked the ergodox but during my time with it, I understand couple of things:
1. I really like the idea of using less and fewer keys. Now I am using 36 keys.
2. To use the three keys with thumps, I need to move the keys slightly to right (For the left side keyboard)
3. I would like the keys should be hot swappable.
After a lot research, I found this project [3D-Printable Hotswap Keyboard PCB Generator](https://github.com/50an6xy06r6n/hotswap_pcb_generator). The creator, 50an6xy06r6n is had a clever idea how to achieve the hot swappable. He is using the diode and the wires of the columns to achieve it. I have printed and soldered all the parts and start to use it. In couple first month I really liked it, but from time to time I had some issue with couple of the keys, I had to push hard to connect the key properly. At some point I got really annoid with that, and I put this keyboard away. And again I return to use the Ergodox at home and at the office.
At this point I have realize I have two options. First option to learn how to create a PCB and create the keyboard I want and the second option to create a new project like project 50an6xy06r6n has created but instead of using the diode and the wires to connect the cable I would use a real hot swappable connect. Long story short, I have decided to create my own project. From couple of reason, I don't really know which layout I would want and I didn't want to wast a lot of mouny with unwanted PCB's, if I create my own projet I can easyly tried different component like LCD, Joystick and more. I have chosen [solidpython2](https://github.com/jeff-dh/SolidPython) because I don't really like the Openscad and I really enjoy the flexibility of python.



Explain this: `After a few weeks, however, ` Why using however?4
