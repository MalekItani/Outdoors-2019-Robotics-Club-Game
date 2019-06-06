 fruit ninja inspired video game to be showcased at AUB Outdoors 2019
The game consists of colorful shapes which appear on the screen. The player must destroy all shapes on the screen to achieve the highest possible score. Shapes can be categorized into 3 types:
- **Regular Shapes:** These are solid, fixed colored squares or circles and make up the majority of the shapes that will appear. They explode on hit and grant the player 1 point.
- **Chameleon Shapes:** These are squares or circles which change hue over time. They explode on hit and grant the player 2 points. Chameleon shapes are 50 times rarer than their regular counterparts.
- **Yves:** Initially meant as a goof, this shape is a picture of our - as of 2019 - current club president. Yves takes 3 hits to explode and grants the player 5 points. Yves is 20 times rarer than  Regular shapes.

The game can be played with just mouse, but I strongly suggest you used a wii remote and make use of wminput and an IR emitter to control the game. However, this approach is ineffective under sunlight. 

For this reason, I have developed a novel mechanism to simulate a mouse tracker using OpenCV and AprilTags. This was the primary method of tracking in AUB Outdoors, and the results were appreciable. To activate this mode, a camera running on a Raspberry Pi was used to retrieve images, stream them to the host PC, and perform the necessary processing to track the position of the AprilTag. The code for this is not included in this repository. Up to my knowledge, this marks the first ever attempt at AprilTag use for video gaming and mouse pointer simulation.

As of now, there are only two kinds of cursor the player can use to destroy the shapes:
- **Crosshair**
- **Lightsaber**

with resonable recoil times for all.

The game was developed using Python, and all graphics are rendered on a Tkinter canvas. The game requires the following dependencies:
- tkinter
- pygame
- numpy
- pillow
- sox/play (for sound effects)
- wminput (optional, for wiimote-based tracking)
- AprilTags (optional, for AprilTag-based tracking)
- OpenCV (optional, for AprilTag-based tracking)
- requests (optional, for AprilTag-based tracking)

