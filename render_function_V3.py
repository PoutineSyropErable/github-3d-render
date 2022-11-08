#importing the mathematical library

print("\n"*20+"-"*11,"start of program","-"*11)

import numpy as np
import math as m
import random
np.set_printoptions(suppress=True)

#setting constants:
PI = m.pi
WIDTH , HEIGHT = 1920,1080
W_BUFFER, H_BUFFER = 40,40 #for when the camera moves off screen
z_near, z_far = 0.4,40
fov = 50 * PI/180
game_paused = False
FPS_playing = 30

#creating a grid
GRID_MIN, GRID_MAX =  -3, 3
GRID_SIZE = 1

#setting cube faces: 1 5 4 0
face= np.array([ [0,2,3,1] , [0,1,5,4], [2,6,7,3], [4,5,7,6], [1,3,7,5] , [0,4,6,2]])
color_face = ["red", "green", "blue", "orange","white","black"]




#----------------------defining mathematical functions
def a(x,y):
    ''' (num,num) -> (num,num)
    takes a coordinates in cartesian and output the number in shitty 
    coordinates png style
    '''
    return(x + WIDTH/2,HEIGHT/2 - y)

def b(array):
    ''' (array or list) -> list
    takes an arrray corresponding to a coordinates in cartesian
    | output the coordinate in array form in a shitty png style'''

    ##print(array)
    return(a(array[0],array[1]))




def norm(array):
    """(array)-> (num)
    takes an array and return the euclidean norm"""
    return(np.linalg.norm(array))

#
def camera_cart(phi,theta):
    """(num,num)->[num,num,num]
    takes the angle phi and theta, a modified cylindrical coordinate system so that
    theta starts on the horizontal plane, not the z axis. So, z = l*sin(theta)
    return a numpy array representing a vector pointing in that direction in 3d cartesian
    """
    return(np.array([m.cos(theta)*m.cos(phi),m.cos(theta)*m.sin(phi),m.sin(theta)]))

def camera_3_angle(alpha,beta,gamma):
    '''(num,num,num)->[num,num,num]
    takes the 3 angles and returns a numpy array for a vector pointing foward'''
    return(np.array( [m.cos(alpha),m.cos(beta),m.cos(gamma)]))


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

def get_angle(array):
    """ returns the angle in the modified spherical coordinate system
    """
    array /= norm(array)
    ###print(array)
    x,y,z = tuple(array)

    z_2 = m.asin(z)
    if x == 0:
        if y >=0:
            z_1 = PI/2
        else:
            z_1 = -PI/2
    else:   
        z_1 = m.atan(y/x)
        if x < 0:
            z_1 = PI - z_1
    return([z_1,z_2])



cube_ini = []

for i in [-1,1]:
    for j in [-1,1]:
        for k in [-1,1]:
            cube_ini.append([i,j,k,1])

cube_ini = np.matrix(np.transpose(cube_ini))


def render_cube(camera_pos,projection_matrix,cube_rot=[0,0,0]):
    cube_rot_x, cube_rot_y, cube_rot_z = tuple(cube_rot)
    Rtot_cube = np.matmul(Rx(-cube_rot_x),Ry(-cube_rot_y))
    Rtot_cube = np.matmul(Rz(-cube_rot_z),Rtot_cube)
    ##print("")



    cube= np.dot(Rtot_cube,cube_ini)





    pos_cam_proj = np.dot(projection_matrix,cube)

    face_normal = []
    face_not_shown = []


    shape = (np.shape(pos_cam_proj)[1],3)
    pos_cam_perspective = np.zeros(shape)
    for i in range(shape[0]):
        pos_cam_perspective[i,0] =  0.5 * (1/m.tan(fov/2)) * HEIGHT * pos_cam_proj[0,i]  /pos_cam_proj[2,i] 
        pos_cam_perspective[i,1] =  0.5 * (1/m.tan(fov/2)) * HEIGHT  * pos_cam_proj[1,i]  /pos_cam_proj[2,i] 
        pos_cam_perspective[i,2] = (z_far/(z_far-z_near))*(pos_cam_proj[2,i] - z_near)
        if abs(pos_cam_perspective[i,0]) > WIDTH + 2*W_BUFFER or  abs(pos_cam_perspective[i,1]) >HEIGHT + 2*H_BUFFER or  pos_cam_perspective[i,2] > z_far or pos_cam_perspective[i,2] <z_near:
            face_not_shown.append(i)




    #----------------------------------------------------------------defining the face vectors:
    cube_array = np.transpose(np.array(cube))[:,0:3]
    #print(cube_array)
    
    for i in range(len(face)):
        vect1 =  cube_array[face[i,1]]-  cube_array[face[i,0]]
        #print(vect1)
        vect2 =  cube_array[face[i,2]] -  cube_array[face[i,1]]
        vect1 /=norm(vect1)
        vect2 /= norm(vect2)
        normal_vector = np.cross(vect1,vect2)
        face_normal.append(normal_vector)
        ###print("dot_result=",np.dot(normal_vector,-camera_pos/norm(camera_pos)))
        if np.dot(normal_vector,-camera_pos/norm(camera_pos)) <=0 and i not in face_not_shown:
            face_not_shown.append(i)

    face_not_shown = np.sort(face_not_shown)

    face_center_dist = []
    for i in range(len(face)):
        face_center_dist.append(norm(sum(cube_array[face[i]])/4-camera_pos))

    cube_order = list(np.flip(np.argsort(face_center_dist)))
    for i in face_not_shown:
        if i in cube_order:
            cube_order.remove(i)

