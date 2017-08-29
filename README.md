## Project: Search and Sample Return

### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it! _Sorry in advance for my crippled English_

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.

* To successfully identify rock samples, color_thresh function had to be modified to be able to use interval rather then only low threshold values. 
Please see next section for detailed description


#### 2. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 


* The following steps were taken to process rover vision image and update Rover object attributes
1. To compensate Rover rolling, image is rotated around center in the direction opposite to roll angle. (please see rotate_image helper function). To get roll and pitch angles I had to add correspongin attributes to Databucket class
2. To get rover map view applied perspective transorm
3. To get navigable area, applied thresholding (160,160,160) to warped image
4. To get obstacle area, inverted previously obtained navigable area
5. To get sample location, applied interval threshholding to warped image, with the following interval low = (100,100,20), high = (255,255,30).

* There are 2 videos in output folder
1. **_test_mapping.mp4_** - based on provided test data
2. **_test_mapping2.mp4_** - based on my recording


### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.


#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**


#### 1. Rover states
Rover is considered as state machine with the following states
* **Main states:**
1. Forward
2. Stop
3. Sample spotted
* **Additional states:**
4. Stuck
5. Circling

##### Forward
* If rover is not stuck and not circling, check if there is enough of navigable terrain;
##### Stop
* If robot is not stuck, spin unless there are enough of navigable terrain and go;
##### Sample spotted
* If there are distances from sample (obtained in perception step) then set navigation angle to the direction of sample, and decrease velocity when approaching;

##### Stuck
* "Stuck" here means that ground velocity of the rover does not change within specified timeinterval (defined as number of measurement cycles). After rover is marked as "stuck", recovery operation is performed (described below);

##### Circling
* Circling is a form of "stuck" when rover is unable to change direction, resulting in it driving in circles indefinitely (usually happens on wide open spaces). Rover marked as "Circling" when steering angle does not change from -15 or 15 within specified time interval (defined as number of measurement cycles), circling recovery is performed in this case (described below);

#### 2. Robot image processing

* The following steps were taken to process rover vision image and update Rover object attributes
1. To compensate Rover rolling, image is rotated around center in the direction opposite to roll angle
2. To get rover map view applied perspective transorm
3. To get navigable area, applied thresholding (160,160,160) to warped image
4. To get obstacle area, inverted previously obtained navigable area
5. To get sample location, applied interval threshholding to warped image, with the following interval low = (100,100,20), high = (255,255,30). (these thresholds definitely need tuning:) )

#### 3. Direction choosing and correction
* I created additional Rover attribute "visited_map" which is 20x20 array of ints. Visited Map is essentinally increased scale (x10) world map, each cell stores the number of perception cycles rover was in the map sector. The plan was to use this map to calculate priority when choosing steer direction.  Currently only the cells which are adjacent to Rover's position are checked to calculate priority, which is obviously not enough.
	
#### 4. Recovery strategies
##### 1. Stuck recovery 
* To "unstuck" rover, its throttle is set to negative number (driving backwards) for a specified time interval (defined as a number of measurment cycles);

##### 2. Circling recovery 
* To "uncircle" rover, its steering angle is reset and mode is set to "stop" allowing it to pick new direction;

#### 5. Potential improvements
* Tune recovery strategies
* Direction prioritization is rather primitive. It only checks cells adjacent to current rover position. Some geofencing might be used here.
* Turn direction in "stop" mode is hardcoded, need better direction prioritization logic.
* Use camera image preprocessing to compensate roll and pitch angles, instead of discarding images where these angles beyond threshhold. I actually try to compensate roll using OpenCV warpAffine method, but not sure if it's optimal solution; 
* Sample spotting and collection routines need improvement. 
1. It's possible to miss samples when setting rover throttle to higher numbers;
2. Rover can "forget" where sample was if for some reason it gets off sight. Need to store last spotted sample coordinated until collected

#### 6. Screenshots
* There are some screenshots located in screenshot folder in this repository.


