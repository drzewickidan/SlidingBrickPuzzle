from copy import deepcopy
from random import choice

move = {'left': (0, -1),
        'right': (0, 1),
        'up': (-1, 0),
        'down': (1, 0)
        }


class Node(object):
    """Represents a node in a n-ary graph."""
    def __init__(self, data, parent=None, move=None):
        self.parent = parent
        self.data = data
        self.move = move
        self.depth = parent.depth + 1 if parent is not None else 0

    def children(self):
        """Return a list of children by applying all possible moves to the board."""
        children = []
        for m in self.data.find_moves():
            child = SlidingBricks(self.data.w, self.data.h, self.data.move(*m))
            child.normalize()
            children.append(Node(child, parent=self, move=m))
        return children


class SlidingBricks:
    """Represents the Sliding Bricks game board."""
    def __init__(self, w, h, board):
        self.w = w
        self.h = h
        self.board = board

    def normalize(self):
        """Standardize board numbers for comparision."""
        next_idx = 3
        for x in range(self.h):
            for y in range(self.w):
                if self.board[x][y] == next_idx:
                    next_idx += 1
                elif self.board[x][y] > next_idx:
                    self.__swap_idx(next_idx, self.board[x][y])
                    next_idx += 1

    def __swap_idx(self, idx1, idx2):
        for x in range(self.h):
            for y in range(self.w):
                if self.board[x][y] == idx1:
                    self.board[x][y] = idx2
                elif self.board[x][y] == idx2:
                    self.board[x][y] = idx1

    def is_clone(self, state):
        """Compare this board to another. Unused."""
        return self.board == state

    def print_state(self):
        """Print the current board to the screen."""
        print("%s,%s," %(self.w, self.h))
        print(',\n'.join(','.join(map(str, sl)) for sl in self.board) + ',')

    def clone_state(self):
        """Returns a copy of the current board."""
        return deepcopy(self.board)

    def move(self, piece, direction):
        """Makes a move on a clone of the board and returns it. Does not affect current board."""
        locations = []
        board = self.clone_state()
        for x, j in enumerate(self.board):
            for y, k in enumerate(j):
                if k == piece:
                    board[x][y] = 0
                    locations.append([x, y])
        for location in locations:
            x, y = location
            board[x + move[direction][0]][y + move[direction][1]] = piece
        return board

    def find_moves(self):
        """Returns list of valid moves in the form: [piece, direction]."""
        invalid = []
        found = []
        for x, j in enumerate(self.board):
            for y, k in enumerate(j):
                if k > 2:
                    for d in move:
                        if self.board[x + move[d][0]][y + move[d][1]] == 0:
                            if [k, d] not in found and [k, d] not in invalid:
                                found.append([k, d])
                        else:
                            if self.board[x + move[d][0]][y + move[d][1]] == k:
                                continue
                            else:
                                invalid.append([k, d])
                                if [k, d] in found:
                                    found.remove([k, d])
                if k == 2:
                    for d in move:
                        if self.board[x + move[d][0]][y + move[d][1]] == 0 or self.board[x + move[d][0]][y + move[d][1]] == -1:
                            if [k, d] not in found and [k, d] not in invalid:
                                found.append([k, d])
                        else:
                            if self.board[x + move[d][0]][y + move[d][1]] == k:
                                continue
                            else:
                                invalid.append([k, d])
                                if [k, d] in found:
                                    found.remove([k, d])
        return found

    def is_solved(self):
        """Returns true if the current board is solved."""
        for x, j in enumerate(self.board):
            for y, k in enumerate(j):
                if k == -1:
                    return False
        return True


class Solver:
    def __init__(self, game):
        self.game = game

    def random_walk(self, n):
        self.game.print_state() # Initial board.
        for i in range(n):
            move = choice(self.game.find_moves())
            new_board = SlidingBricks(self.game.w, self.game.h, self.game.move(*move))
            new_board.normalize()
            self.game = new_board
            self.print_move(move)
            self.game.print_state()
            if self.game.is_solved():
                break
        return

    def bfs(self, i=0):
        # Track each node visited in a list of boards. Add nodes to a queue.
        # BFS: FIFO
        # DFS: LIFO
        visited, queue = [], [Node(self.game)]
        while queue:
            # Determine if the board in next node is a solution.
            node = queue.pop(i)
            visited.append(node.data.board)
            if node.data.is_solved():
                return self.print_solution(node, visited)
            # Each child is a possible move from current node.
            for child in node.children():
                if child.data.board not in visited: # Eliminate boards already visited.
                    visited.append(child.data.board)
                    queue.append(child)

    def dfs(self):
        return self.bfs(-1)

    def ids(self):
        import itertools
        # Iterate depth from 0 to inf.
        for depth in itertools.count():
            # Track each visited node in a {board: depth} hash. Add nodes to a FIFO queue.
            visited, queue = {}, [Node(self.game)]
            while queue:
                # Determine if the board in next deepest node is a solution.
                node = queue.pop()
                visited[str(node.data.board)] = node.depth
                if node.data.is_solved():
                    return self.print_solution(node, visited)
                # Each child is a possible move from current node.
                if node.depth < depth: # Limit depth.
                    for child in node.children():
                        # Remove duplicate nodes or update with a lower depth.
                        if str(child.data.board) not in visited or visited[str(child.data.board)] > child.depth:
                            visited[str(child.data.board)] = child.depth
                            queue.append(child)

    def print_solution(self, node, visited):
        """Print the moves to reach the solution and print the solved board."""
        self.game = node.data
        branch = []
        # Climb up the tree and track the moves that led to each respective state.
        while node.parent is not None:
            branch.append(node.move)
            node = node.parent
        for m in reversed(branch):
            self.print_move(m)
        self.game.print_state()
        return len(visited), len(branch)

    @staticmethod
    def print_move(move):
        print("(%d,%s)" % tuple(move))

def load_game(file):
    board = []
    with open(file) as f:
        w, h = [int(i) for i in f.readline().split(',')[:-1]]
        for line in f:
            board.append([int(i) for i in line.split(',')[:-1]])
    return w, h, board


if __name__ == "__main__":
    from timeit import default_timer as timer
    game = SlidingBricks(*load_game("SBP-level0.txt"))

    solver = Solver(game)
    start = timer()
    nodes, length = solver.bfs()
    end = timer()
    print("%d %f %d\n" % (nodes, end - start, length))

    solver = Solver(game)
    start = timer()
    nodes, length = solver.dfs()
    end = timer()
    print("%d %f %d\n" % (nodes, end - start, length))

    solver = Solver(game)
    start = timer()
    nodes, length = solver.ids()
    end = timer()
    print("%d %f %d\n" % (nodes, end - start, length))
