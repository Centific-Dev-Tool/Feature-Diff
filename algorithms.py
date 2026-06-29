"""
常用算法合集 (Algorithms Collection)
=====================================
涵盖排序、搜索、图论、动态规划、字符串、数学、树结构等经典算法。
每个算法都配有详细注释和示例。
"""

from typing import List, Optional, Tuple, TypeVar
from collections import deque
import heapq
import math

# ============================================================
#  一、排序算法 (Sorting)
# ============================================================

def bubble_sort(arr: List[int]) -> List[int]:
    """冒泡排序 O(n²)"""
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr



def selection_sort(arr: List[int]) -> List[int]:
    """选择排序 O(n²)"""
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


def insertion_sort(arr: List[int]) -> List[int]:
    """插入排序 O(n²)，适合小规模 / 近乎有序数据"""
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def merge_sort(arr: List[int]) -> List[int]:
    """归并排序 O(n log n)"""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left: List[int], right: List[int]) -> List[int]:
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def quick_sort(arr: List[int]) -> List[int]:
    """快速排序 O(n log n) 平均, O(n²) 最坏"""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)


def quick_sort_inplace(arr: List[int], low: int = 0, high: int = None) -> List[int]:
    """快速排序 - 原地分区版"""
    if high is None:
        high = len(arr) - 1
    if low < high:
        pi = _partition(arr, low, high)
        quick_sort_inplace(arr, low, pi - 1)
        quick_sort_inplace(arr, pi + 1, high)
    return arr


def _partition(arr: List[int], low: int, high: int) -> int:
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def heap_sort(arr: List[int]) -> List[int]:
    """堆排序 O(n log n)"""
    heapq.heapify(arr)
    return [heapq.heappop(arr) for _ in range(len(arr))]


def counting_sort(arr: List[int]) -> List[int]:
    """计数排序 O(n + k)，适用于整数且范围较小"""
    if not arr:
        return arr
    min_val, max_val = min(arr), max(arr)
    count = [0] * (max_val - min_val + 1)
    for x in arr:
        count[x - min_val] += 1
    result = []
    for i, c in enumerate(count):
        result.extend([i + min_val] * c)
    return result


def shell_sort(arr: List[int]) -> List[int]:
    """希尔排序，插入排序的改进版"""
    n = len(arr)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = temp
        gap //= 2
    return arr


# ============================================================
#  二、搜索算法 (Searching)
# ============================================================

def binary_search(arr: List[int], target: int) -> int:
    """二分查找 O(log n)，返回索引，未找到返回 -1"""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def binary_search_leftmost(arr: List[int], target: int) -> int:
    """二分查找 - 最左边界（第一个 >= target 的位置）"""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def binary_search_rightmost(arr: List[int], target: int) -> int:
    """二分查找 - 最右边界（最后一个 <= target 的位置）"""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo - 1


def ternary_search(arr: List[int], lo: int, hi: int, target: int) -> int:
    """三分查找"""
    if hi >= lo:
        mid1 = lo + (hi - lo) // 3
        mid2 = hi - (hi - lo) // 3
        if arr[mid1] == target:
            return mid1
        if arr[mid2] == target:
            return mid2
        if target < arr[mid1]:
            return ternary_search(arr, lo, mid1 - 1, target)
        elif target > arr[mid2]:
            return ternary_search(arr, mid2 + 1, hi, target)
        else:
            return ternary_search(arr, mid1 + 1, mid2 - 1, target)
    return -1


def jump_search(arr: List[int], target: int) -> int:
    """跳跃搜索 O(√n)"""
    import math
    n = len(arr)
    step = int(math.sqrt(n))
    prev = 0
    while prev < n and arr[min(step, n) - 1] < target:
        prev = step
        step += int(math.sqrt(n))
        if prev >= n:
            return -1
    for i in range(prev, min(step, n)):
        if arr[i] == target:
            return i
    return -1


def exponential_search(arr: List[int], target: int) -> int:
    """指数搜索 O(log n)，适用于无界 / 大数组"""
    if arr[0] == target:
        return 0
    i = 1
    n = len(arr)
    while i < n and arr[i] <= target:
        i *= 2
    return binary_search(arr[:min(i, n)], target)


# ============================================================
#  三、图论算法 (Graph)
# ============================================================

def bfs(graph: dict, start):
    """广度优先搜索 (BFS)"""
    visited = set()
    queue = deque([start])
    visited.add(start)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order


def dfs_iterative(graph: dict, start):
    """深度优先搜索 - 迭代版 (DFS)"""
    visited = set()
    stack = [start]
    order = []
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            order.append(node)
            for neighbor in reversed(graph.get(node, [])):
                if neighbor not in visited:
                    stack.append(neighbor)
    return order


def dfs_recursive(graph: dict, node, visited: set = None, order: list = None):
    """深度优先搜索 - 递归版"""
    if visited is None:
        visited = set()
    if order is None:
        order = []
    visited.add(node)
    order.append(node)
    for neighbor in graph.get(node, []):
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited, order)
    return order


def dijkstra(graph: dict, start) -> dict:
    """Dijkstra 最短路径 O((V+E) log V)"""
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    while pq:
        dist, node = heapq.heappop(pq)
        if dist > distances[node]:
            continue
        for neighbor, weight in graph[node].items():
            new_dist = dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))
    return distances


