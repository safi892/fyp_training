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
| anchors quoting a real line | 84/91 (92%) |
| named a container the code declares | 3/3 |
| named a container that is not there | 0/6 |
| loops described as recursive | 1/3 |

Whether an explanation is *correct overall* is not scored here. That needs a
known-truth label for each program; these are the checks that can be made
without one. Read the prose below before quoting any number above.

---

## tree_inorder — recursive

- anchors: 0 exact, 13 relocated, **2 quoting a line that is not in the file**, of 15
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
| 10 | `Node* root = new Node(8);` | Create the binary tree: 8 (root) → 3 → 1 → 6 → 4 → 7 → 10 → 13 → 14 |
| 11 | `root->left = new Node(3);` | left subtree: 3 → 1 → 6 → 4 → 7 |
| 12 | `root->right = new Node(10);` | right subtree: 10 → 13 → 14 |
| 13 | `root->left->left = new Node(1);` | left‑left subtree: 1 |
| 14 | `root->left->right = new Node(6);` | left‑right subtree: 6 → 4 → 7 |
| 15 | `root->left->right->left = new Node(4);` | left‑right‑left subtree: 4 |
| 16 | `root->left->right->right = new Node(7);` | left‑right‑right subtree: 7 |
| 17 | `root->right->right = new Node(14);` | right‑right subtree: 13 → 14 |
| 18 | `root->right->right->left = new Node(13);` | right‑right‑left subtree: 13 |
| 21 | `if (node == nullptr) return;` | Base case: stop recursion when reaching a null pointer |
| 22 | `inorder(node->left);` | Visit left subtree first (in‑order traversal) |
| 23 | `cout << node->value << " ";` | Output current node's value |
| 24 | `inorder(node->right);` | Visit right subtree next |
| 27 | `Node* root = sample();` | Build the sample tree |
| 28 | `inorder(sample()); cout << "\n";` | Perform inorder traversal and output result |

**Explanation**

Purpose: Prints the values of a binary tree in in‑order traversal.  
Input: Node* root – pointer to the root of the binary tree (or nullptr).  
Output: void – writes the inorder sequence to standard output followed by a newline.  
Algorithm: Recursively visits the left subtree, outputs the current node’s value, then visits the right subtree. The recursion stops when a null pointer is encountered.

---

## tree_inorder — iterative

- anchors: 1 exact, 18 relocated, **1 quoting a line that is not in the file**, of 20
- containers in the code: stack

  - *container named*: Create the binary tree: 8 (root) → 3 → 1 → 6 → 4 → 7 → 10 → 13 → 14 left subtree: 3 → 1 → 6 → 4 → 7 right subtree: 10 → 13 → 14 left‑left: 1 left‑right: 6 left‑right‑left: 4 left‑right‑right: 7 right‑right: 14 right‑right‑left: 13 Iterative inorder traversal using a stack Continue until all nodes are processed Reach the leftmost node of the current subtree Push the current node onto the stack Move to the left child Pop the node from the stack Remove the node from the stack Output the node's value Move to the right child If the stack is empty, we have processed the entire tree main function Purpose: Perform an in‑order traversal of a binary tree and print node values.
  - *container named*: Algorithm: Initialize a stack and repeatedly push nodes onto it while they have left children, then pop the top node, output its value, and push its right child.

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
| 10 | `Node* root = new Node(8);` | Create the binary tree: 8 (root) → 3 → 1 → 6 → 4 → 7 → 10 → 13 → 14 |
| 11 | `root->left = new Node(3);` | left subtree: 3 → 1 → 6 → 4 → 7 |
| 12 | `root->right = new Node(10);` | right subtree: 10 → 13 → 14 |
| 13 | `root->left->left = new Node(1);` | left‑left: 1 |
| 14 | `root->left->right = new Node(6);` | left‑right: 6 |
| 15 | `root->left->right->left = new Node(4);` | left‑right‑left: 4 |
| 16 | `root->left->right->right = new Node(7);` | left‑right‑right: 7 |
| 17 | `root->right->right = new Node(14);` | right‑right: 14 |
| 18 | `root->right->right->left = new Node(13);` | right‑right‑left: 13 |
| 21 | `stack<Node*> pending;` | Iterative inorder traversal using a stack |
| 22 | `while (node != nullptr \|\| !pending.empty()) {` | Continue until all nodes are processed |
| 23 | `while (node != nullptr) {` | Reach the leftmost node of the current subtree |
| 24 | `pending.push(node);` | Push the current node onto the stack |
| 25 | `node = node->left;` | Move to the left child |
| 27 | `node = pending.top();` | Pop the node from the stack |
| 28 | `pending.pop();` | Remove the node from the stack |
| 29 | `cout << node->value << " ";` | Output the node's value |
| 30 | `node = node->right;` | Move to the right child |
| 32 | `}` | If the stack is empty, we have processed the entire tree |
| 34 | `return 0;` | main function |

