import asyncio

class Node:

    def __init__(self,state,coords, parent,boxes,keeper, cost=None, heuristic=None,):
        self.state  = state
        self.coords = coords
        self.parent = parent
        self.heuristic = heuristic
        self.cost = cost
        self.totalCost = 0
        self.path = []
        self.boxes = boxes
        self.keeper = keeper
    
    def __str__(self):
        return f"nó ({self.coords},{self.state})) \n"
    
    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.coords == other.coords

    def __lt__(self,other):
        return self.totalCost < other.totalCost

# Manhattan distance
def heuristic(pos,end_pos):
        return abs(pos[0] - end_pos[0]) + abs(pos[1] - end_pos[1])

# Algorithm for the valid game states. returns path of the keeper
async def generate_game_states(grid,boxes,keeper):
    #hashtable with all current searched states, to avoid repetition
    searched_states={}

    # Initialize both open and closed list
    open_list = []

    # Add both boxes to open positions
    for box in boxes:
        open_list.append(Node(grid,box,None,boxes,keeper))

    # Loop until you find the end
    while len(open_list) > 0:
        # Get the current node
        current_node = open_list.pop(0)
        #children
        children = []

        # Found the goal
        if is_solved(current_node.state):
            print("solved")
            print("searched states = ",len(searched_states))
            return current_node.path

        # possible moves
        adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0))

        current_state = [line[:] for line in current_node.state]

        #For every move possible , calculate it's map states
        for box in current_node.boxes: # The boxes in any given state

            valid_positions = get_valid_positions(current_node.state,box)

            for positions in valid_positions: # Valid adjacent squares

                new_node_position = (box[0] + positions[0],box[1]+positions[1])
                new_map_state,new_boxes,new_keeper = update_grid(current_node,box,new_node_position)
        

                # if the state hasn't been searched, we add it 
                if str(new_map_state) not in searched_states:
                    keys = get_keeper_moves(current_node,box,positions)
                    # if there are valid keeper moves, then we add that move to the tree of valid game states
                    if keys != None:
                        #hashtable with the state, and the keeper position in that state
                        searched_states[str(new_map_state)] = new_keeper
                        new_node = Node(new_map_state,new_node_position,current_node,new_boxes,new_keeper)
                        new_node.path = current_node.path + keys

                        # Append
                        open_list.append(new_node) 
                          
        await asyncio.sleep(0)

# Get grid-like map and boxes coordinates, and goal coordinates  | status: done
def get_grid(map_lvl):

    mapa = open(map_lvl,'r')
    grid = []
    boxes = []
    goals = []
    keeper = ()
    
    #create grid
    x=y=0
    for line in mapa:
        row = []
        for symbol in line:
            if symbol == "-":
                row.append(0)
            if symbol == "#":
                row.append(1)   
            if symbol == ".":
                row.append(2)
                goals.append((x,y))
            if symbol == "@":
                keeper=(x,y)
                row.append(4)
            if symbol == "+":
                keeper=(x,y)
                goals.append((x,y))
                row.append(6)
            if symbol == "$":
                boxes.append((x,y))
                row.append(3)
            if symbol == "*":
                boxes.append((x,y))
                goals.append((x,y))
                row.append(5)
            x += 1
        grid.append(row)
        y += 1
        x = 0


    return grid,boxes,keeper,goals

# Check if push is valid in a given state | status: done | optimised
def is_push_valid(grid,start_position,push_dir):
    x = start_position[0]
    y = start_position[1]
    end_pos = (start_position[0]+push_dir[0],start_position[1]+push_dir[1])
    
    # Depending on the direction, we must assure that the keeper can go to the opposite position in order to push the box
    sym_push_dir = (-push_dir[0],-push_dir[1])

    #Direction can be Up -> (0,-1), Down -> (0,1), Left -> (-1,0) or Right -> (1,0)
    if(grid[y+sym_push_dir[1]][x+sym_push_dir[0]]) != 1 and grid[y+sym_push_dir[1]][x+sym_push_dir[0]] != 3 and grid[y+sym_push_dir[1]][x+sym_push_dir[0]] != 5:
        # Make sure that the final position isn't a wall, or a box, or a box_on_goal, or a deadlock state
        if grid[end_pos[1]][end_pos[0]] != 1 and grid[end_pos[1]][end_pos[0]] != 3 and grid[end_pos[1]][end_pos[0]] != 5 and grid[end_pos[1]][end_pos[0]] != 9 and grid[end_pos[1]][end_pos[0]] != 10:
            return True
        else:
            return False
    else:
        return False

# Get path | status: done
def get_path(node):
    if node.parent is None:
        return [node.coords]
    path = get_path(node.parent)
    path += [node.coords]
    return path

