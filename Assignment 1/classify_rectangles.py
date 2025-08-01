import re
import numpy as np
import time
import psutil
import tracemalloc
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import List, Tuple

# Measure current memory usage in MB
def measure_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    return memory_info.rss / 1024 / 1024

# Decorator to measure execution time and memory usage of functions
def measure_performance(func):
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        start_memory = measure_memory_usage()
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        end_memory = measure_memory_usage()
        memory_used = end_memory - start_memory
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"\nPerformance metrics for {func.__name__}:")
        print(f"Execution time: {execution_time:.4f} seconds")
        print(f"Memory usage: {memory_used:.2f} MB")
        print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
        return result
    return wrapper

# Read rectangle data from a file
@measure_performance
def read_rectangle_data(filename: str) -> np.ndarray:
    try:
        with open(filename, 'r') as file:
            content = file.read().strip()
        content = re.sub(r'\s+', ' ', content)
        rect_pattern = re.compile(r'\{(\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?)\}')
        rectangles_match = rect_pattern.findall(content)
        if not rectangles_match:
            raise ValueError("No valid rectangle data found in the file")
        rectangles = np.array([list(map(float, rect)) for rect in rectangles_match])
        print(f"Successfully read {len(rectangles)} rectangles from the file.")
        return rectangles
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# Plot all rectangles on a graph
def plot_rectangles(rectangles: np.ndarray, point: Tuple[float, float] = None, title: str = "Rectangles"):
    plt.figure(figsize=(12, 10))
    plt.title(title)
    color_list = list(mcolors.TABLEAU_COLORS.values())
    colors = [color_list[i % len(color_list)] for i in range(len(rectangles))]
    for rect, color in zip(rectangles, colors):
        rect_id, x1, y1, x2, y2 = rect
        plt.gca().add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, edgecolor=color, linewidth=2))
        plt.text((x1 + x2) / 2, (y1 + y2) / 2, f'{int(rect_id)}', horizontalalignment='center', verticalalignment='center', color=color, fontweight='bold')
    if point is not None:
        plt.plot(point[0], point[1], 'ro', label='Point', markersize=10)
        plt.legend()
    all_x = rectangles[:, [1, 3]].flatten()
    all_y = rectangles[:, [2, 4]].flatten()
    padding = (max(all_x) - min(all_x)) * 0.1
    plt.xlim(min(all_x) - padding, max(all_x) + padding)
    plt.ylim(min(all_y) - padding, max(all_y) + padding)
    plt.xlabel('X coordinate')
    plt.ylabel('Y coordinate')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.axis('equal')
    plt.show()

# Plot only the rectangles with the specified IDs
def plot_specific_rectangles(rectangles: np.ndarray, specific_ids: List[int], title: str = "Specific Rectangles"):
    if not specific_ids:
        print(f"No rectangles to plot for: {title}")
        return
    plt.figure(figsize=(12, 10))
    plt.title(title)
    specific_rects = rectangles[np.isin(rectangles[:, 0], specific_ids)]
    color_list = list(mcolors.TABLEAU_COLORS.values())
    colors = [color_list[i % len(color_list)] for i in range(len(specific_rects))]
    for rect, color in zip(specific_rects, colors):
        rect_id, x1, y1, x2, y2 = rect
        plt.gca().add_patch(plt.Rectangle((x1, y1), x2-x1, y2-y1, fill=False, edgecolor=color, linewidth=2))
        plt.text((x1+x2)/2, (y1+y2)/2, f'{int(rect_id)}', horizontalalignment='center', verticalalignment='center', color=color, fontweight='bold')
    all_x = specific_rects[:, [1, 3]].flatten()
    all_y = specific_rects[:, [2, 4]].flatten()
    padding = (max(all_x) - min(all_x)) * 0.1
    plt.xlim(min(all_x) - padding, max(all_x) + padding)
    plt.ylim(min(all_y) - padding, max(all_y) + padding)
    plt.xlabel('X coordinate')
    plt.ylabel('Y coordinate')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.axis('equal')
    plt.show()

# Check if a point is inside a rectangle
def is_point_in_rectangle(point: Tuple[float, float], rectangle: np.ndarray) -> bool:
    _, x1, y1, x2, y2 = rectangle
    x, y = point
    return x1 <= x <= x2 and y1 <= y <= y2

# Find rectangles enclosing a point
@measure_performance
def find_enclosing_rectangles(rectangles: np.ndarray, point: Tuple[float, float]) -> str:
    enclosed = [int(rect[0]) for rect in rectangles if is_point_in_rectangle(point, rect)]
    return "{" + ", ".join(map(str, enclosed)) + "}" if enclosed else "{}"

# Check if two rectangles overlap or touch
def check_rectangle_overlap(rect1: np.ndarray, rect2: np.ndarray) -> bool:
    _, x1_1, y1_1, x2_1, y2_1 = rect1
    _, x1_2, y1_2, x2_2, y2_2 = rect2
    return not (x1_1 >= x2_2 or x2_1 <= x1_2 or y1_1 >= y2_2 or y2_1 <= y1_2)

# Check if one rectangle is contained within another
def is_rectangle_contained(rect1: np.ndarray, rect2: np.ndarray) -> bool:
    _, x1_1, y1_1, x2_1, y2_1 = rect1
    _, x1_2, y1_2, x2_2, y2_2 = rect2
    return x1_2 <= x1_1 and y1_2 <= y1_1 and x2_2 >= x2_1 and y2_2 >= y2_1