#----------------------------------------------------------------end of definin the face vector




    ###print("The final result\n",pos_cam_perspective)



    #---------------------------------------------------------------old method------------------------------------------------------------------
    '''
    
    pos_decal_angle = []

    for i in range(len(cube)):
        ###print(pos_decal_dist[i])
        pos_decal_angle.append( get_angle(pos_decal[i]))
    pos_decal_angle = np.array(pos_decal_angle)

    ###print("\n",pos_decal_angle)

    rel_angle = pos_decal_angle - camera_angle

    

    rel_pos_screen = []
    for i in range(len(rel_angle)):
        rel_pos_screen.append([f*  (rel_angle[i,0])/pos_decal_dist[i]  ,f* (rel_angle[i,1])/pos_decal_dist[i] ])

    rel_pos_screen = np.array(rel_pos_screen)

    ###print("This is rel_pos_screen\n",rel_pos_screen,"\n this is the other method",pos_cam_proj) 
    
    '''
    #----------------------------End of the old method


    """ returning the final output"""
    ###print("------ \n This is the final result: \n",rel_pos_screen)
    return(pos_cam_perspective,cube_order)


camera_pos = np.array([-5,0,0])
camera_phi,camera_theta,camera_rot = 0.1,0.02, [0,0,0]
camera_angle = np.array([camera_phi,camera_theta])
#render_cube(camera_pos,camera_angle,camera_rot)







grid = []
for i in range(GRID_MIN,GRID_MAX+1):
    for j in range(GRID_MIN,GRID_MAX+1):
        for k in range(GRID_MIN,GRID_MAX+1):
            grid.append([GRID_SIZE*i,GRID_SIZE*j,GRID_SIZE*k,1])



next = np.array([     [GRID_SIZE,0,0,0] , [0,GRID_SIZE,0,0] , [0,0,GRID_SIZE,0]   ])
###print(next)
all_neigh = []

for i in range(len(grid)):
    neigh = []
    for j in range(3):
        if (grid[i]+next[j]).tolist() in grid:
            neigh.append(grid.index( (grid[i]+next[j]).tolist()  ))
    if neigh != []:
        all_neigh.append(neigh)

grid = np.matrix(np.transpose(grid))

###print("this is all neighboor:\n",all_neigh)





#-----------------------------------------------------------------Rendering the grid-----------------------------------------------

"""
def render_grid2(camera_pos,camera_rot):
    camera_rot_x,camera_rot_y,camera_rot_z = tuple(camera_rot)
    Rtot_camera = np.matmul(Rx(camera_rot_x),Ry(camera_rot_y))
    Rtot_camera = np.matmul(Rz(camera_rot_z),Rtot_camera)

    pos_decal = np.zeros(np.shape())

    pos_decal = grid - camera_pos
    pos_cam_proj = np.transpose(np.matmul(Rtot_camera,np.transpose(pos_decal)))
    

    pos_decal_dist = []
    for i in range(len(grid)):
        pos_decal_dist.append(norm(grid[i]-camera_pos))
    pos_decal_dist = np.array(pos_decal_dist)
    #qqq= np.shape(pos_cam_proj)
    ###print("\nqqq=",qqq,"\n")
    pos_cam_perspective = np.zeros(np.shape(pos_cam_proj) )
    for i in range(len(pos_cam_proj)):
        pos_cam_perspective[i,0] =  WIDTH * pos_cam_proj[i,0] * (1/m.tan(fov/2)) / pos_decal_dist[i]
        pos_cam_perspective[i,1] =  HEIGHT* pos_cam_proj[i,1] * (1/m.tan(fov/2)) /pos_decal_dist[i]
        pos_cam_perspective[i,2] = pos_decal_dist[i]

    return(pos_cam_perspective)
"""





