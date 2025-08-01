import numpy as np
import time
import psutil
import matplotlib.pyplot as plt
import sys

def measure_memory_usage():
    # Returns memory usage in MB
    process = psutil.Process()
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)

def read_input_data(filename):
    # Reads node coordinates from file
    try:
        with open(filename, 'r') as file:
            content = file.read().strip()
            content = content.replace('{', '').replace('}', '').replace(',', ' ')
            data = list(map(float, content.split()))
            return data
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)

def find_optimal_trunk(nodes):
    # Finds the optimal trunk line and Steiner points
    start_time = time.time()
    initial_memory = measure_memory_usage()
    
    n = int(nodes[0])
    node_coords = [(nodes[i], nodes[i+1]) for i in range(1, len(nodes), 2)]
    
    if len(node_coords) != n:
        print(f"Warning: Expected {n} nodes but found {len(node_coords)}")
    
    sorted_nodes = sorted(node_coords, key=lambda p: p[0])
    x_min, x_max = sorted_nodes[0][0], sorted_nodes[-1][0]
    y_coords = [node[1] for node in node_coords]
    y_median = np.median(y_coords)
    trunk = (x_min, y_median, x_max, y_median)

    steiner_points = [(x_min, y_median), (x_max, y_median)]
    for node_x, node_y in node_coords:
        steiner_points.append((node_x, y_median))
    steiner_points = list(set(steiner_points))

    end_time = time.time()
    final_memory = measure_memory_usage()

    print(f"Memory Usage: {final_memory - initial_memory:.2f} MB")
    print(f"Time Taken: {end_time - start_time:.6f} seconds")

    return trunk, node_coords, steiner_points

def calculate_elmore_delay(path_lengths, r_per_unit=1, c_per_unit=1e-15):
    # Computes total Elmore delay along a path
    total_delay = 0
    cumulative_capacitance = 0
    for length in reversed(path_lengths):
        r = r_per_unit * length
        c = c_per_unit * length
        cumulative_capacitance += c
        total_delay += r * cumulative_capacitance 
    return total_delay

def build_steiner_tree(node_coords, trunk, steiner_points):
    # Builds a dictionary of Steiner tree segments and delays
    x1, y1, x2, y2 = trunk
    segments = {}
    trunk_length = abs(x2 - x1)
    segments[((x1, y1), (x2, y2))] = {
        "length": trunk_length,
        "delay": calculate_elmore_delay([trunk_length])
    }
    for i, (x, y) in enumerate(node_coords):
        vertical_segment = ((x, y), (x, y1))
        vertical_length = abs(y - y1)
        segments[vertical_segment] = {
            "length": vertical_length,
            "delay": calculate_elmore_delay([vertical_length])
        }
    return segments

def find_critical_net(node_coords, trunk, segments, clock_pos):
    # Finds the critical net with maximum delay
    x1, y1, x2, y2 = trunk
    clock_x, clock_y = clock_pos
    max_delay = 0
    critical_path = []
    critical_node_idx = None

    for i, (x, y) in enumerate(node_coords):
        path_segments = []
        path_lengths = []
        total_delay = 0

        if clock_y != y1:
            connect_length = abs(clock_y - y1)
            path_lengths.append(connect_length)

        trunk_length = abs(x - clock_x)
        if trunk_length > 0:
            horizontal_segment = ((clock_x, y1), (x, y1))
            path_segments.append(horizontal_segment)
            path_lengths.append(trunk_length)
            trunk_delay = calculate_elmore_delay(path_lengths)
            total_delay += trunk_delay

        vertical_length = abs(y - y1)
        if vertical_length > 0:
            vertical_segment = ((x, y1), (x, y))
            path_segments.append(vertical_segment)
            path_lengths.append(vertical_length)
            vertical_delay = calculate_elmore_delay(path_lengths)
            total_delay += vertical_delay

        if total_delay > max_delay:
            max_delay = total_delay
            critical_path = path_segments
            critical_node_idx = i

    return critical_path, max_delay, critical_node_idx

def calculate_delays_to_all_nodes(node_coords, trunk, clock_pos):
    # Calculates delay to all nodes from clock
    x1, y1, x2, y2 = trunk
    clock_x, clock_y = clock_pos
    node_delays = []

    for node_pos in node_coords:
        node_x, node_y = node_pos
        path_lengths = []
        total_delay = 0

        if clock_y != y1 or clock_x not in [x1, x2]:
            pass

        trunk_length = abs(node_x - clock_x)
        if trunk_length > 0:
            path_lengths.append(trunk_length)
            total_delay += calculate_elmore_delay(path_lengths)

        vertical_length = abs(node_y - y1)
        if vertical_length > 0:
            path_lengths.append(vertical_length)
            total_delay += calculate_elmore_delay(path_lengths)

        node_delays.append(total_delay)

    return node_delays

