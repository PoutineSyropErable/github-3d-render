import pygame #duh
import sys, os
os.chdir(sys.path[0])  #----This line of code sets the current working directory to the directory where the file is being runned, rather then just documents folder
from render_function_V3 import *
pygame.init() #Needed to get pygame initiated


#pygame boiler plate part 2
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("3d_renderer")
clock = pygame.time.Clock()


#--------------setting up the text
font = pygame.font.Font('freesansbold.ttf', 20)



#-------------------Defining the function that needs to be in this part
#making the general drawing code:
def draw_shape(shape,shape_face,player_pos,projection_matrix):
    ''' draws a shape on the screen. shape is the array wth all the vertexes, faces is the array with all the neighboor for each vertex. '''
    """ player_pos is the position of the player and camera_rot is the rotation of the camera"""
    shape_screen,object_order = render_shape_mesh(shape,all_neigh,player_pos,projection_matrix)
    for i in range(len(shape_face)): #
        for j in range(len(shape_face[i])):
            pygame.draw.line(screen, (100,100,100,80), b(shape_screen[i]),b(shape_screen[shape_face[i][j]]))

    """
    for i in range(len(shape_face)): #
        for j in range(len(shape_face[i])):
            pygame.draw.line(screen, "black", b(shape_screen[i]),b(shape_screen[shape_face[i][j]]))
    """


def pause(game_paused):
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            pygame.quit()
            #print("The program finished running \n \n")
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                #print("Test")
                game_paused = not game_paused
        
    pygame.display.update()
    clock.tick(20)
    return(game_paused)
#------------------------------------------------------End of the function that needs to be in this part

#-------Make the surfaces
white_surface = pygame.Surface((WIDTH,HEIGHT))
white_surface.fill("grey")



#--------------Initializing variables
player_pos = np.array([0,0,-10])
player_move_speed = 7/FPS_playing
player_move_vec = np.array([0,0,0])


camera_rot_y,camera_rot_x = 0,0
camera_rot_z = 0 #this won't change
camera_sensitivity_hor, camera_sensitivity_ver = 3 , 3
camera_rot = np.array([0,PI/2,PI/2])
camera_rot_speed_hor = 0.1/(FPS_playing) * camera_sensitivity_hor
camera_rot_speed_ver = 0.1/(FPS_playing) * camera_sensitivity_ver


cube_rot_speed = 0.02
cube_rot_x,cube_rot_y,cube_rot_z = 0,0,0
cube_stop = False


pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
pygame.mouse.set_pos(a(0,0))

