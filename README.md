To configure the json file of your keyboard you need to provide the key type of your keyboard.
+The key type is used to determine the spacing between the parts in the keyboard.
`json

{ name: "tez", switchType:"carry"},
[{x:3.5},"#\\n3",{x:10.5},"*\\n8"],
[{y:-0.875,x:2.5},"@\\n2",{x:1},"$\\n4",{x:8.5},"&\\n7",{x:1},"(\\n9"],
[{y:-0.875,x:5.5},"%\\n5","LS0",{x:0.25,a:7,w:1.5,h:2.75},"\\n\\n\\n\\nArduino",{x:2.75,a:4},"RS0","^\\n6"],

`

When you add a new part make sure to add the key type to the get_part_obj


== Pins
Plate pins on top of a key can be in 0.15 units on top of a key
