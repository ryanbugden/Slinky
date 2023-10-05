# Slinky

<img src="./images/mechanic_icon.png"  width="80">

#### Slinky is a RoboFont extension for scaling your whole font up or down.

You can choose a precise measurement (either UPM or Ascender-to-Descender height), and set some settings, and it will do the rest.

<img src="./images/ui.png"  width="300">

## Units

Enter your desired measurement here, in units.


## Scale From

This is what your measurement will correspond to. You can scale based on UPM, or your ascender-to-descender height. If you scale your UPM, everything will be scaled proportionately. If you scale your Ascender-to-Descender height, you'll have the option on how/whether UPM is changed...


## UPM Options

These options are only available when Asc-Desc Height is enabled:

#### Scale

Scale the UPM proportionately to how you're scaling the ascender-to-descender height is being scaled. This will ensure the relationship between your font dimensions and your UPM is maintained.

#### Match Asc-Desc Height

This will snap the UPM to match the Unit measurement provided, and ultimately match the distance between your ascender and descender.

#### Don’t Change

This will leave UPM unaffected while everything else scales around it. This is useful, for instance, if you've got your UPM correct, but your glyphs/font dimensions are too small.

## Scale

These are things you can choose to scale along with everything else. Usually it's a good idea to leave all of these checked.

## Round

When you scale drawings, there may be `float` numbers that no longer fit the grid you're working on. If you'd like to leave them `float` for now, choose Don’t Round. If you'd like your final drawings to be shimmied a bit to fit a 1-unit grid, choose 1 Unit.

## Layer(s)

Choose which layers you'd like to scale, either just the foreground, or all layers.

## Font(s)

Choose which fonts you'd like to scale, either just the front-most `CurrentFont()`, or all open fonts.

## Perform...

Choose whether you'd like to scale the font in-place, or whether you'd like Slinky to make a copy first and _then_ scale. 

> Note: If you scale the font in-place, just remember that it's hard to Undo. Be sure to save your work before clicking Scale.