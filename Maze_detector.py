import numpy as np
import cv2
import csv


#To know which path is explorable from a a given encoded node.
def cell(no):
	s = "{:04b}".format(no)
	left, top, right, bottom = int(s[3]), int(s[2]), int(s[1]), int(s[0])
	return [left, top, right, bottom]

visited = [[0 for _ in range (10)] for _ in range (10)]
final = []

# start --> tuple, end --> tuple, maze --> list of list and path --> list of tuples
def dfs_util(start, end, maze):
    global final
    final = []
    visited[start[0]][start[1]] = 1

    def dfs(node, path, vis):
        if node == end:

            for i in path:
                final.append(i)
            return True
        
        i, j = node[0], node[1]
        
        if i < 0 or i > 9 or j  < 0 or j > 9:
            return False


        left, top, right, bottom = cell(maze[i][j])
        # print(left, top, right, bottom)
        if not left:
            if not vis[i][j-1]:

                vis[i][j-1] = 1
                path.append((i, j-1))
                # print(path)
                if not dfs((i, j-1), path, vis):
                    path.pop()

        
        if not top:
            if not vis[i-1][j]:
                vis[i-1][j] = 1
                path.append((i-1, j))
                # print(path)
                if not dfs((i-1, j),path , vis):
                    path.pop()

        if not right:
            if not vis[i][j+1]:
                vis[i][j+1] = 1
                path.append((i, j+1))

                if not dfs((i, j+1),path , vis):
                    path.pop()


        if not bottom:
            if not vis[i+1][j]:

                vis[i+1][j] = 1
                path.append((i+1, j))
  
                if not dfs((i+1, j),path , vis):
                    path.pop()

        else:
            return False

    return dfs(start, [start], visited)


def applyPerspectiveTransform(input_img):

    warped_img = None
    img = cv2.cvtColor(input_img , cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(img,(7,7),2)
    thresh = cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    thresh = cv2.bitwise_not(thresh)
    cnts,_ = cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    c = max(cnts,key=cv2.contourArea)
    approx = cv2.approxPolyDP(c,0.01*cv2.arcLength(c,True),True)
    pt1 = []

    pt1.append([approx[0][0][0],approx[0][0][1]])
    pt1.append([approx[3][0][0],approx[3][0][1]])
    pt1.append([approx[1][0][0],approx[1][0][1]])
    pt1.append([approx[2][0][0],approx[2][0][1]])

    pt2 = np.float32([[0,0],[500,0],[0,500],[500,500]])
    matrix = cv2.getPerspectiveTransform(np.float32(pt1),pt2)
    warped_img = cv2.warpPerspective(input_img,matrix,(500,500))

    return warped_img


def detectMaze(warped_img):

    maze_array = []

    result = cv2.cvtColor(warped_img,cv2.COLOR_BGR2GRAY)
    _,result =  cv2.threshold(result,120,255,cv2.THRESH_BINARY)
    result[:][0:3] = 0;
    result[0:2][:] = 0;
    result[:][496:500] =0;
    result[496:500][:] = 0;
    for r in range(0,10):
        edge = []
        for c in range(0,10):
            if(c==0):
                left = 1
            else:
                left = (not(result[r*50+25][c*50]))*1
            if(r==0):
                up = 2
            else:
                up = (not(result[r*50][c*50+25]))*2
            if(c==9):
                right = 4
            else:
                right = (not(result[r*50+25][c*50+50]))*4
            if(r==9):
                down = 8
            else:
                down = (not(result[r*50+50][c*50+25]))*8
            edge.append(left+up+right+down)
        maze_array.append(edge)

    return maze_array



if __name__ == "__main__":

    img_file_path = 'test_cases/maze00.jpg'

    input_img = cv2.imread(img_file_path)

    warped_img = applyPerspectiveTransform(input_img)

    if type(warped_img) is np.ndarray:

        maze_array = detectMaze(warped_img)

        # Mention the starting and ending coordinates of the Maze
        st, en = (0, 4), (9,5)

        if (type(maze_array) is list) and (len(maze_array) == 10):

            

            print('\nEncoded Maze Array = %s' % (maze_array))
            
            dfs_util(st, en, maze_array)
            print()
            print(f"********* THE PATH FROM {st} --> {en} is ***************************")
            print(final)

            cv2.imshow('warped_img_0',  warped_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()