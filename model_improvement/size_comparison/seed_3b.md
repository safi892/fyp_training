# What the model wrote about each program

Each pair is one algorithm written twice, recursively and with an explicit
container, under the **same function name**. A description that follows the
name rather than the code says the same thing about both halves, and is
therefore wrong about one of them.

## Totals

| | |
| --- | ---: |
| programs | 6 |
| valid JSON, of output that finished | 6/6 |
| ran past the token budget | 0/6 |
| anchors quoting a real line | 51/52 (98%) |
| named a container the code declares | 3/3 |
| named a container that is not there | 1/6 |
| loops described as recursive | 1/3 |

Whether an explanation is *correct overall* is not scored here. That needs a
known-truth label for each program; these are the checks that can be made
without one. Read the prose below before quoting any number above.

---

## tree_inorder — recursive

> **names a container the code does not use**

- anchors: 0 exact, 2 relocated, **1 quoting a line that is not in the file**, of 3
- containers in the code: none

  - *container NOT in the code*: Algorithm: The function performs an iterative in‑order traversal using a stack; it pushes nodes onto the stack while descending left, then visits them when no more left children exist, and finally pops nodes to visit right children.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

void inorder(Node* node) {
    if (node == nullptr) return;
    inorder(node->left);
    cout << node->value << " ";
    inorder(node->right);
}