# Updates the state of the grid based on the move | status: done
def update_grid(node,box,new_position):
    # 0 means, it's a floor tile
    # 3 means, it's a box
    # 5 means, it's a bon on goal
    # 9 means, it's a deadlocked state
    # 10 means, it's a keeper on a deadlocked state
    new_grid = [line[:] for line in node.state]

    #get keeper starting position
    keeper_pos = node.keeper
    new_keeper = (box[0],box[1])

    #remove old keeper pos
    if new_grid[keeper_pos[1]][keeper_pos[0]] == 4:
        new_grid[keeper_pos[1]][keeper_pos[0]] = 0
    elif new_grid[keeper_pos[1]][keeper_pos[0]] == 6:
        new_grid[keeper_pos[1]][keeper_pos[0]] = 2
    elif new_grid[keeper_pos[1]][keeper_pos[0]] == 10:
        new_grid[keeper_pos[1]][keeper_pos[0]] = 9

    #if the coordinates of the new positions, are a box tile
    if new_grid[new_position[1]][new_position[0]] == 0:
        # we set the new position as a tile with a box
        new_grid[new_position[1]][new_position[0]] = 3
        # the old position now holds the keeper, or keeper on goal, because of the push
        if new_grid[box[1]][box[0]] == 3:
            new_grid[box[1]][box[0]] = 4
        elif new_grid[box[1]][box[0]] == 5:
            new_grid[box[1]][box[0]] = 6
        
    #if the coordinates are a box on a goal, we update accordingly
    elif new_grid[new_position[1]][new_position[0]] == 2:
        # we set the new position as a tile with a box
        new_grid[new_position[1]][new_position[0]] = 5
        # the old position now holds the keeper, or keeper on goal, because of the push
        if new_grid[box[1]][box[0]] == 3:
            new_grid[box[1]][box[0]] = 4
        elif new_grid[box[1]][box[0]] == 5:
            new_grid[box[1]][box[0]] = 6

    #on the array of boxes of the node, we update the box that was moved
    new_boxes = [line for line in node.boxes]
    for i,b in enumerate(new_boxes):
        if b == box:
            new_boxes[i] = new_position

    return new_grid,new_boxes,new_keeper

# Check if keeper can get behind the box to make the push | status: done
def get_keeper_moves(node,box,push_dir):
    #get keeper starting position
    keeper_start = node.keeper

    #keeper should end at the opposite side of the push direction
    keeper_end = (box[0]-push_dir[0],box[1]-push_dir[1])

    path = a_star_keeper(node.state,keeper_start,keeper_end)
    if path != None:
        keys = translate_path(path)
        #to the path, we add the push direction
        if push_dir == (0,1):
            keys += "s"
        if push_dir == (0,-1):
            keys += ("w")
        if push_dir == (1,0):
            keys +=("d")
        if push_dir == (-1,0):
            keys += ("a")
        return keys
    else:
        return None

# Check if it's solved, basically, if the number of 5, equals the number of boxes  | status: done
def is_solved(state):

    #if it doesnt find any 3 (box), it means they are all [box on goal]
    for y in state:
        for x in y:
            if x == 3:
                return False

    return True

# Translate the sequence of keeper positions, into a 'wasd' sequence
def translate_path(path):
    key = []
    for i in range(0,len(path)-1):
        move = (path[i+1][0]-path[i][0],path[i+1][1]-path[i][1])
        if move == (0,1):
            key += "s"
        if move == (0,-1):
            key += ("w")
        if move == (1,0):
            key +=("d")
        if move == (-1,0):
            key += ("a")    

    return key

# grid will only have walls, goals, and floor tiles
def clean_grid(grid,deadlock=False):

    if deadlock:
        new_grid = [line[:] for line in grid]
        x=y=0
        for y_c in grid:
            for x_c in y_c:
                if (x_c == 4 or x_c == 3):
                    new_grid[y][x] = 0
                if (x_c == 6 or x_c == 5):
                    new_grid[y][x] = 2    
                x += 1
            y += 1
            x = 0
        return new_grid
    else:
        # we want to preserve the boxes on the state
        new_grid = [line[:] for line in grid]
        x=y=0
        for y_c in grid:
            for x_c in y_c:
                if (x_c == 4):
                    new_grid[y][x] = 0
                if (x_c == 6):
                    new_grid[y][x] = 2    
                x += 1
            y += 1
            x = 0
        return new_grid