def calculate_initial_clock_skew(node_coords, trunk):
    # Calculates skew for initial clock position
    x1, y1, _, _ = trunk
    initial_clock_pos = (x1, y1)
    delays = calculate_delays_to_all_nodes(node_coords, trunk, initial_clock_pos)
    initial_skew = max(delays) - min(delays) if delays else 0

    print("\nInitial Clock Position (leftmost end of trunk) Analysis:")
    print(f"Clock Position: {{{x1}, {y1}}}")
    print("Delays to each node:")
    for i, delay in enumerate(delays):
        print(f"  Node {i+1}: {delay:.2e} seconds")
    print(f"Initial Clock Skew: {initial_skew:.2e} seconds")

    return initial_skew, delays

def minimize_clock_skew(node_coords, trunk, segments):
    # Finds clock location minimizing skew
    start_time = time.time()
    initial_memory = measure_memory_usage()
    x1, y1, x2, y2 = trunk

    best_skew = float('inf')
    best_position = None
    best_delays = None
    best_critical_path = None
    best_critical_node_idx = None

    x_min = min(node[0] for node in node_coords) - 5
    x_max = max(node[0] for node in node_coords) + 5
    y_min = min(node[1] for node in node_coords) - 5
    y_max = max(node[1] for node in node_coords) + 5

    x_step = (x_max - x_min) / 20
    y_step = (y_max - y_min) / 20

    for x in np.arange(x_min, x_max + x_step, x_step):
        for y in np.arange(y_min, y_max + y_step, y_step):
            clock_pos = (x, y)
            node_delays = calculate_delays_to_all_nodes(node_coords, trunk, clock_pos)

            if node_delays:
                current_skew = max(node_delays) - min(node_delays)

                if current_skew < best_skew:
                    best_skew = current_skew
                    best_position = clock_pos
                    best_delays = node_delays
                    critical_path, _, critical_node_idx = find_critical_net(node_coords, trunk, segments, clock_pos)
                    best_critical_path = critical_path
                    best_critical_node_idx = critical_node_idx

    end_time = time.time()
    final_memory = measure_memory_usage()

    print(f"Memory Usage: {final_memory - initial_memory:.2f} MB")
    print(f"Time Taken: {end_time - start_time:.6f} seconds")

    if best_delays:
        print("\nOptimal Clock Position Analysis:")
        print(f"Clock Position: {{{best_position[0]}, {best_position[1]}}}")
        print("Delays to each node:")
        for i, delay in enumerate(best_delays):
            print(f"  Node {i+1}: {delay:.2e} seconds")
        print(f"  Min Delay: {min(best_delays):.2e} seconds")
        print(f"  Max Delay: {max(best_delays):.2e} seconds")
        print(f"Minimum Clock Skew: {best_skew:.2e} seconds")

    return best_position, best_skew, best_critical_path, best_critical_node_idx, best_delays

def nearest_point_on_trunk(x, y, x1, x2, y_trunk):
    # Finds closest point on trunk to a given position
    trunk_x = max(x1, min(x2, x))
    return (trunk_x, y_trunk)

def main_problem1(nodes):
    print("Problem 1: Optimal Steiner Tree Trunk")
    trunk, node_coords, steiner_points = find_optimal_trunk(nodes)
    segments = build_steiner_tree(node_coords, trunk, steiner_points)
    initial_skew, initial_delays = calculate_initial_clock_skew(node_coords, trunk)
    critical_path, max_delay, critical_node_idx = find_critical_net(node_coords, trunk, segments, (trunk[0], trunk[1]))
    print(f"Optimal Trunk Coordinates: {{{trunk[0]}, {trunk[1]}, {trunk[2]}, {trunk[3]}}}")
    print(f"Critical Path Delay: {max_delay:.2e} seconds")
    print(f"Number of Steiner Points: {len(steiner_points)}")
    print(f"Steiner Points: {steiner_points}")
    plot_steiner_tree(node_coords, trunk, segments, steiner_points, 
                      critical_path=critical_path, critical_node_idx=critical_node_idx,
                      node_delays=initial_delays)
    return trunk, node_coords, steiner_points, segments, initial_delays

def main_problem2(nodes, trunk, node_coords, steiner_points, segments):
    print("\nProblem 2: Minimize Clock Skew with New Clock Location")
    clock_generator, min_skew, critical_path, critical_node_idx, optimal_delays = minimize_clock_skew(node_coords, trunk, segments)
    print(f"Optimal Clock Generator Location: {{{clock_generator[0]}, {clock_generator[1]}}}")
    print(f"Minimum Clock Skew: {min_skew:.2e} seconds")
    plot_steiner_tree(node_coords, trunk, segments, steiner_points, 
                      critical_path=critical_path, critical_node_idx=critical_node_idx, 
                      clock_generator=clock_generator, node_delays=optimal_delays)
    return clock_generator

def main():
    filename = input("Enter the input file name: ")
    input_data = read_input_data(filename)
    trunk, node_coords, steiner_points, segments, initial_delays = main_problem1(input_data)
    clock_generator = main_problem2(input_data, trunk, node_coords, steiner_points, segments)

if __name__ == "__main__":
    main()
