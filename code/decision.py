import numpy as np
from perception import *
import random


def decision_step(Rover):

    if Rover.nav_angles is not None:
           
        if Rover.mode == 'sample_spotted':
            print('sample spotted')
            #if is_stuck(Rover):
            #    Rover.mode = 'stuck'
            if Rover.near_sample:
                Rover.brake = Rover.brake_set
                if Rover.vel == 0 and not Rover.picking_up:
                    Rover.send_pickup = True
                elif Rover.picking_up:
                    Rover.samples_collected += 1
                    Rover.mode = 'stop'
            elif(Rover.sample_angles is not None and len(Rover.sample_angles) > 0):
                sample_dist = np.min(Rover.sample_dists)
                print(sample_dist)
                if(sample_dist < 20.0 and Rover.vel > 0.5):
                    Rover.brake = Rover.brake_set
                elif(Rover.vel < 0.5):
                    Rover.brake = 0
                    Rover.throttle = Rover.throttle_set / 2
                else:
                    pass
                    
                Rover.steer = np.clip(np.mean(Rover.sample_angles * 180 / np.pi), -15, 15)

            elif len(Rover.sample_angles) == 0:
                #Rover.mode = 'forward'
                pass

        elif Rover.mode == 'stuck':
            print('stuck')
            perform_recovery(Rover)

        elif Rover.mode == 'circling':
            print('circling')
            perform_circling_recovery(Rover)
        elif Rover.mode == 'forward':
            print('forward')
            # Check the extent of navigable terrain
            navigable_dist = np.mean(Rover.nav_dists)
            if is_stuck(Rover):
                Rover.mode = 'stuck'
            elif is_circling(Rover):
                Rover.mode = 'circling'
            elif(len(Rover.sample_dists) > 0):
                Rover.mode = 'sample_spotted'
                Rover.brake = Rover.brake_set
                Rover.throttle = 0
                Rover.steer = np.clip(np.mean(Rover.sample_angles * 180/np.pi), -15, 15)
                
            elif (len(Rover.nav_angles) >= Rover.stop_forward and navigable_dist
            > 20):
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                Rover.prev_vel = Rover.vel
                # Set steering to average angle clipped to the range +/- 15
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                get_direction(Rover)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif (len(Rover.nav_angles) < Rover.stop_forward or navigable_dist
            <= 20):
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

        elif Rover.mode == 'stop':
            print('stop')
            steer_angle = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15,15)
            if is_stuck(Rover):
                Rover.mode = 'stuck'
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    Rover.steer = -15 # Could be more clever here about which way to turn
                    #if(len(Rover.nav_angles) > 0):
                    #    if(abs(np.min(Rover.nav_angles)) < abs(np.max(Rover.nav_angles))):
                    #        Rover.steer = -15 # Could be more clever here about which way to turn
                    #    else:
                    #        Rover.steer = 15 # Could be more clever here about which way to turn
                    #else:
                    #    Rover.steer = random.choice[-1, 1] * 15

                if (len(Rover.nav_angles) >= Rover.go_forward):
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    #Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.steer = steer_angle
                    Rover.mode = 'forward'
    # Just to make the rover do something 
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0
    
    return Rover

def is_stuck(Rover):
    if (abs(Rover.vel) <= 0.05):
        Rover.stuck_cycles += 1
        print('Rover stuck cycles {0}'.format(Rover.stuck_cycles))
    else:
        Rover.stuck_cycles = 0

    if(Rover.stuck_cycles >= Rover.stuck_set):
        return True;
    else:
        return False;

def perform_recovery(Rover):
    print('Trying to recover, recovery cycle {0}'.format(Rover.recovery_cycles))
    Rover.brake = 0
    Rover.steer = -Rover.steer
    Rover.throttle = -2

    if Rover.recovery_cycles >= Rover.recovery_set:
        Rover.mode = 'forward'
        Rover.stuck_cycles = 0
        Rover.recovery_cycles = 0
    else:
        Rover.recovery_cycles += 1

def is_circling(Rover):
    if abs(Rover.steer) >= 14.5:
        Rover.circling_cycles += 1
    else:
        Rover.circling_cycles = 0
    if(Rover.circling_cycles >= Rover.circling_set):
        return True;
    else:
        return False;

def perform_circling_recovery(Rover):
    print('Trying to recover from circling')
    Rover.mode = 'stop'
    Rover.circling_cycles = 0
    Rover.steer = random.randint(-15, 15)

def get_direction(Rover):
    x = np.floor_divide(Rover.pos[0], 10).astype(np.int)
    y = np.floor_divide(Rover.pos[1], 10).astype(np.int)
    res = []
    print('{0}:{1}'.format(x,y))
    if  0 <= Rover.yaw < 90:
        res.append((Rover.visited_map[y+1, x], y+1, x))
        res.append((Rover.visited_map[y+1, x+1], y+1, x+1))
        res.append((Rover.visited_map[y, x+1], y, x + 1))
    elif 90 <= Rover.yaw < 180:
        res.append((Rover.visited_map[y+1, x], y+1, x))
        res.append((Rover.visited_map[y+1, x-1], y+1, x-1))
        res.append((Rover.visited_map[y, x-1], y, x-1))
    elif 180 <= Rover.yaw < 270:
        res.append((Rover.visited_map[y, x-1], y, x-1))
        res.append((Rover.visited_map[y-1, x-1], y-1, x-1))
        res.append((Rover.visited_map[y-1, x], y-1, x))
    else:
        res.append((Rover.visited_map[y, x+1], y, x+1))
        res.append((Rover.visited_map[y-1, x+1], y-1, x+1))
        res.append((Rover.visited_map[y-1, x], y-1, x))

    weight, y_vis, x_vis = min(res, key = lambda t: t[0])
    if(weight == 0):
        Rover.steer += 5
    elif(y_vis != y):
        Rover.steer += 10
    elif(x_vis != x):
        Rover.steer -= 10
    



