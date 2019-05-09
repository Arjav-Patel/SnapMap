# SnapMap
Tool to automatically import level maps in Unity with corresponding map/sprite pictures.

### This might be useful to you if
   *  You need a replica of a 2D game to develop game AI
   *  You want to recreate 2D games (Mario, Zelda, etc), and focus solely on game logic, not game design
   *  You want to quickly prototype 2D levels, and want to use Photoshop, Paint, or some other photo editor instead of Unity

# Usage

For first time usage, run `python setup.py` then run `pip install opencv-python tqdm`

To get initial data, place all level images in *Assets/Resources/Levels* and all sprite images in *Assets/Resources/Sprites*

Run `python main.py [options]`

Options: Use `--multiscale True/False` to use sprite images that are not perfectly scaled with the level images (ex. Proper Super Mario Bros. sprites are multiples of 16px by 16px images, and the levels are composed solely of these). Note, that this will take much longer, so it is advised to find proper scans of the levels and sprites if possible.

After this is done, a .txt file of the level data will be saved in *Assets/Data*. 

Load the project in Unity, the Level GameObject's inspector has a property called *level*. Type in the name of the level you want to load, and hit play.

If you move, rotate, or rescale the blocks, hit the save button in the inspector of the Level GameObject, to preserve these changes. Hitting reload will take you back to your last save point.

To reimport assets run `./reimport.sh`
<p align="center">
  <img src="https://i.imgur.com/oMQSi5g.png">
  <img src="https://i.imgur.com/uqbYoPp.png" width="671" height="223">
</p>
