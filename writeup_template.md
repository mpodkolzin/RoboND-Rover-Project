## Project: Search and Sample Return
### Writeup Template: You can use this file as a template for your writeup if you want to submit it as a markdown file, but feel free to use some other method and submit a pdf if you prefer.

---


**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook). 
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands. 
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  

[//]: # (Image References)

[image1]: ./misc/rover_image.jpg
[image2]: ./calibration_images/example_grid1.jpg
[image3]: ./calibration_images/example_rock1.jpg 

## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it!

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.
Here is an example of how to include an image in your writeup.

![alt text][image1]

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 
And another! 

![alt text][image2]
### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.


#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**


#### 1. Rover states
Rover is considered as state machine with the following states
	Main states:
	1. Forward
	2. Stop
	3. Sample spotted
	Additional states:
	4. Stuck
	5. Circling

##### Forward
	If rover is not stuck and not circling, check if there is enough of navigable terrain
##### Stop
	If robot is not stuck spin unless there are enough of navigable terrain and go
##### Sample spotted
	If there are distances from sample (obtained in perception step) then set navigation angle to the direction of sample, and decrease velocity when approaching 

##### Stuck
	"Stuck" here means that ground velocity of the rover does not change within specified timeinterval (defined as number of measurement cycles). After rover is marked as "stuck", recovery operation is performed (described below)

##### Circling
	Circling is a form of "stuck" when rover is unable to change direction, resulting in it driving in circles indefinitely (usually happens on wide open spaces). Rover marked as "Circling" when steering angle does not change from -15 or 15 within specified time interval (defined as number of measurement cycles), circling recovery is performed in this case (described below)

#### 2. Robot image processing

#### 3. Direction choosing and correction
#### 4. Recovery strategy
##### 1. Stuck recovery 
	To "unstuck" rover, it's throttle is set to negative number (driving backwards) for a specified time interval (defined as a number of measurment cycles)
##### 2. Circling recovery 
	To "uncircle" rover, it's steering angle is reset and mode is set to "stop" allowing it to pick new direction

#### 5. Potential improvements



![alt text][image3]