#--------------------------------------------------------------The actual code being runned every frame
while True:
    ##print(player_pos)
    #adding a pause to the game:
    while game_paused:
        game_paused = pause(game_paused)
        

    #----------------------------------------------START OF MOUSE MOVEMENT CODE
    #Moving the camera with the mouse fps style
    mouse_change_rel = pygame.mouse.get_rel()
    if mouse_change_rel != (0,0):
        camera_rot_y += camera_rot_speed_hor*mouse_change_rel[0]
        camera_rot_x -= camera_rot_speed_ver*mouse_change_rel[1] #because the change in y coordinate, mobing the mouse down means a positive delta_mouse_y

        mouse_position = pygame.mouse.get_pos()#so the mouse stays in the screen
        if (mouse_position[0] <= W_BUFFER or mouse_position[0] >= WIDTH-W_BUFFER) or (mouse_position[1] <= H_BUFFER or mouse_position[1] >= HEIGHT-H_BUFFER): 
            pygame.mouse.set_pos(a(0,0))
        if camera_rot_x >= PI/2:
            camera_rot_x = PI/2
        if camera_rot_x <= -PI/2:
            camera_rot_x = -PI/2
    #--------------------------------------------------END OF MOUSE MOVEMENT CODE
    
    #-------------START OF PLAYER MOUVEMENT CODE------------------------------------------
        #These are the vector for movements
    movement_array = np.dot(Ry(camera_rot_y),Rz(camera_rot_z))
    movement_array = np.dot(Rx(camera_rot_x),movement_array)
    movement_array = np.transpose(np.array(movement_array)[0:3,0:3])
    movement_array[2,1] = 0
    movement_array[0,1] = 0
    movement_array[2] = movement_array[2] / norm(movement_array[2])
    movement_array[1] = movement_array[1] / norm(movement_array[1])

    keys = pygame.key.get_pressed()
    #movement keys
    player_move_vec = np.array([0,0,0])
    if keys[pygame.K_w]:
        player_move_vec = player_move_vec + movement_array[2] #using absolute positioning to simplify stuff
    if keys[pygame.K_s]:
        player_move_vec = player_move_vec - movement_array[2]
    if keys[pygame.K_d]:
        player_move_vec = player_move_vec + movement_array[0]
    if keys[pygame.K_a]:
        player_move_vec = player_move_vec - movement_array[0]
    if keys[pygame.K_SPACE]:
        player_move_vec = player_move_vec + np.array([0,1,0])
    if keys[pygame.K_LSHIFT]:
        player_move_vec = player_move_vec - np.array([0,1,0])

    if abs(norm(player_move_vec) - 1) > 0.1 and norm(player_move_vec) > 0.1  :
        player_move_vec = player_move_vec / norm(player_move_vec)

    player_pos = player_pos + player_move_speed*player_move_vec
    #-------------END OF PLAYER MOUVEMENT CODE------------------------------------------


    #Getting the event and single key press (Runs once when the key is pressed) +++++++ Making it quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            pygame.quit()
            #print("The program finished running \n \n")
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                game_paused = not game_paused

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: #r for resetting your position
                camera_rot_y,camera_rot_x = 0,0
                player_pos = np.array([0,0,-10])
            if event.key == pygame.K_e:
                player_pos = np.array([0,0,-10])
            if event.key == pygame.K_f:
                cube_stop = not cube_stop
                
    
    #--------------# creating the projection matrix
    translation_matrix = np.matrix([[ 1 , 0 , 0 , -player_pos[0]],
                                    [ 0 , 1 , 0 , -player_pos[1]],
                                    [ 0 , 0 , 1 , -player_pos[2]],
                                    [ 0 , 0 , 0 ,       1       ]])
    rotation_matrix = np.dot(Ry(-camera_rot_y),Rz(-camera_rot_z))
    rotation_matrix = np.dot(Rx(-camera_rot_x),rotation_matrix)
    projection_matrix = np.dot(rotation_matrix,translation_matrix)
    

    #rendering the cube calculations
    camera_angle = np.array([camera_rot_y,camera_rot_x])
    cube_rot = [cube_rot_x,cube_rot_y,cube_rot_z]
    cube_screen, cube_order = render_cube(player_pos,projection_matrix,cube_rot)

    #-------- START OF DRAWING EVERYTHING------------------------------------- START OF DRAWING EVERYTHINg----------- START OF DRAWING EVERYTHING
    screen.fill("grey")
    #screen.blit(white_surface,(0,0))   #- this is kept so i remember screen.blit(surface,position)

    for i in (cube_order):
        pygame.draw.polygon(screen,color_face[i],[b(cube_screen[face[i,0]]),b(cube_screen[ face[i,1]  ]),b(cube_screen[  face[i,2]  ]),b(cube_screen[   face[i,3] ])])


    draw_shape(grid,all_neigh,player_pos,projection_matrix)
    

    #the cursor
    pygame.draw.line(screen,"gold",a(-10,0),a(10,0))
    pygame.draw.line(screen,"gold",a(0,-10),a(0,10))

    #---------THE TEXT    
    player_pos_text = font.render('player pos = ' + str(  np.round(player_pos,2)  ), True, (0,0,0),)
    text_pos_Rect = player_pos_text.get_rect(center= a(int(0.6*WIDTH/2),int(0.75*HEIGHT/2)))
    screen.blit(player_pos_text, text_pos_Rect)

    player_angle_text = font.render('[phi, theta] = ' + str(  np.round(180/PI*camera_angle,2)  ), True, (0,0,0))
    text_angle_Rect = player_angle_text.get_rect()
    text_angle_Rect.center = a(0.6*WIDTH/2,0.65*HEIGHT/2)
    screen.blit(player_angle_text, text_angle_Rect)
    #-------- END OF DRAWING EVERYTHING------------------------------------- END OF DRAWING EVERYTHING----- END OF DRAWING EVERYTHING----- END OF DRAWING EVERYTHING-----

    


    #update everything (except player mouvement and mouse movement (so everything that moved during the frame thats not directly player input))
    #So, if my input makes an entity move (indirectly), the code to change said entity is here (let's say it's due to the entity reaction time of 1 frame)
    cube_rot_x += cube_rot_speed*(not cube_stop)
    cube_rot_y += random.random()*cube_rot_speed*(not cube_stop)
    cube_rot_z += m.sqrt(2)*cube_rot_speed*(not cube_stop)

    
    #the final two lines
    pygame.display.update()
    clock.tick(FPS_playing)