#------------------------
#camera_rot_x,camera_rot_y,camera_rot_z = tuple(camera_rot)
#camera_phi, camera_theta = tuple(camera_angle)
#Rtot_camera = np.matmul(Ry(camera_theta),Rz(camera_phi))
"""
for i in range(len(pos_cam_proj)):
    pos_cam_perspective[i,0] =  WIDTH * pos_cam_proj[i,0] * (1/m.tan(fov/2)) / pos_decal_dist[i]
    pos_cam_perspective[i,1] =  HEIGHT* pos_cam_proj[i,1] * (1/m.tan(fov/2)) /pos_decal_dist[i]
    pos_cam_perspective[i,2] = pos_decal_dist[i]
"""

def render_shape_mesh_1(shape,projection_matrix):
    pos_cam_proj = np.dot(projection_matrix,shape)
    pos_cam_perspective = np.zeros( (np.shape(pos_cam_proj)[1],3) )
    for i in range((np.shape(pos_cam_proj)[1])):
        pos_cam_perspective[i,0] =  0.5 * (1/m.tan(fov/2)) * HEIGHT * pos_cam_proj[0,i]  /pos_cam_proj[2,i] 
        pos_cam_perspective[i,1] =  0.5 * (1/m.tan(fov/2)) * HEIGHT  * pos_cam_proj[1,i]  /pos_cam_proj[2,i] 
        pos_cam_perspective[i,2] = (z_far/(z_far-z_near))*(pos_cam_proj[2,i] - z_near)
        #if abs(pos_cam_perspective[i,0]) > WIDTH + 2*W_BUFFER or  abs(pos_cam_perspective[i,1]) >HEIGHT + 2*H_BUFFER or  pos_cam_perspective[i,2] > z_far or pos_cam_perspective[i,2] <z_near:
            #face_not_shown.append(i)
    return(pos_cam_perspective)




    



def render_shape_mesh_2(shape,shape_face,camera_pos,projection_matrix):
    face_not_shown = []
    face_center = []
    face_center_dist = []

    #------------------------------Creating the position of the center of the face
    for i in range(len(shape_face)):
        for j in shape_face[i]:
            if j != []:
                face_center.append(   (sum(shape[j])/len(shape_face[i])-camera_pos)   )

    #-------------------------------Getting the distance between the center of the face and you.
    for i in range(len(face_center)):
       # #print("face center=")
        face_center_dist.append(norm(face_center[i]))
    #print("face_center_dist=",face_center_dist)

    #------------------Getting the position on the screen of the center of the faces.
    face_center_screen = render_shape_mesh_1(face_center,camera_pos,projection_matrix)

    #------------------Removing those with a face center located outside the screen
    for i in range(len(face_center_screen)):
        if abs(face_center_screen[i,0]) > WIDTH/2 + W_BUFFER or  abs(face_center_screen[i,1]) > HEIGHT/2 + H_BUFFER or  face_center_screen[i,2] > z_far or face_center_screen[i,2] <z_near:
            face_not_shown.append(i)


    object_order = list(np.flip(np.argsort(face_center_dist)))
    #print("object order before removal=",object_order)
    #print("face not shown order=",face_not_shown)


    for i in face_not_shown:
        if i in object_order:
            ##print("i=",i)
            object_order.remove(i)
    #print("object order after removal=",object_order)
    return(object_order)



def render_shape_mesh(shape,shape_face,camera_pos,projection_matrix):
    pos_cam_perspective =  render_shape_mesh_1(shape,projection_matrix)
    object_order = 0 #render_shape_mesh_2(shape,shape_face,camera_pos,projection_matrix)

    return(pos_cam_perspective,object_order)

def render_grid(camera_pos,camera_rot,Rtot_camera_2):
    return(render_shape_mesh(grid,all_neigh,camera_pos,camera_rot,Rtot_camera_2))

#render_grid(np.array([-5,0,0]),np.array([PI/2,0,0]))