# From a given map, put it's deadlocked squares as 9
def set_deadlocked_pos(grid,goals):
    new_grid = [line[:] for line in grid]
      
    # we clean the map, meaning it's only walls, floor, and goals
    clean = clean_grid(new_grid,True)


    # now, for each map position, we check if
    # there's a sequence of moves to any of the goals
    # if there isn't, it means that square is a deadlocked square
    # Number 9 on  a grid means it's a deadlock

    path = []
    is_dead = True
    x=y=0
    for y_c in clean:
        for x_c in y_c:
            # we dont test for walls
            if(clean[y][x] == 0):
                for goal in goals:
                    path = (bfs_deadlock_detection(clean,(x,y),goal))
                    # if there is at least one path, it isn't a deadlock
                    if path != None:
                        is_dead = False
                # if for both goals, that square didn't produce a path to a goal, it's deadlocked
                if is_dead:
                    if new_grid[y][x] == 0:
                        new_grid[y][x] = 9
                    # keeper on deadlocked state    
                    if new_grid[y][x] == 4:
                        new_grid[y][x] = 10
            path = None
            is_dead = True
            x += 1
        y += 1
        x = 0
   
    return new_grid

# Breadth first search algorithm but to check if there's a sequence of moves that can
# get a box in a certain position to any of the goals. It's used to check if
# a certain position is a deadlock
# status: done
def bfs_deadlock_detection(grid,start,end):
    
    # Create start and end node
    start_node = Node(None,start,None,None,None)
    end_node = Node(None,end,None,None,None)
    searched = {}
    # Initialize both open and closed list
    open_list = []

    # Heapify the open_list and Add the start node
    # heapq.heapify(open_list)  <- not necessary probably
    open_list.append(start_node)

    # what squares do we search
    adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0))

    # Loop until you find the end
    while len(open_list) > 0:
        
        # Get the current node
        current_node = open_list.pop()

        # Found the goal
        if current_node == end_node:
            return get_path(current_node)

        # Generate children
        children = []
        
        for new_position in adjacent_squares: # Adjacent squares

            # Get node position
            node_position = (current_node.coords[0] + new_position[0], current_node.coords[1] + new_position[1])

            # Make sure the the grid point is a walkable space for the keeper
            try:
                if is_push_valid(grid,current_node.coords,new_position):
                    # Create new node
                    # new_node = Node(state,current_node, node_position)
                    new_node = Node(None,node_position,current_node,None,None)

                    # Append
                    if new_node.coords not in searched:
                        searched[new_node.coords] = "visited"
                        open_list.append(new_node)
            
            # it means we tried to calculate positions on a floor node
            # thats outside the walkable area. Happens on some maps that fill
            # empty positions to the left with floor tiles
            except IndexError:
                return None

# Get the valid positions of a certain box in a given state
def get_valid_positions(state,box):
    # possible moves
    adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0))
    possible_moves=[]


    for adjacent in adjacent_squares:
        if is_push_valid(state,box,adjacent):
                possible_moves.append(adjacent)

    return possible_moves

# A star algorithm for the keeper to push a box
def a_star_keeper(grid,start,end):
    # Create start and end node
    start_node = Node(None,start,None,None,None,0,heuristic(start,end))
    end_node = Node(None,end,None,None,None)
    searched = {}
    # Initialize both open and closed list
    open_list = []
    closed_list = []

    open_list.append(start_node)
    # what squares do we search
    adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0))

    # Loop until you find the end
    while len(open_list) > 0:
        
        # Get the current node
        current_node = open_list.pop(0)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            return get_path(current_node)

        # Generate children
        children = []
        
        for new_position in adjacent_squares: # Adjacent squares

            # Get node position
            node_position = (current_node.coords[0] + new_position[0], current_node.coords[1] + new_position[1])

            # Make sure the the grid point is a walkable space for the keeper

            keeper_new_pos = grid[node_position[1]][node_position[0]]
            if keeper_new_pos == 0 or keeper_new_pos == 2 or keeper_new_pos == 4 or keeper_new_pos == 6 or keeper_new_pos == 9:
                # Create new node
                # new_node = Node(current_node, node_position)
                new_node = Node(None,node_position,current_node,None,None)

                # Append
                if new_node.coords not in searched:
                    searched[new_node.coords] = "visited"
                    children.append(new_node)

        # # Loop through children
        for child in children:
            child.cost = current_node.cost + 1
            child.heuristic = heuristic(child.coords,end_node.coords)
            child.totalCost = child.cost + child.heuristic
            open_list.append(child)

    # Optimization, sort by heuristic + cost
    open_list = sorted(open_list,key = lambda n: n.totalCost)

# Get heuristic of the state, based on the distance from the boxes to the goals
def get_heuristic(boxes,goals):
    totalHeuristic = 0
    for box in boxes:
        closest = heuristic(box,goals[0])
        for goal in goals:
            dist = heuristic(box,goal)
            if dist < closest:
                closest = dist
    totalHeuristic += closest

    return totalHeuristic