def bellman_ford(edges: List[Tuple[int, int, int]], n: int, start: int) -> List[float]:
    """Bellman-Ford 最短路径，可处理负权边，检测负环 O(VE)"""
    dist = [float('inf')] * n
    dist[start] = 0
    for _ in range(n - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:
            break
    # 检测负环
    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            raise ValueError("图中存在负权环!")
    return dist


def floyd_warshall(graph: List[List[float]]) -> List[List[float]]:
    """Floyd-Warshall 全源最短路径 O(V³)"""
    n = len(graph)
    dist = [row[:] for row in graph]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist


def topological_sort(graph: dict) -> List:
    """拓扑排序 (Kahn 算法) O(V+E)"""
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] = in_degree.get(neighbor, 0) + 1
    queue = deque([node for node, deg in in_degree.items() if deg == 0])
    result = []
    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    if len(result) != len(in_degree):
        raise ValueError("图中存在环，无法拓扑排序!")
    return result


def has_cycle_undirected(graph: dict) -> bool:
    """无向图环检测 (并查集)"""
    parent = {}

    def find(x):
        if parent.setdefault(x, x) != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        parent[find(x)] = find(y)

    visited_edges = set()
    for u in graph:
        for v in graph[u]:
            edge = tuple(sorted((u, v)))
            if edge in visited_edges:
                continue
            visited_edges.add(edge)
            if find(u) == find(v):
                return True
            union(u, v)
    return False


def kruskal_mst(edges: List[Tuple[int, int, int]], n: int) -> List[Tuple[int, int, int]]:
    """Kruskal 最小生成树 O(E log E)"""
    edges = sorted(edges, key=lambda x: x[2])
    parent = list(range(n))

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        parent[find(x)] = find(y)

    mst = []
    for u, v, w in edges:
        if find(u) != find(v):
            union(u, v)
            mst.append((u, v, w))
            if len(mst) == n - 1:
                break
    return mst


def prim_mst(graph: dict, start) -> List[Tuple]:
    """Prim 最小生成树 O(E log V)"""
    visited = set()
    mst = []
    pq = [(0, start, None)]  # (weight, node, parent)
    while pq and len(visited) < len(graph):
        w, node, parent = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)
        if parent is not None:
            mst.append((parent, node, w))
        for neighbor, weight in graph[node].items():
            if neighbor not in visited:
                heapq.heappush(pq, (weight, neighbor, node))
    return mst


# ============================================================
#  四、动态规划 (Dynamic Programming)
# ============================================================