int main() { inorder(sample()); cout << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 12 | `Node* root = new Node(8);` | Build a simple binary tree for testing:          8               / \             3   10            / \ / \           1   6     14  / \            4   7 |
| 20 | `cout << node->value << " ";` | Visit left subtree, then current node, then right subtree |
| 23 | `inorder(sample()); cout << "\n";` | Perform an in‑order traversal of the sample tree and print each node's value |

**Explanation**

Purpose: Prints the values of a binary tree in in‑order traversal.  
Input: A pointer to the root of a binary tree (Node*).  
Output: Writes each node's value to standard output, separated by spaces; returns void.  
Algorithm: The function performs an iterative in‑order traversal using a stack; it pushes nodes onto the stack while descending left, then visits them when no more left children exist, and finally pops nodes to visit right children. The recursion version is equivalent but uses explicit call frames.

---

## tree_inorder — iterative

> **describes this loop as recursive**

- anchors: 0 exact, 5 relocated, **0 quoting a line that is not in the file**, of 5
- containers in the code: stack

  - *recursion claim*: When a node has no left child, it is popped from the stack and its value printed; then the right subtree is processed recursively.
  - *container named*: Iterative inorder traversal using a stack Push current node onto the stack and move to its left subtree Pop the last pushed node (the next inorder node) Visit the node Move to the right subtree for further inorder traversal Purpose: Prints the values of a binary tree in in‑order traversal.
  - *container named*: Algorithm: Uses an explicit stack to simulate recursive left‑traversal while pushing nodes onto the stack.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

void inorder(Node* node) {
    stack<Node*> pending;
    while (node != nullptr || !pending.empty()) {
        while (node != nullptr) {
            pending.push(node);
            node = node->left;
        }
        node = pending.top();
        pending.pop();
        cout << node->value << " ";
        node = node->right;
    }
}

int main() { inorder(sample()); cout << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 12 | `while (node != nullptr \|\| !pending.empty()) {` | Iterative inorder traversal using a stack |
| 14 | `pending.push(node);` | Push current node onto the stack and move to its left subtree |
| 18 | `node = pending.top();` | Pop the last pushed node (the next inorder node) |
| 20 | `cout << node->value << " ";` | Visit the node |
| 21 | `node = node->right;` | Move to the right subtree for further inorder traversal |

**Explanation**

Purpose: Prints the values of a binary tree in in‑order traversal.  
Input: A pointer to the root of a binary tree (Node*).  
Output: Writes each node's value to standard output, separated by spaces; returns void.  
Algorithm: Uses an explicit stack to simulate recursive left‑traversal while pushing nodes onto the stack. When a node has no left child, it is popped from the stack and its value printed; then the right subtree is processed recursively. The loop terminates when both the current node and the stack are empty.

---

## tree_height — recursive

- anchors: 0 exact, 4 relocated, **0 quoting a line that is not in the file**, of 4
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

int height(Node* node) {
    if (node == nullptr) return 0;
    int left = height(node->left);
    int right = height(node->right);
    return 1 + (left > right ? left : right);
}

int main() { cout << height(sample()) << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 12 | `Node* root = new Node(8);` | Build a simple binary tree for testing |
| 15 | `int left = height(node->left);` | Recursively compute heights of sub‑trees |
| 16 | `int right = height(node->right);` | Choose the larger height to determine current depth |
| 17 | `return 1 + (left > right ? left : right);` | Add one for the current node |

**Explanation**

Purpose: Compute the height of a binary tree.  
Input: Node* node – pointer to the root of the binary tree (may be nullptr).  
Output: int – the number of edges on the longest path from the root to a leaf.  
Algorithm: Perform a depth‑first traversal; for each node, recursively compute the heights of its left and right sub‑trees, then return 1 plus the larger of those two heights. The recursion stops when a null pointer is encountered (height 0).

---

## tree_height — iterative

- anchors: 0 exact, 13 relocated, **0 quoting a line that is not in the file**, of 13
- containers in the code: queue

  - *container named*: Build a simple binary tree for testing BFS to count levels start from root number of BFS passes each iteration processes one level nodes at current depth process all nodes in this level current node to examine remove from queue enqueue left child if present enqueue right child if present one more level processed total number of levels Purpose: Compute the number of levels in a binary tree (its height).
  - *container named*: Algorithm: Perform a breadth‑first traversal using a queue; each level is processed until the queue empties, counting how many levels were visited.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <queue>
#include <vector>
using namespace std;

struct Node {
    int value;
    Node *left, *right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* sample() {
    Node* root = new Node(8);
    root->left = new Node(3);
    root->right = new Node(10);
    root->left->left = new Node(1);
    root->left->right = new Node(6);
    root->left->right->left = new Node(4);
    root->left->right->right = new Node(7);
    root->right->right = new Node(14);
    root->right->right->left = new Node(13);
    return root;
}

int height(Node* node) {
    if (node == nullptr) return 0;
    queue<Node*> level;
    level.push(node);
    int levels = 0;
    while (!level.empty()) {
        int width = level.size();
        for (int i = 0; i < width; i++) {
            Node* current = level.front();
            level.pop();
            if (current->left) level.push(current->left);
            if (current->right) level.push(current->right);
        }
        levels++;
    }
    return levels;
}

int main() { cout << height(sample()) << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 13 | `Node* root = new Node(8);` | Build a simple binary tree for testing |
| 24 | `queue<Node*> level;` | BFS to count levels |
| 25 | `level.push(node);` | start from root |
| 26 | `int levels = 0;` | number of BFS passes |
| 27 | `while (!level.empty()) {` | each iteration processes one level |
| 28 | `int width = level.size();` | nodes at current depth |
| 29 | `for (int i = 0; i < width; i++) {` | process all nodes in this level |
| 30 | `Node* current = level.front();` | current node to examine |
| 31 | `level.pop();` | remove from queue |
| 32 | `if (current->left) level.push(current->left);` | enqueue left child if present |
| 33 | `if (current->right) level.push(current->right);` | enqueue right child if present |
| 35 | `levels++;` | one more level processed |
| 37 | `return levels;` | total number of levels |

**Explanation**

Purpose: Compute the number of levels in a binary tree (its height).  
Input: Node* node – pointer to the root of the binary tree.  
Output: int – the height of the tree (number of edges on the longest root‑to‑leaf path).  
Algorithm: Perform a breadth‑first traversal using a queue; each level is processed until the queue empties, counting how many levels were visited. The function returns the total count.

---

## quicksort_ranges — recursive

- anchors: 0 exact, 13 relocated, **0 quoting a line that is not in the file**, of 13
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <utility>
#include <vector>
using namespace std;

int partition(vector<int>& values, int low, int high) {
    int pivot = values[high];
    int boundary = low - 1;
    for (int i = low; i < high; i++)
        if (values[i] <= pivot) swap(values[++boundary], values[i]);
    swap(values[boundary + 1], values[high]);
    return boundary + 1;
}

void quicksort(vector<int>& values, int low, int high) {
    if (low >= high) return;
    int split = partition(values, low, high);
    quicksort(values, low, split - 1);
    quicksort(values, split + 1, high);
}

int main() {
    vector<int> values = {9, 4, 17, 3, 8, 1, 12, 5, 20, 2, 11};
    quicksort(values, 0, values.size() - 1);
    for (int v : values) cout << v << " ";
    cout << "\n";
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 4 | `int pivot = values[high];` | Choose the last element as the pivot |
| 5 | `int boundary = low - 1;` | Boundary separates elements <= pivot from > pivot |
| 6 | `for (int i = low; i < high; i++)` | Scan all elements except the pivot |
| 7 | `if (values[i] <= pivot) swap(values[++boundary], values[i]);` | Move smaller or equal element to the left side of boundary |
| 9 | `swap(values[boundary + 1], values[high]);` | Place pivot at its final position |
| 10 | `return boundary + 1;` | Index of the pivot after partitioning |
| 13 | `if (low >= high) return;` | Base case: empty or single‑element subarray |
| 14 | `int split = partition(values, low, high);` | Partition and obtain pivot index |
| 15 | `quicksort(values, low, split - 1);` | Recursively sort left subarray |
| 16 | `quicksort(values, split + 1, high);` | Recursively sort right subarray |
| 20 | `vector<int> values = {9, 4, 17, 3, 8, 1, 12, 5, 20, 2, 11};` | Initial data to be sorted |
| 21 | `quicksort(values, 0, values.size() - 1);` | Sort the entire vector in place |
| 22 | `for (int v : values) cout << v << " ";` | Output sorted sequence |

**Explanation**

Purpose: Sorts a vector of integers in ascending order using the quicksort algorithm.
Input: A reference to a vector of integers and two integers representing the start and end indices of the subarray to be sorted.
Output: None (the vector is sorted in place).
Algorithm: The function selects a pivot element from the array and partitions the other elements into two sub-arrays, according to whether they are less than or greater than the pivot. The sub-arrays are then recursively sorted.

---

## quicksort_ranges — iterative

- anchors: 0 exact, 14 relocated, **0 quoting a line that is not in the file**, of 14
- containers in the code: stack

  - *container named*: pivot chosen as the last element boundary index for elements <= pivot iterate over all but the pivot element move smaller or equal element to left side place pivot at its final position index of the pivot after partitioning push current sub‑array onto stack process sub‑arrays until stack empty top of the stack is the next sub‑array remove processed sub‑array empty or invalid sub‑array partition and get pivot index push left half for further processing push right half for further processing Purpose: Sorts a vector of integers in ascending order using the quicksort algorithm.
  - *container named*: Algorithm: The function uses a stack to implement an iterative version of quicksort.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <utility>
#include <vector>
using namespace std;

int partition(vector<int>& values, int low, int high) {
    int pivot = values[high];
    int boundary = low - 1;
    for (int i = low; i < high; i++)
        if (values[i] <= pivot) swap(values[++boundary], values[i]);
    swap(values[boundary + 1], values[high]);
    return boundary + 1;
}

void quicksort(vector<int>& values, int low, int high) {
    stack<pair<int, int>> ranges;
    ranges.push({low, high});
    while (!ranges.empty()) {
        pair<int, int> range = ranges.top();
        ranges.pop();
        if (range.first >= range.second) continue;
        int split = partition(values, range.first, range.second);
        ranges.push({range.first, split - 1});
        ranges.push({split + 1, range.second});
    }
}

int main() {
    vector<int> values = {9, 4, 17, 3, 8, 1, 12, 5, 20, 2, 11};
    quicksort(values, 0, values.size() - 1);
    for (int v : values) cout << v << " ";
    cout << "\n";
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 5 | `int pivot = values[high];` | pivot chosen as the last element |
| 6 | `int boundary = low - 1;` | boundary index for elements <= pivot |
| 7 | `for (int i = low; i < high; i++)` | iterate over all but the pivot element |
| 8 | `if (values[i] <= pivot) swap(values[++boundary], values[i]);` | move smaller or equal element to left side |
| 10 | `swap(values[boundary + 1], values[high]);` | place pivot at its final position |
| 12 | `return boundary + 1;` | index of the pivot after partitioning |
| 15 | `ranges.push({low, high});` | push current sub‑array onto stack |
| 16 | `while (!ranges.empty()) {` | process sub‑arrays until stack empty |
| 17 | `pair<int, int> range = ranges.top();` | top of the stack is the next sub‑array |
| 18 | `ranges.pop();` | remove processed sub‑array |
| 19 | `if (range.first >= range.second) continue;` | empty or invalid sub‑array |
| 20 | `int split = partition(values, range.first, range.second);` | partition and get pivot index |
| 21 | `ranges.push({range.first, split - 1});` | push left half for further processing |
| 22 | `ranges.push({split + 1, range.second});` | push right half for further processing |

**Explanation**

Purpose: Sorts a vector of integers in ascending order using the quicksort algorithm.
Input: A vector of integers and two indices representing the current subarray to be sorted.
Output: None (the vector is sorted in place).
Algorithm: The function uses a stack to implement an iterative version of quicksort. It repeatedly partitions the array and pushes the subarrays that need further sorting onto the stack until all subarrays are processed.

---