# Find non-overlapping rectangles
def find_non_overlapping_rectangles(rectangles: np.ndarray) -> str:
    non_overlapping = set()
    for i, rect1 in enumerate(rectangles):
        has_overlap = False
        for j, rect2 in enumerate(rectangles):
            if i != j and check_rectangle_overlap(rect1, rect2):
                has_overlap = True
                break
        if not has_overlap:
            non_overlapping.add(int(rect1[0]))
    return "{" + ", ".join(map(str, sorted(non_overlapping))) + "}"

# Find overlapping rectangles
def find_overlapping_rectangles(rectangles: np.ndarray) -> str:
    overlap_dict = {}
    for i, rect1 in enumerate(rectangles):
        rect1_id = int(rect1[0])
        for j, rect2 in enumerate(rectangles):
            if i != j:
                rect2_id = int(rect2[0])
                if check_rectangle_overlap(rect1, rect2):
                    if rect1_id not in overlap_dict:
                        overlap_dict[rect1_id] = set()
                    overlap_dict[rect1_id].add(rect2_id)
    result = []
    processed = set()
    for rect_id, overlapping in overlap_dict.items():
        if rect_id not in processed:
            overlap_str = f"{{{rect_id}, {', '.join(map(str, sorted(overlapping)))}}}"
            result.append(overlap_str)
            processed.add(rect_id)
            processed.update(overlapping)
    return "{" + ", ".join(result) + "}" if result else "{}"

# Find contained rectangles
def find_contained_rectangles(rectangles: np.ndarray) -> str:
    result = []
    for i, rect1 in enumerate(rectangles):
        contained_ids = [
            int(rect2[0]) for j, rect2 in enumerate(rectangles)
            if i != j and is_rectangle_contained(rect2, rect1)
        ]
        if contained_ids:
            result.append(f"{{{int(rect1[0])}, {', '.join(map(str, contained_ids))}}}")
    return "{" + ", ".join(result) + "}" if result else "{}"

# Find abutting rectangles
def find_abutting_rectangles(rectangles: np.ndarray) -> str:
    abutting_rectangles = []
    for i, rect1 in enumerate(rectangles):
        for j, rect2 in enumerate(rectangles):
            if i != j:
                _, x1_1, y1_1, x2_1, y2_1 = rect1
                _, x1_2, y1_2, x2_2, y2_2 = rect2
                x_overlap = x1_1 < x2_2 and x2_1 > x1_2
                y_overlap = y1_1 < y2_2 and y2_1 > y1_2
                if x_overlap:
                    if abs(y2_1 - y1_2) < 1e-10:
                        abutting_rectangles.append(f"{{{int(rect1[0])}, 'n', {int(rect2[0])}}}")
                    elif abs(y1_1 - y2_2) < 1e-10:
                        abutting_rectangles.append(f"{{{int(rect1[0])}, 's', {int(rect2[0])}}}")
                if y_overlap:
                    if abs(x2_1 - x1_2) < 1e-10:
                        abutting_rectangles.append(f"{{{int(rect1[0])}, 'e', {int(rect2[0])}}}")
                    elif abs(x1_1 - x2_2) < 1e-10:
                        abutting_rectangles.append(f"{{{int(rect1[0])}, 'w', {int(rect2[0])}}}")
    return "{" + ", ".join(abutting_rectangles) + "}" if abutting_rectangles else "{}"

# Main program with performance monitoring
@measure_performance
def main():
    start_time = time.time()
    start_memory = measure_memory_usage()
    try:
        filename = input("Enter the filename: ")
        rectangles = read_rectangle_data(filename)
        if rectangles is not None:
            plot_rectangles(rectangles, title="All Rectangles")
            point = tuple(map(float, input("Enter point coordinates (x y): ").split()))
            enclosing_rectangles = find_enclosing_rectangles(rectangles, point)
            print(f"Enclosing rectangles: {enclosing_rectangles}")
            plot_rectangles(rectangles, point, title="Rectangles with Point")
            non_overlapping = find_non_overlapping_rectangles(rectangles)
            print(f"Non-overlapping rectangles: {non_overlapping}")
            non_overlapping_ids = [int(x) for x in non_overlapping[1:-1].split(',') if x.strip()]
            if non_overlapping_ids:
                plot_specific_rectangles(rectangles, non_overlapping_ids, "Non-overlapping Rectangles")
            overlapping_rectangles = find_overlapping_rectangles(rectangles)
            print("Overlapping rectangles:", overlapping_rectangles)
            overlapping_ids = []
            for group in overlapping_rectangles.strip('{}').split('}, {'):
                if group:
                    ids = [int(x.strip()) for x in group.strip('{}').split(',')]
                    overlapping_ids.extend(ids)
            if overlapping_ids:
                plot_specific_rectangles(rectangles, list(set(overlapping_ids)), "Overlapping Rectangles")
            contained_rectangles = find_contained_rectangles(rectangles)
            print("Contained rectangles:", contained_rectangles)
            contained_ids = []
            for group in contained_rectangles.strip('{}').split('}, {'):
                if group:
                    ids = [int(x.strip()) for x in group.strip('{}').split(',')]
                    contained_ids.extend(ids)
            if contained_ids:
                plot_specific_rectangles(rectangles, list(set(contained_ids)), "Contained Rectangles")
            abutting_rectangles = find_abutting_rectangles(rectangles)
            print("Abutting rectangles:", abutting_rectangles)
    except Exception as e:
        print(f"An error occurred: {e}")
    end_time = time.time()
    end_memory = measure_memory_usage()
    print("\nOverall Performance Metrics:")
    print(f"Total execution time: {end_time - start_time:.4f} seconds")
    print(f"Total memory usage: {end_memory - start_memory:.2f} MB")
    print(f"Current memory usage: {end_memory:.2f} MB")

if __name__ == "__main__":
    main()