**Explanation**

Purpose: Perform an in‑order traversal of a binary tree and print node values.  
Input: Node* root – pointer to the root of the binary tree (sample() builds a predefined tree).  
Output: void – writes the inorder traversal to standard output followed by a newline.  
Algorithm: Initialize a stack and repeatedly push nodes onto it while they have left children, then pop the top node, output its value, and push its right child. Continue until the stack is empty and the current node is null.

---

## tree_height — recursive

- anchors: 0 exact, 13 relocated, **1 quoting a line that is not in the file**, of 14
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
| 10 | `Node* root = new Node(8);` | Create the binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 11 | `root->left = new Node(3);` | left child of 8 |
| 12 | `root->right = new Node(10);` | right child of 8 |
| 13 | `root->left->left = new Node(1);` | left child of 3 |
| 14 | `root->left->right = new Node(6);` | right child of 3 |
| 15 | `root->left->right->left = new Node(4);` | left child of 6 |
| 16 | `root->left->right->right = new Node(7);` | right child of 6 |
| 17 | `root->right->right = new Node(14);` | right child of 10 |
| 18 | `root->right->right->left = new Node(13);` | left child of 14 |
| 21 | `if (node == nullptr) return 0;` | Base case: empty subtree has height 0 |
| 22 | `int left = height(node->left);` | Recursively compute height of left subtree |
| 23 | `int right = height(node->right);` | Recursively compute height of right subtree |
| 24 | `return 1 + (left > right ? left : right);` | Return 1 plus the larger of the two heights |
| 27 | `cout << height(sample()) << "\n";` | Print the height of the constructed tree |

**Explanation**

Purpose: Compute the height of a binary tree.  
Input: Node* root – pointer to the root of the tree (or nullptr for an empty tree).  
Output: int – the maximum depth of the tree (0 for an empty tree).  
Algorithm: Perform a post‑order traversal, recursively calculating the height of each subtree and returning the larger of the two heights plus one. The recursion stops when a null pointer is encountered.

---

## tree_height — iterative

- anchors: 0 exact, 22 relocated, **1 quoting a line that is not in the file**, of 23
- containers in the code: queue

  - *container named*: Create the binary tree structure: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 left child of 8 right child of 8 left child of 3 right child of 3 left child of 6 right child of 6 right child of 10 left child of 14 Base case: an empty subtree has height 0 BFS traversal queue start BFS from the root counter for the number of levels continue until all levels are processed number of nodes in the current BFS level process each node in the current level front node of the queue remove the front node from the queue enqueue left child if it exists enqueue right child if it exists increment level counter total number of levels in the tree Print the height of the constructed tree Purpose: Compute the maximum number of nodes at any depth in a binary tree.
  - *container named*: Algorithm: Perform a breadth‑first traversal using a queue, counting nodes per level until the queue becomes empty.

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
| 10 | `Node* root = new Node(8);` | Create the binary tree structure: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 11 | `root->left = new Node(3);` | left child of 8 |
| 12 | `root->right = new Node(10);` | right child of 8 |
| 13 | `root->left->left = new Node(1);` | left child of 3 |
| 14 | `root->left->right = new Node(6);` | right child of 3 |
| 15 | `root->left->right->left = new Node(4);` | left child of 6 |
| 16 | `root->left->right->right = new Node(7);` | right child of 6 |
| 17 | `root->right->right = new Node(14);` | right child of 10 |
| 18 | `root->right->right->left = new Node(13);` | left child of 14 |
| 21 | `if (node == nullptr) return 0;` | Base case: an empty subtree has height 0 |
| 22 | `queue<Node*> level;` | BFS traversal queue |
| 23 | `level.push(node);` | start BFS from the root |
| 24 | `int levels = 0;` | counter for the number of levels |
| 25 | `while (!level.empty()) {` | continue until all levels are processed |
| 26 | `int width = level.size();` | number of nodes in the current BFS level |
| 27 | `for (int i = 0; i < width; i++) {` | process each node in the current level |
| 28 | `Node* current = level.front();` | front node of the queue |
| 29 | `level.pop();` | remove the front node from the queue |
| 30 | `if (current->left) level.push(current->left);` | enqueue left child if it exists |
| 31 | `if (current->right) level.push(current->right);` | enqueue right child if it exists |
| 33 | `levels++;` | increment level counter |
| 36 | `return levels;` | total number of levels in the tree |
| 40 | `cout << height(sample()) << "\n";` | Print the height of the constructed tree |

