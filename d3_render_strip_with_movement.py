import numpy as np
import math as m
import pygame, sys, random
pygame.init() #Needed to get pygame initiated

print("\n"*20+"-"*11,"start of program","-"*11)
#---------------------------------------------------------Start of math construct
#defining constants
PI = m.pi
WIDTH , HEIGHT = 1920, 1080
W_BUFFER, H_BUFFER = 40,40 #for when the camera moves off screen
aspect_ratio = WIDTH/HEIGHT
fov = 55 * PI/180
f = 0.1
Px = 0.06
Py = 0.048

#------ START of initialising the player and camera variables variables.
player_pos = np.array([0,0,-10])
player_move_speed = 4 / 30
player_move_vec = np.array([0,0,0]) #that's the velocity vector


camera_rot_y = 0 
camera_rot_x = 0 
camera_rot_z = 0 #we don't use that one

camera_sensitivity_hor, camera_sensitivity_ver = 3 , 3
camera_rot_speed_hor = 0.1/30 * camera_sensitivity_hor
camera_rot_speed_ver = 0.1/30 * camera_sensitivity_ver
#------ END of initialising the player and camera variables variables.

#defining math functions
def a(x,y): # it's to put (0,0) at the center of the screen
    ''' (num,num) -> (num,num)
    takes a coordinates in cartesian and output the number in shitty 
    coordinates png style
    '''
    return(x + WIDTH/2,HEIGHT/2 - y)

def b(array):
    ''' (array or list) -> list
    takes an arrray corresponding to a coordinates in cartesian
    | output the coordinate in array form in a shitty png style'''
    return(a(array[0],array[1]))

def Rx(rot_x):  #The rotation matrix over the x axis
    z   = np.matrix([
    [ 1, 0, 0, 0],
    [ 0, m.cos(rot_x), m.sin(rot_x), 0],
    [ 0, -m.sin(rot_x), m.cos(rot_x), 0],
    [ 0, 0, 0, 1 ]
    ])
    return(z)

def Ry(rot_y):#The rotation matrix over the y axis
    z = np.matrix([
    [ m.cos(rot_y), 0,m.sin(rot_y), 0],
    [ 0, 1, 0, 0],
    [ -m.sin(rot_y), 0, m.cos(rot_y), 0],
    [ 0, 0, 0, 1 ],
    ])
    return(z)

def Rz(rot_z): #The rotation matrix over the z axis
    z = np.matrix([
    [ m.cos(rot_z), m.sin(rot_z), 0, 0],
    [- m.sin(rot_z), m.cos(rot_z), 0, 0],
    [ 0, 0, 1, 0],
    [ 0, 0, 0, 1 ]
    ])
    return(z)

#----------------------------------------------------------------------End of math construct.
#initialising the cube:
cube_ini = []

for i in [-1,1]:
    for j in [-1,1]:
        for k in [-1,1]:
            if [i,j,k] == [0,1,0]:
                print("Yo")
            cube_ini.append([i,j,k,1])
cube = np.matrix(np.transpose(cube_ini))

face= np.array([ [0,2,3,1] , [0,1,5,4], [2,6,7,3], [4,5,7,6], [1,3,7,5] , [0,4,6,2]])


#---------the color of each line in the cube mesh
color_array = []
for i in range(36):
    color_array.append([int(255*random.random()),int(255*random.random()),int(255*random.random())])



#----------------------------------------------------pygame boiler plate part 2
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("3d_renderer")
clock = pygame.time.Clock()

pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
pygame.mouse.set_pos(a(0,0))
#-----------------------------------------------------------Start of animation code
while True:
    movement_array = np.dot(Ry(camera_rot_y),Rz(camera_rot_z))
    movement_array = np.dot(Rx(camera_rot_x),movement_array)
    movement_array = np.transpose(np.array(movement_array)[0:3,0:3])
    movement_array[2,1] = 0
    movement_array[0,1] = 0

    

    keys = pygame.key.get_pressed()
    #The movement keys
    if keys[pygame.K_w]:
        player_move_vec = movement_array[2] #using absolute positioning to simplify stuff
    elif keys[pygame.K_s]:
        player_move_vec = -movement_array[2]
    elif keys[pygame.K_d]:
        player_move_vec = movement_array[0]
    elif keys[pygame.K_a]:
        player_move_vec = -movement_array[0]
    elif keys[pygame.K_SPACE]:
        player_move_vec = np.array([0,1,0])
    elif keys[pygame.K_LSHIFT]:
        player_move_vec = -np.array([0,1,0])
    else:
        player_move_vec = np.array([0,0,0])

    mouse_change_rel = pygame.mouse.get_rel()
    if mouse_change_rel != (0,0):
        camera_rot_y += camera_rot_speed_hor*mouse_change_rel[0]
        camera_rot_x -= camera_rot_speed_ver*mouse_change_rel[1] #because the change in y coordinate, mobing the mouse down means a positive delta_mouse_y

    mouse_position = pygame.mouse.get_pos()
    if (mouse_position[0] <= W_BUFFER or mouse_position[0] >= WIDTH-W_BUFFER) or (mouse_position[1] <= H_BUFFER or mouse_position[1] >= HEIGHT-H_BUFFER):
        pygame.mouse.set_pos(a(0,0))
    if camera_rot_x >= PI/2:
        camera_rot_x = PI/2
    if camera_rot_x <= -PI/2:
        camera_rot_x = -PI/2

    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            pygame.quit()
            print("The program finished running \n \n")
            sys.exit()
        if keys[pygame.K_r]:
            pygame.mouse.set_pos(a(0,0))

    #Creating the projection matrix
    translation_matrix = np.matrix([[ 1 , 0 , 0 , -player_pos[0]],
                          [ 0 , 1 , 0 , -player_pos[1]],
                          [ 0 , 0 , 1 , -player_pos[2]],
                          [ 0, 0, 0, 1 ]])
    rotation_matrix = np.dot(Ry(-camera_rot_y),Rz(-camera_rot_z))
    rotation_matrix = np.dot(Rx(-camera_rot_x),rotation_matrix)
    projection_matrix = np.dot(rotation_matrix,translation_matrix)


    #making the calculation for the projection of the cube
    pos_cam_proj = np.dot(projection_matrix,cube)
    pos_cam_perspective = np.zeros((8,2))
    for i in range(8):
        pos_cam_perspective[i,0] =  0.5 * (1/m.tan(fov/2)) * HEIGHT * pos_cam_proj[0,i]  /pos_cam_proj[2,i] 
        pos_cam_perspective[i,1] =  0.5 * (1/m.tan(fov/2)) * HEIGHT  * pos_cam_proj[1,i]  /pos_cam_proj[2,i] 

    cube_screen = np.array(pos_cam_perspective)


    #-----------------------drawing the lines
    screen.fill("black")
    pygame.draw.line(screen,"gold",a(-10,0),a(10,0)) #the cursor
    pygame.draw.line(screen,"gold",a(0,-10),a(0,10)) #the cursor

    for i in range(6):
        for j in range(3): #
            pygame.draw.line(screen, "white", b(cube_screen[  face[i][j]  ][0:2]),b(cube_screen[face[i][j+1]][0:2]))



    #updating the player position
    player_pos = player_pos + player_move_speed*player_move_vec

    #---final two boiler plate lines
    pygame.display.update()
    clock.tick(30)#------------------------------------------------------------End of animation code