def knapsack_01(weights: List[int], values: List[int], capacity: int) -> int:
    """0-1 背包问题"""
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for c in range(capacity, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[capacity]


def knapsack_unbounded(weights: List[int], values: List[int], capacity: int) -> int:
    """完全背包（无限物品）"""
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for c in range(w, capacity + 1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[capacity]


def longest_common_subsequence(s1: str, s2: str) -> int:
    """最长公共子序列 (LCS) O(mn)"""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


def longest_common_subsequence_str(s1: str, s2: str) -> str:
    """最长公共子序列 - 返回子序列字符串"""
    m, n = len(s1), len(s2)
    dp = [[""] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + s1[i - 1]
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1], key=len)
    return dp[m][n]


def longest_increasing_subsequence(arr: List[int]) -> int:
    """最长递增子序列 (LIS) O(n log n)"""
    tails = []
    for x in arr:
        i = binary_search_leftmost(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


def longest_increasing_subsequence_arr(arr: List[int]) -> List[int]:
    """最长递增子序列 - 返回序列"""
    n = len(arr)
    dp = [1] * n
    prev = [-1] * n
    for i in range(n):
        for j in range(i):
            if arr[j] < arr[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
                prev[i] = j
    # 回溯
    idx = dp.index(max(dp))
    result = []
    while idx != -1:
        result.append(arr[idx])
        idx = prev[idx]
    return result[::-1]


def edit_distance(s1: str, s2: str) -> int:
    """编辑距离 (Levenshtein) O(mn)"""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[m][n]


def coin_change(coins: List[int], amount: int) -> int:
    """零钱兑换 - 最少硬币数"""
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for x in range(coin, amount + 1):
            dp[x] = min(dp[x], dp[x - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1


def coin_change_ways(coins: List[int], amount: int) -> int:
    """零钱兑换 - 组合数"""
    dp = [0] * (amount + 1)
    dp[0] = 1
    for coin in coins:
        for x in range(coin, amount + 1):
            dp[x] += dp[x - coin]
    return dp[amount]


def max_subarray_sum(arr: List[int]) -> int:
    """最大子数组和 (Kadane 算法) O(n)"""
    max_ending = max_so_far = arr[0]
    for x in arr[1:]:
        max_ending = max(x, max_ending + x)
        max_so_far = max(max_so_far, max_ending)
    return max_so_far


def max_subarray_range(arr: List[int]) -> Tuple[int, int, int]:
    """最大子数组和 - 返回 (和, 起始索引, 结束索引)"""
    max_ending = max_so_far = arr[0]
    start = end = temp_start = 0
    for i in range(1, len(arr)):
        if arr[i] > max_ending + arr[i]:
            max_ending = arr[i]
            temp_start = i
        else:
            max_ending += arr[i]
        if max_ending > max_so_far:
            max_so_far = max_ending
            start = temp_start
            end = i
    return max_so_far, start, end


def matrix_chain_order(dims: List[int]) -> int:
    """矩阵链乘法 - 最少乘法次数 O(n³)"""
    n = len(dims) - 1
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float('inf')
            for k in range(i, j):
                cost = dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                dp[i][j] = min(dp[i][j], cost)
    return dp[0][n - 1]


def rod_cutting(prices: List[int], n: int) -> int:
    """钢条切割 - 最大收益"""
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        max_val = float('-inf')
        for j in range(i):
            max_val = max(max_val, prices[j] + dp[i - j - 1])
        dp[i] = max_val
    return dp[n]


# ============================================================
#  五、字符串算法 (String)
# ============================================================

def kmp_search(text: str, pattern: str) -> List[int]:
    """KMP 字符串匹配 O(n+m)，返回所有匹配起始位置"""
    if not pattern:
        return list(range(len(text) + 1))
    lps = _kmp_lps(pattern)
    matches = []
    j = 0
    for i in range(len(text)):
        while j > 0 and text[i] != pattern[j]:
            j = lps[j - 1]
        if text[i] == pattern[j]:
            j += 1
        if j == len(pattern):
            matches.append(i - j + 1)
            j = lps[j - 1]
    return matches


def _kmp_lps(pattern: str) -> List[int]:
    """构建 LPS (Longest Prefix Suffix) 数组"""
    lps = [0] * len(pattern)
    j = 0
    for i in range(1, len(pattern)):
        while j > 0 and pattern[i] != pattern[j]:
            j = lps[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
            lps[i] = j
    return lps


def rabin_karp(text: str, pattern: str, prime: int = 101) -> List[int]:
    """Rabin-Karp 字符串匹配 (滚动哈希)"""
    n, m = len(text), len(pattern)
    if m > n:
        return []
    base = 256
    # 计算 hash
    pattern_hash = 0
    text_hash = 0
    h = 1
    for _ in range(m - 1):
        h = (h * base) % prime
    for i in range(m):
        pattern_hash = (base * pattern_hash + ord(pattern[i])) % prime
        text_hash = (base * text_hash + ord(text[i])) % prime
    matches = []
    for i in range(n - m + 1):
        if pattern_hash == text_hash:
            if text[i:i + m] == pattern:
                matches.append(i)
        if i < n - m:
            text_hash = (base * (text_hash - ord(text[i]) * h) + ord(text[i + m])) % prime
            if text_hash < 0:
                text_hash += prime
    return matches


def z_algorithm(s: str) -> List[int]:
    """Z 算法 - 计算 Z 数组"""
    n = len(s)
    z = [0] * n
    l = r = 0
    for i in range(1, n):
        if i <= r:
            z[i] = min(r - i + 1, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] - 1 > r:
            l, r = i, i + z[i] - 1
    return z


def manacher(s: str) -> str:
    """Manacher 算法 - 最长回文子串 O(n)"""
    if not s:
        return ""
    t = "#" + "#".join(s) + "#"
    n = len(t)
    p = [0] * n
    center = right = 0
    max_len = max_center = 0
    for i in range(n):
        mirror = 2 * center - i
        if i < right:
            p[i] = min(right - i, p[mirror])
        while i - p[i] - 1 >= 0 and i + p[i] + 1 < n and t[i - p[i] - 1] == t[i + p[i] + 1]:
            p[i] += 1
        if i + p[i] > right:
            center, right = i, i + p[i]
        if p[i] > max_len:
            max_len = p[i]
            max_center = i
    start = (max_center - max_len) // 2
    return s[start:start + max_len]


def longest_common_prefix(strs: List[str]) -> str:
    """最长公共前缀"""
    if not strs:
        return ""
    prefix = strs[0]
    for s in strs[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix


def is_palindrome(s: str) -> bool:
    """判断回文串"""
    lo, hi = 0, len(s) - 1
    while lo < hi:
        if s[lo] != s[hi]:
            return False
        lo += 1
        hi -= 1
    return True


def count_palindromic_substrings(s: str) -> int:
    """统计回文子串数量 O(n²)"""
    n = len(s)
    count = 0
    for center in range(2 * n - 1):
        left = center // 2
        right = left + center % 2
        while left >= 0 and right < n and s[left] == s[right]:
            count += 1
            left -= 1
            right += 1
    return count


# ============================================================
#  六、树结构算法 (Tree)
# ============================================================

class TreeNode:
    """二叉树节点"""
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def preorder_traversal(root: TreeNode) -> List[int]:
    """前序遍历 - 递归"""
    if not root:
        return []
    return [root.val] + preorder_traversal(root.left) + preorder_traversal(root.right)


def inorder_traversal(root: TreeNode) -> List[int]:
    """中序遍历 - 迭代"""
    result, stack = [], []
    cur = root
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        result.append(cur.val)
        cur = cur.right
    return result


def postorder_traversal(root: TreeNode) -> List[int]:
    """后序遍历 - 迭代"""
    if not root:
        return []
    result, stack = [], [root]
    while stack:
        node = stack.pop()
        result.append(node.val)
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
    return result[::-1]


def level_order_traversal(root: TreeNode) -> List[List[int]]:
    """层序遍历 BFS"""
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result


def tree_height(root: TreeNode) -> int:
    """二叉树高度"""
    if not root:
        return 0
    return 1 + max(tree_height(root.left), tree_height(root.right))


def is_balanced(root: TreeNode) -> bool:
    """判断平衡二叉树"""
    def check(node):
        if not node:
            return 0, True
        lh, lb = check(node.left)
        rh, rb = check(node.right)
        return 1 + max(lh, rh), lb and rb and abs(lh - rh) <= 1
    return check(root)[1]


def is_symmetric(root: TreeNode) -> bool:
    """判断对称二叉树"""
    def mirror(a, b):
        if not a and not b:
            return True
        if not a or not b:
            return False
        return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)
    return mirror(root, root)


def lowest_common_ancestor(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    """二叉树的最近公共祖先 (LCA)"""
    if not root or root == p or root == q:
        return root
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    if left and right:
        return root
    return left or right


def lowest_common_ancestor_bst(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    """二叉搜索树的最近公共祖先"""
    while root:
        if p.val < root.val and q.val < root.val:
            root = root.left
        elif p.val > root.val and q.val > root.val:
            root = root.right
        else:
            return root


def is_valid_bst(root: TreeNode, lo=float('-inf'), hi=float('inf')) -> bool:
    """验证二叉搜索树"""
    if not root:
        return True
    if root.val <= lo or root.val >= hi:
        return False
    return is_valid_bst(root.left, lo, root.val) and is_valid_bst(root.right, root.val, hi)


def diameter_of_tree(root: TreeNode) -> int:
    """二叉树的直径"""
    diameter = 0

    def depth(node):
        nonlocal diameter
        if not node:
            return 0
        left = depth(node.left)
        right = depth(node.right)
        diameter = max(diameter, left + right)
        return 1 + max(left, right)

    depth(root)
    return diameter


def max_path_sum(root: TreeNode) -> int:
    """二叉树的最大路径和"""
    max_sum = float('-inf')

    def dfs(node):
        nonlocal max_sum
        if not node:
            return 0
        left = max(0, dfs(node.left))
        right = max(0, dfs(node.right))
        max_sum = max(max_sum, node.val + left + right)
        return node.val + max(left, right)

    dfs(root)
    return max_sum


def serialize_tree(root: TreeNode) -> str:
    """序列化二叉树"""
    if not root:
        return "#"
    return f"{root.val},{serialize_tree(root.left)},{serialize_tree(root.right)}"


def deserialize_tree(data: str) -> TreeNode:
    """反序列化二叉树"""
    it = iter(data.split(","))

    def build():
        val = next(it)
        if val == "#":
            return None
        node = TreeNode(int(val))
        node.left = build()
        node.right = build()
        return node

    return build()


# ============================================================
#  七、数学算法 (Math)
# ============================================================

def gcd(a: int, b: int) -> int:
    """最大公约数 (欧几里得算法)"""
    while b:
        a, b = b, a % b
    return a


def lcm(a: int, b: int) -> int:
    """最小公倍数"""
    return a * b // gcd(a, b)


def gcd_extended(a: int, b: int) -> Tuple[int, int, int]:
    """扩展欧几里得算法，返回 (gcd, x, y) 满足 ax + by = gcd"""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = gcd_extended(b, a % b)
    return g, y1, x1 - (a // b) * y1


def mod_inverse(a: int, m: int) -> int:
    """模逆元 (a * x ≡ 1 mod m)"""
    g, x, _ = gcd_extended(a, m)
    if g != 1:
        raise ValueError("模逆元不存在")
    return x % m


def is_prime(n: int) -> bool:
    """素数判断 O(√n)"""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def sieve_of_eratosthenes(n: int) -> List[int]:
    """埃拉托色尼筛法 - 找出 [2, n] 所有素数 O(n log log n)"""
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]


def prime_factors(n: int) -> List[int]:
    """质因数分解"""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def fast_pow(base: int, exp: int, mod: int = None) -> int:
    """快速幂 (二分幂) O(log n)"""
    result = 1
    if mod:
        base %= mod
    while exp > 0:
        if exp & 1:
            result = result * base % mod if mod else result * base
        base = base * base % mod if mod else base * base
        exp >>= 1
    return result


def fibonacci(n: int) -> int:
    """斐波那契数列 - 矩阵快速幂 O(log n)"""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def fibonacci_matrix(n: int) -> int:
    """斐波那契数列 - 矩阵快速幂 O(log n)"""
    def mat_mul(a, b):
        return [
            [a[0][0] * b[0][0] + a[0][1] * b[1][0],
             a[0][0] * b[0][1] + a[0][1] * b[1][1]],
            [a[1][0] * b[0][0] + a[1][1] * b[1][0],
             a[1][0] * b[0][1] + a[1][1] * b[1][1]]
        ]

    def mat_pow(mat, exp):
        res = [[1, 0], [0, 1]]
        while exp:
            if exp & 1:
                res = mat_mul(res, mat)
            mat = mat_mul(mat, mat)
            exp >>= 1
        return res

    if n <= 1:
        return n
    base = [[1, 1], [1, 0]]
    result = mat_pow(base, n - 1)
    return result[0][0]


def is_happy_number(n: int) -> bool:
    """快乐数"""
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(d) ** 2 for d in str(n))
    return n == 1


def nth_ugly_number(n: int) -> int:
    """第 n 个丑数 (只含质因数 2,3,5)"""
    ugly = [1]
    i2 = i3 = i5 = 0
    while len(ugly) < n:
        next2, next3, next5 = ugly[i2] * 2, ugly[i3] * 3, ugly[i5] * 5
        next_ugly = min(next2, next3, next5)
        ugly.append(next_ugly)
        if next_ugly == next2:
            i2 += 1
        if next_ugly == next3:
            i3 += 1
        if next_ugly == next5:
            i5 += 1
    return ugly[-1]


def n_queens_count(n: int) -> int:
    """N 皇后 - 解的数量 (位运算版)"""
    def dfs(row, cols, diag1, diag2):
        if row == n:
            return 1
        count = 0
        available = ((1 << n) - 1) & ~(cols | diag1 | diag2)
        while available:
            pos = available & -available
            available ^= pos
            count += dfs(row + 1, cols | pos, (diag1 | pos) << 1, (diag2 | pos) >> 1)
        return count
    return dfs(0, 0, 0, 0)


def n_queens_solutions(n: int) -> List[List[str]]:
    """N 皇后 - 所有解"""
    board = [["."] * n for _ in range(n)]
    result = []
    cols = set()
    diag1 = set()  # 主对角线 row+col
    diag2 = set()  # 副对角线 row-col

    def backtrack(row):
        if row == n:
            result.append(["".join(r) for r in board])
            return
        for col in range(n):
            if col in cols or (row + col) in diag1 or (row - col) in diag2:
                continue
            board[row][col] = "Q"
            cols.add(col); diag1.add(row + col); diag2.add(row - col)
            backtrack(row + 1)
            cols.remove(col); diag1.remove(row + col); diag2.remove(row - col)
            board[row][col] = "."

    backtrack(0)
    return result


# ============================================================
#  八、回溯算法 (Backtracking)
# ============================================================

def permutations(arr: List[int]) -> List[List[int]]:
    """全排列"""
    result = []
    n = len(arr)

    def backtrack(start):
        if start == n:
            result.append(arr[:])
            return
        for i in range(start, n):
            arr[start], arr[i] = arr[i], arr[start]
            backtrack(start + 1)
            arr[start], arr[i] = arr[i], arr[start]

    backtrack(0)
    return result


def combinations(arr: List[int], k: int) -> List[List[int]]:
    """组合 C(n, k)"""
    result = []

    def backtrack(start, path):
        if len(path) == k:
            result.append(path[:])
            return
        for i in range(start, len(arr)):
            path.append(arr[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return result


def subsets(arr: List[int]) -> List[List[int]]:
    """子集 (幂集)"""
    result = []

    def backtrack(start, path):
        result.append(path[:])
        for i in range(start, len(arr)):
            path.append(arr[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return result


def generate_parentheses(n: int) -> List[str]:
    """生成有效括号组合"""
    result = []

    def backtrack(open_cnt, close_cnt, path):
        if len(path) == 2 * n:
            result.append(path)
            return
        if open_cnt < n:
            backtrack(open_cnt + 1, close_cnt, path + "(")
        if close_cnt < open_cnt:
            backtrack(open_cnt, close_cnt + 1, path + ")")

    backtrack(0, 0, "")
    return result


def letter_combinations(digits: str) -> List[str]:
    """电话号码的字母组合"""
    if not digits:
        return []
    mapping = {
        "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"
    }
    result = []

    def backtrack(idx, path):
        if idx == len(digits):
            result.append("".join(path))
            return
        for ch in mapping[digits[idx]]:
            path.append(ch)
            backtrack(idx + 1, path)
            path.pop()

    backtrack(0, [])
    return result


def word_search(board: List[List[str]], word: str) -> bool:
    """单词搜索 (DFS + 回溯)"""
    m, n = len(board), len(board[0])

    def dfs(i, j, idx):
        if idx == len(word):
            return True
        if i < 0 or i >= m or j < 0 or j >= n or board[i][j] != word[idx]:
            return False
        temp, board[i][j] = board[i][j], "#"
        found = (dfs(i + 1, j, idx + 1) or dfs(i - 1, j, idx + 1) or
                 dfs(i, j + 1, idx + 1) or dfs(i, j - 1, idx + 1))
        board[i][j] = temp
        return found

    for i in range(m):
        for j in range(n):
            if board[i][j] == word[0] and dfs(i, j, 0):
                return True
    return False


# ============================================================
#  九、数据结构相关 (Data Structure Operations)
# ============================================================

class LRUCache:
    """LRU 缓存 (Least Recently Used)"""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.order = deque()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.order.remove(key)
        self.order.append(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            oldest = self.order.popleft()
            del self.cache[oldest]
        self.cache[key] = value
        self.order.append(key)


class UnionFind:
    """并查集 (Disjoint Set Union)"""
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # 路径压缩
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            self.parent[px] = py
        elif self.rank[px] > self.rank[py]:
            self.parent[py] = px
        else:
            self.parent[py] = px
            self.rank[px] += 1
        self.count -= 1
        return True

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)


class TrieNode:
    """前缀树 (Trie) 节点"""
    def __init__(self):
        self.children = {}
        self.is_end = False


class Trie:
    """前缀树 (Trie)"""
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._find(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        return self._find(prefix) is not None

    def _find(self, s: str) -> TrieNode:
        node = self.root
        for ch in s:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node


class FenwickTree:
    """树状数组 (Binary Indexed Tree) - 单点更新，区间查询"""
    def __init__(self, n: int):
        self.n = n
        self.tree = [0] * (n + 1)

    def update(self, idx: int, delta: int) -> None:
        idx += 1
        while idx <= self.n:
            self.tree[idx] += delta
            idx += idx & -idx

    def query(self, idx: int) -> int:
        """前缀和 [0, idx]"""
        idx += 1
        result = 0
        while idx > 0:
            result += self.tree[idx]
            idx -= idx & -idx
        return result

    def range_query(self, left: int, right: int) -> int:
        return self.query(right) - self.query(left - 1)


class SegmentTree:
    """线段树 - 区间更新，区间查询"""
    def __init__(self, data: List[int]):
        self.n = len(data)
        self.tree = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        self._build(data, 0, 0, self.n - 1)

    def _build(self, data, node, left, right):
        if left == right:
            self.tree[node] = data[left]
            return
        mid = (left + right) // 2
        self._build(data, node * 2 + 1, left, mid)
        self._build(data, node * 2 + 2, mid + 1, right)
        self.tree[node] = self.tree[node * 2 + 1] + self.tree[node * 2 + 2]

    def _push(self, node, left, right):
        if self.lazy[node] != 0:
            self.tree[node] += (right - left + 1) * self.lazy[node]
            if left != right:
                self.lazy[node * 2 + 1] += self.lazy[node]
                self.lazy[node * 2 + 2] += self.lazy[node]
            self.lazy[node] = 0

    def update_range(self, ql: int, qr: int, delta: int, node=0, left=0, right=None):
        if right is None:
            right = self.n - 1
        self._push(node, left, right)
        if ql > right or qr < left:
            return
        if ql <= left and right <= qr:
            self.lazy[node] += delta
            self._push(node, left, right)
            return
        mid = (left + right) // 2
        self.update_range(ql, qr, delta, node * 2 + 1, left, mid)
        self.update_range(ql, qr, delta, node * 2 + 2, mid + 1, right)
        self.tree[node] = self.tree[node * 2 + 1] + self.tree[node * 2 + 2]

    def query_range(self, ql: int, qr: int, node=0, left=0, right=None) -> int:
        if right is None:
            right = self.n - 1
        self._push(node, left, right)
        if ql > right or qr < left:
            return 0
        if ql <= left and right <= qr:
            return self.tree[node]
        mid = (left + right) // 2
        return (self.query_range(ql, qr, node * 2 + 1, left, mid) +
                self.query_range(ql, qr, node * 2 + 2, mid + 1, right))


# ============================================================
#  十、贪心算法 (Greedy)
# ============================================================

def activity_selection(starts: List[int], finishes: List[int]) -> List[int]:
    """活动选择问题 - 最大不重叠活动数"""
    n = len(starts)
    activities = sorted(zip(starts, finishes, range(n)), key=lambda x: x[1])
    selected = [activities[0][2]]
    last_finish = activities[0][1]
    for s, f, idx in activities[1:]:
        if s >= last_finish:
            selected.append(idx)
            last_finish = f
    return selected


def huffman_coding(freq: dict) -> dict:
    """哈夫曼编码"""
    heap = [(f, ch, "") for ch, f in freq.items()]
    heapq.heapify(heap)
    codes = {}
    while len(heap) > 1:
        f1, ch1, code1 = heapq.heappop(heap)
        f2, ch2, code2 = heapq.heappop(heap)
        for ch, code in [(ch1, code1 + "0"), (ch2, code2 + "1")]:
            if isinstance(ch, str) and len(ch) == 1:  # 叶子节点
                codes[ch] = code
            else:
                heapq.heappush(heap, (f1 + f2, ch, code))
        heapq.heappush(heap, (f1 + f2, f"{ch1}{ch2}", code1 + code2))
    return codes


def interval_scheduling(intervals: List[Tuple[int, int]]) -> int:
    """区间调度 - 最少箭数射爆气球"""
    intervals.sort(key=lambda x: x[1])
    count = 0
    arrow = float('-inf')
    for start, end in intervals:
        if start > arrow:
            count += 1
            arrow = end
    return count


def jump_game(nums: List[int]) -> int:
    """跳跃游戏 II - 最少步数到达终点"""
    n = len(nums)
    jumps = cur_end = cur_farthest = 0
    for i in range(n - 1):
        cur_farthest = max(cur_farthest, i + nums[i])
        if i == cur_end:
            jumps += 1
            cur_end = cur_farthest
    return jumps


# ============================================================
#  十一、位运算技巧 (Bit Manipulation)
# ============================================================

def count_set_bits(n: int) -> int:
    """统计二进制中 1 的个数 (Brian Kernighan)"""
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count


def is_power_of_two(n: int) -> bool:
    """判断是否为 2 的幂"""
    return n > 0 and (n & (n - 1)) == 0


def single_number(arr: List[int]) -> int:
    """数组中只出现一次的数字 (其余出现两次)"""
    result = 0
    for x in arr:
        result ^= x
    return result


def single_number_iii(arr: List[int]) -> Tuple[int, int]:
    """数组中两个只出现一次的数字 (其余出现两次)"""
    xor = 0
    for x in arr:
        xor ^= x
    # 找到最右边的 1
    lsb = xor & -xor
    a = b = 0
    for x in arr:
        if x & lsb:
            a ^= x
        else:
            b ^= x
    return a, b


def reverse_bits(n: int, bit_width: int = 32) -> int:
    """反转二进制位"""
    result = 0
    for _ in range(bit_width):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result


def get_bit(n: int, i: int) -> int:
    """获取第 i 位"""
    return (n >> i) & 1


def set_bit(n: int, i: int) -> int:
    """设置第 i 位为 1"""
    return n | (1 << i)


def clear_bit(n: int, i: int) -> int:
    """清除第 i 位"""
    return n & ~(1 << i)


def toggle_bit(n: int, i: int) -> int:
    """翻转第 i 位"""
    return n ^ (1 << i)


# ============================================================
#  十二、其他实用算法
# ============================================================

def reservoir_sampling(stream, k: int) -> List:
    """蓄水池抽样 - 从流中随机选 k 个"""
    import random
    reservoir = []
    for i, item in enumerate(stream):
        if i < k:
            reservoir.append(item)
        else:
            j = random.randint(0, i)
            if j < k:
                reservoir[j] = item
    return reservoir


def next_permutation(arr: List[int]) -> bool:
    """下一个排列 (in-place)，返回是否有下一个"""
    n = len(arr)
    i = n - 2
    while i >= 0 and arr[i] >= arr[i + 1]:
        i -= 1
    if i < 0:
        return False
    j = n - 1
    while arr[j] <= arr[i]:
        j -= 1
    arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1:] = reversed(arr[i + 1:])
    return True


def sliding_window_max(arr: List[int], k: int) -> List[int]:
    """滑动窗口最大值 O(n)"""
    result = []
    dq = deque()  # 存储索引
    for i in range(len(arr)):
        if dq and dq[0] <= i - k:
            dq.popleft()
        while dq and arr[dq[-1]] < arr[i]:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(arr[dq[0]])
    return result


def median_of_two_sorted(arr1: List[int], arr2: List[int]) -> float:
    """两个有序数组的中位数 O(log(min(m,n)))"""
    if len(arr1) > len(arr2):
        arr1, arr2 = arr2, arr1
    m, n = len(arr1), len(arr2)
    lo, hi = 0, m
    while lo <= hi:
        i = (lo + hi) // 2
        j = (m + n + 1) // 2 - i
        max_left1 = arr1[i - 1] if i > 0 else float('-inf')
        min_right1 = arr1[i] if i < m else float('inf')
        max_left2 = arr2[j - 1] if j > 0 else float('-inf')
        min_right2 = arr2[j] if j < n else float('inf')
        if max_left1 <= min_right2 and max_left2 <= min_right1:
            if (m + n) % 2 == 0:
                return (max(max_left1, max_left2) + min(min_right1, min_right2)) / 2
            else:
                return max(max_left1, max_left2)
        elif max_left1 > min_right2:
            hi = i - 1
        else:
            lo = i + 1
    raise ValueError("输入数组未排序")


def trap_rain_water(height: List[int]) -> int:
    """接雨水 - 双指针法 O(n)"""
    if not height:
        return 0
    left, right = 0, len(height) - 1
    left_max = right_max = 0
    water = 0
    while left < right:
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                water += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1
    return water


def largest_rectangle_area(heights: List[int]) -> int:
    """柱状图中最大矩形面积 O(n)"""
    stack = []
    max_area = 0
    heights.append(0)  # 哨兵
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)
    heights.pop()
    return max_area


def rotate_matrix(matrix: List[List[int]]) -> List[List[int]]:
    """旋转矩阵 90° 顺时针 (in-place)"""
    n = len(matrix)
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for i in range(n):
        matrix[i].reverse()
    return matrix


def spiral_order(matrix: List[List[int]]) -> List[int]:
    """螺旋矩阵遍历"""
    if not matrix:
        return []
    result = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            result.append(matrix[top][j])
        top += 1
        for i in range(top, bottom + 1):
            result.append(matrix[i][right])
        right -= 1
        if top <= bottom:
            for j in range(right, left - 1, -1):
                result.append(matrix[bottom][j])
            bottom -= 1
        if left <= right:
            for i in range(bottom, top - 1, -1):
                result.append(matrix[i][left])
            left += 1
    return result


def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
    """合并区间"""
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


# ============================================================
#  测试入口
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("排序算法测试")
    print("=" * 60)
    test_arr = [64, 34, 25, 12, 22, 11, 90]
    print(f"原数组: {test_arr}")
    print(f"冒泡排序: {bubble_sort(test_arr[:])}")
    print(f"选择排序: {selection_sort(test_arr[:])}")
    print(f"插入排序: {insertion_sort(test_arr[:])}")
    print(f"归并排序: {merge_sort(test_arr[:])}")
    print(f"快速排序: {quick_sort(test_arr[:])}")
    print(f"快速排序(原地): {quick_sort_inplace(test_arr[:])}")
    print(f"堆排序: {heap_sort(test_arr[:])}")
    print(f"计数排序: {counting_sort(test_arr[:])}")
    print(f"希尔排序: {shell_sort(test_arr[:])}")

    print("\n" + "=" * 60)
    print("搜索算法测试")
    print("=" * 60)
    sorted_arr = [1, 3, 5, 7, 9, 11, 13, 15]
    print(f"有序数组: {sorted_arr}")
    print(f"二分查找 7: 索引 {binary_search(sorted_arr, 7)}")
    print(f"二分查找 8: 索引 {binary_search(sorted_arr, 8)}")
    print(f"最左边界 7: {binary_search_leftmost(sorted_arr, 7)}")
    print(f"跳跃搜索 11: 索引 {jump_search(sorted_arr, 11)}")

    print("\n" + "=" * 60)
    print("图论算法测试")
    print("=" * 60)
    graph = {
        "A": ["B", "C"],
        "B": ["A", "D", "E"],
        "C": ["A", "F"],
        "D": ["B"],
        "E": ["B", "F"],
        "F": ["C", "E"]
    }
    print(f"BFS: {bfs(graph, 'A')}")
    print(f"DFS(迭代): {dfs_iterative(graph, 'A')}")
    print(f"DFS(递归): {dfs_recursive(graph, 'A')}")

    weighted_graph = {
        "A": {"B": 1, "C": 4},
        "B": {"A": 1, "C": 2, "D": 5},
        "C": {"A": 4, "B": 2, "D": 1},
        "D": {"B": 5, "C": 1}
    }
    print(f"Dijkstra: {dijkstra(weighted_graph, 'A')}")

    print("\n" + "=" * 60)
    print("动态规划测试")
    print("=" * 60)
    print(f"0-1背包: {knapsack_01([2,3,4,5], [3,4,5,6], 8)}")
    print(f"LCS: {longest_common_subsequence('abcde', 'ace')}")
    print(f"LCS 字符串: {longest_common_subsequence_str('abcde', 'ace')}")
    print(f"LIS 长度: {longest_increasing_subsequence([10,9,2,5,3,7,101,18])}")
    print(f"LIS 序列: {longest_increasing_subsequence_arr([10,9,2,5,3,7,101,18])}")
    print(f"编辑距离: {edit_distance('horse', 'ros')}")
    print(f"最大子数组和: {max_subarray_sum([-2,1,-3,4,-1,2,1,-5,4])}")
    print(f"最大子数组范围: {max_subarray_range([-2,1,-3,4,-1,2,1,-5,4])}")

    print("\n" + "=" * 60)
    print("字符串算法测试")
    print("=" * 60)
    print(f"KMP: {kmp_search('ababcabcabababd', 'ababd')}")
    print(f"Rabin-Karp: {rabin_karp('ababcabcabababd', 'ababd')}")
    print(f"Manacher 最长回文: {manacher('babad')}")
    print(f"回文子串数: {count_palindromic_substrings('aaa')}")

    print("\n" + "=" * 60)
    print("数学算法测试")
    print("=" * 60)
    print(f"GCD(48,18): {gcd(48, 18)}")
    print(f"LCM(12,18): {lcm(12, 18)}")
    print(f"素数列表(<=50): {sieve_of_eratosthenes(50)}")
    print(f"质因数分解(84): {prime_factors(84)}")
    print(f"快速幂(2,10): {fast_pow(2, 10)}")
    print(f"快速幂取模(2,10,1000): {fast_pow(2, 10, 1000)}")
    print(f"斐波那契(20): {fibonacci(20)}")
    print(f"斐波那契矩阵(20): {fibonacci_matrix(20)}")
    print(f"第10个丑数: {nth_ugly_number(10)}")
    print(f"4皇后解数: {n_queens_count(4)}")

    print("\n" + "=" * 60)
    print("回溯算法测试")
    print("=" * 60)
    print(f"排列 [1,2,3]: {permutations([1,2,3])}")
    print(f"组合 C(4,2): {combinations([1,2,3,4], 2)}")
    print(f"子集 [1,2,3]: {subsets([1,2,3])}")
    print(f"括号生成 n=3: {generate_parentheses(3)}")

    print("\n" + "=" * 60)
    print("数据结构测试")
    print("=" * 60)
    lru = LRUCache(2)
    lru.put(1, 1); lru.put(2, 2)
    print(f"LRU get(1): {lru.get(1)}")
    lru.put(3, 3)
    print(f"LRU get(2) after put(3): {lru.get(2)}")

    uf = UnionFind(5)
    uf.union(0, 1); uf.union(1, 2)
    print(f"并查集 connected(0,2): {uf.connected(0, 2)}")
    print(f"并查集 connected(0,3): {uf.connected(0, 3)}")

    trie = Trie()
    for w in ["apple", "app", "banana"]:
        trie.insert(w)
    print(f"Trie search 'app': {trie.search('app')}")
    print(f"Trie startsWith 'ban': {trie.starts_with('ban')}")

    bit = FenwickTree(5)
    for i, v in enumerate([1, 3, 5, 7, 9]):
        bit.update(i, v)
    print(f"树状数组 range_query(1,3): {bit.range_query(1, 3)}")

    print("\n" + "=" * 60)
    print("贪心 & 其他算法测试")
    print("=" * 60)
    print(f"接雨水: {trap_rain_water([0,1,0,2,1,0,1,3,2,1,2,1])}")
    print(f"最大矩形面积: {largest_rectangle_area([2,1,5,6,2,3])}")
    print(f"滑动窗口最大值: {sliding_window_max([1,3,-1,-3,5,3,6,7], 3)}")
    print(f"合并区间: {merge_intervals([[1,3],[2,6],[8,10],[15,18]])}")
    print(f"中位数: {median_of_two_sorted([1,3,8], [7,9,10,11])}")
    print(f"跳跃游戏II: {jump_game([2,3,1,1,4])}")
    print(f"活动选择: {activity_selection([1,3,0,5,8,5], [2,4,6,7,9,9])}")

    print("\n" + "=" * 60)
    print("位运算测试")
    print("=" * 60)
    print(f"1的个数(13): {count_set_bits(13)}")  # 1101 -> 3
    print(f"2的幂(16): {is_power_of_two(16)}")
    print(f"只出现一次: {single_number([4,1,2,1,2])}")
    print(f"反转32位(1): {reverse_bits(1)}")

    print("\n[OK] 所有算法测试完成!")