**Explanation**

Purpose: Compute the maximum number of nodes at any depth in a binary tree.  
Input: Node* root – pointer to the root of the binary tree (or nullptr for an empty tree).  
Output: int – height of the tree (0 for an empty tree).  
Algorithm: Perform a breadth‑first traversal using a queue, counting nodes per level until the queue becomes empty. Each time the queue size changes, increment the depth counter. The final counter value is the height.

---

## quicksort_ranges — recursive

- anchors: 0 exact, 7 relocated, **1 quoting a line that is not in the file**, of 8
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
| 10 | `if (low >= high) return;` | Base case: if the sub‑array is empty or a single element, it is already sorted. |
| 11 | `int split = partition(values, low, high);` | Locate the pivot position using the Lomuto partition scheme. |
| 12 | `quicksort(values, low, split - 1);` | Recursively sort the left partition. |
| 13 | `quicksort(values, split + 1, high);` | Recursively sort the right partition. |
| 16 | `vector<int> values = {9, 4, 17, 3, 8, 1, 12, 5, 20, 2, 11};` | Initial sample data; the algorithm will sort this array. |
| 17 | `quicksort(values, 0, values.size() - 1);` | Sort the entire vector in‑place. |
| 18 | `for (int v : values) cout << v << " ";` | Output the sorted array. |
| 19 | `cout << '\n';` | Ensure a newline after the output. |

**Explanation**

Purpose: Sorts a vector of integers in ascending order using the quicksort algorithm.  
Input: `vector<int>& values` – the mutable list to be sorted; `int low` and `int high` – inclusive indices defining the current sub‑range.  
Output: `void` – the vector `values` is reordered in‑place; `int` – the pivot index after partitioning.  
Algorithm: Recursively selects a pivot element from the last element, partitions the remaining elements into two groups (elements ≤ pivot and elements > pivot), and swaps the pivot into its final position. The recursion continues on the left and right partitions until the sub‑range is empty.

---

## quicksort_ranges — iterative

> **describes this loop as recursive**

- anchors: 3 exact, 7 relocated, **1 quoting a line that is not in the file**, of 11
- containers in the code: stack

  - *recursion claim*: Place pivot at its final position Return index of pivot after partition Recursively sort left sub‑array Recursively sort right sub‑array Base case: empty or single element range Select pivot and partition Push left sub‑range for further recursion Push right sub‑range for further recursion Print sorted array Add newline for clarity Success Purpose: Sorts a vector of integers in ascending order using the quicksort algorithm.
  - *recursion claim*: After each recursive call, the left and right sub‑ranges are pushed onto the stack, ensuring the entire range is processed.
  - *container named*: Algorithm: Uses a stack to perform a depth‑first traversal of the range, applying the `partition` helper to locate the pivot and split the range.
  - *container named*: After each recursive call, the left and right sub‑ranges are pushed onto the stack, ensuring the entire range is processed.

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
| 10 | `swap(values[boundary + 1], values[high]);` | Place pivot at its final position |
| 11 | `return boundary + 1;` | Return index of pivot after partition |
| 16 | `ranges.push({low, split - 1});` | Recursively sort left sub‑array |
| 17 | `ranges.push({split + 1, range.second});` | Recursively sort right sub‑array |
| 21 | `if (range.first >= range.second) continue;` | Base case: empty or single element range |
| 23 | `int split = partition(values, range.first, range.second);` | Select pivot and partition |
| 24 | `ranges.push({range.first, split - 1});` | Push left sub‑range for further recursion |
| 25 | `ranges.push({split + 1, range.second});` | Push right sub‑range for further recursion |
| 29 | `for (int v : values) cout << v << " ";` | Print sorted array |
| 30 | `cout << "\n";` | Add newline for clarity |
| 32 | `return 0;` | Success |

**Explanation**

Purpose: Sorts a vector of integers in ascending order using the quicksort algorithm.  
Input: `vector<int>& values` – the mutable list to be sorted; `int low` and `int high` – inclusive indices defining the current sub‑range.  
Output: The same vector `values` is reordered in‑place; the function returns `void`.  
Algorithm: Uses a stack to perform a depth‑first traversal of the range, applying the `partition` helper to locate the pivot and split the range. After each recursive call, the left and right sub‑ranges are pushed onto the stack, ensuring the entire range is processed. The main loop terminates when the stack is empty.

---
