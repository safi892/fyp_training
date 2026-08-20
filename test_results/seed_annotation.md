# What the model wrote about each program

Each pair is one algorithm written twice, recursively and with an explicit
container, under the **same function name**. A description that follows the
name rather than the code says the same thing about both halves, and is
therefore wrong about one of them.

## Totals

| | |
| --- | ---: |
| programs | 20 |
| valid JSON, of output that finished | 13/13 |
| ran past the token budget | 7/20 |
| anchors quoting a real line | 176/188 (94%) |
| named a container the code declares | 11/11 |
| named a container that is not there | 1/20 |
| loops described as recursive | 1/10 |

Whether an explanation is *correct overall* is not scored here. That needs a
known-truth label for each program; these are the checks that can be made
without one. Read the prose below before quoting any number above.

---

## tree_inorder — recursive

> output hit the token budget and was cut off

- anchors: 0 exact, 0 relocated, **0 quoting a line that is not in the file**, of 0
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

*no usable line comments (output was cut off or malformed)*

**Explanation**

Purpose: Prints the values of a binary tree in in‑order traversal.  
Input: Node* root – pointer to the root of the binary tree (or nullptr for an empty tree).  
Output: void – writes the inorder sequence to standard output.  
Algorithm: The function recursively visits the left subtree, prints the current node, then visits the right subtree. The recursion stops when a null pointer is encountered.

---

## tree_inorder — iterative

> output hit the token budget and was cut off

- anchors: 0 exact, 0 relocated, **0 quoting a line that is not in the file**, of 0
- containers in the code: stack

  - *container named*: Algorithm: Uses a stack to simulate recursion, pushing nodes onto the stack while traversing left children, popping when a node’s left child is null, and printing the node’s value.
  - *container named*: The process repeats until the stack is empty.

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

*no usable line comments (output was cut off or malformed)*

**Explanation**

Purpose: Prints the values of a binary tree in in‑order traversal.  
Input: Node* root – pointer to the root of the binary tree (or nullptr for an empty tree).  
Output: void – writes the inorder sequence to standard output.  
Algorithm: Uses a stack to simulate recursion, pushing nodes onto the stack while traversing left children, popping when a node’s left child is null, and printing the node’s value. The process repeats until the stack is empty.

---

## tree_preorder — recursive

- anchors: 0 exact, 18 relocated, **1 quoting a line that is not in the file**, of 19
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

void preorder(Node* node) {
    if (node == nullptr) return;
    cout << node->value << " ";
    preorder(node->left);
    preorder(node->right);
}

int main() { preorder(sample()); cout << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 12 | `Node* root = new Node(8);` | Create the root node with value 8 |
| 13 | `root->left = new Node(3);` | Left child of root is 3 |
| 14 | `root->right = new Node(10);` | Right child of root is 10 |
| 15 | `root->left->left = new Node(1);` | Left child of left child is 1 |
| 16 | `root->left->right = new Node(6);` | Right child of left child is 6 |
| 17 | `root->left->right->left = new Node(4);` | Left child of right child of left child is 4 |
| 18 | `root->left->right->right = new Node(7);` | Right child of right child of left child is 7 |
| 19 | `root->right->right = new Node(14);` | Right child of right child is 14 |
| 20 | `root->right->right->left = new Node(13);` | Left child of right child of right child is 13 |
| 22 | `if (node == nullptr) return;` | Base case: stop recursion when reaching a null pointer |
| 23 | `cout << node->value << " ";` | Print the current node's value followed by a space |
| 24 | `preorder(node->left);` | Recurse left subtree |
| 25 | `preorder(node->right);` | Recurse right subtree |
| 28 | `Node* root = new Node(8);` | Build a simple binary tree for testing |
| 30 | `root->left->right->right = new Node(7);` | Insert a node with value 7 as the right child of the right child of the left child |
| 32 | `root->right->right = new Node(14);` | Insert a node with value 14 as the right child of the right child |
| 34 | `root->right->right->left = new Node(13);` | Insert a node with value 13 as the left child of the right child of the right child |
| 36 | `return root;` | Return the constructed tree root |
| 39 | `preorder(sample()); cout << \n; return 0;}` | Call preorder traversal on the sample tree and output the result |

**Explanation**

Purpose: Generates a sample binary tree and prints its preorder traversal.  
Input: None (main calls sample()).  
Output: Prints the node values in preorder order to standard output; returns 0.  
Algorithm: sample() constructs a predefined binary tree; preorder(Node*) recursively visits each node, printing its value and recursing left and right subtrees. The main() function invokes preorder on the root and appends a newline.

---

## tree_preorder — iterative

> output hit the token budget and was cut off

- anchors: 0 exact, 0 relocated, **0 quoting a line that is not in the file**, of 0
- containers in the code: stack

  - *container named*: Algorithm: Initialize a stack with the root, then repeatedly pop the top node, output its value, and push its right child before left child onto the stack until the stack is empty.

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

void preorder(Node* node) {
    if (node == nullptr) return;
    stack<Node*> pending;
    pending.push(node);
    while (!pending.empty()) {
        Node* current = pending.top();
        pending.pop();
        cout << current->value << " ";
        if (current->right) pending.push(current->right);
        if (current->left) pending.push(current->left);
    }
}

int main() { preorder(sample()); cout << "\n"; return 0; }
```

</details>

*no usable line comments (output was cut off or malformed)*

**Explanation**

Purpose: Prints the preorder traversal of a binary tree.  
Input: Node* root – pointer to the root of the tree (or nullptr for an empty tree).  
Output: void – writes the node values in preorder to standard output.  
Algorithm: Initialize a stack with the root, then repeatedly pop the top node, output its value, and push its right child before left child onto the stack until the stack is empty. The function handles an empty tree gracefully.

---

## tree_postorder — recursive

- anchors: 0 exact, 13 relocated, **4 quoting a line that is not in the file**, of 17
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

void postorder(Node* node) {
    if (node == nullptr) return;
    postorder(node->left);
    postorder(node->right);
    cout << node->value << " ";
}

int main() { postorder(sample()); cout << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 12 | `Node* root = new Node(8);` | Create the root node with value 8 |
| 13 | `root->left = new Node(3);` | Left child of root is 3 |
| 14 | `root->right = new Node(10);` | Right child of root is 10 |
| 15 | `root->left->left = new Node(1);` | Left child of left child is 1 |
| 16 | `root->left->right = new Node(6);` | Right child of left child is 6 |
| 17 | `root->left->right->left = new Node(4);` | Left child of right child of left child is 4 |
| 18 | `root->left->right->right = new Node(7);` | Right child of right child of left child is 7 |
| 19 | `root->right->right = new Node(14);` | Right child of right child is 14 |
| 20 | `root->right->right->left = new Node(13);` | Left child of right child of right child is 13 |
| 22 | `if (node == nullptr) return;` | Base case: empty subtree → nothing to print |
| 23 | `postorder(node->left);` | Recurse left subtree first |
| 24 | `postorder(node->right);` | Recurse right subtree second |
| 25 | `cout << node->value << " ";` | Output current node's value |
| 28 | `Node* root = sample();` | Build the sample binary tree |
| 29 | `postorder(sample());` | Perform postorder traversal and print result |
| 30 | `cout << "\n";` | End with newline for clean output |
| 31 | `return 0;` | Success exit |

**Explanation**

Purpose: Prints the values of a binary tree in postorder traversal.  
Input: Node* root – pointer to the root of the binary tree (or nullptr for an empty tree).  
Output: void – writes the node values to standard output in postorder order.  
Algorithm: Recursively traverse the left subtree, then the right subtree, and finally output the current node. The recursion stops when a null pointer is encountered.

---

## tree_postorder — iterative

- anchors: 0 exact, 12 relocated, **1 quoting a line that is not in the file**, of 13
- containers in the code: stack

  - *container named*: Build a sample binary tree: 8 (root) → 3 → 1 → 4 → 7 → 6 → 10 → 13 → 14 Build a sample binary tree: 8 (root) → 3 → 1 → 4 → 7 → 6 → 10 → 13 → 14 Push the current node onto the pending stack for later processing Pop nodes from the stack and output their values in postorder current is the node that will be processed next Remove the node from the pending stack Push the node onto the output stack so its value is printed later Push left child onto the pending stack if it exists Push right child onto the pending stack if it exists Output the values of the nodes in postorder Print the value followed by a space Remove the node from the output stack Return success code Purpose: Prints the values of a binary tree in postorder (left‑right‑root) using a stack.
  - *container named*: Algorithm: Perform a depth‑first traversal using a stack, pushing each node onto the stack while also pushing its children onto the output stack.

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

void postorder(Node* node) {
    if (node == nullptr) return;
    stack<Node*> pending, output;
    pending.push(node);
    while (!pending.empty()) {
        Node* current = pending.top();
        pending.pop();
        output.push(current);
        if (current->left) pending.push(current->left);
        if (current->right) pending.push(current->right);
    }
    while (!output.empty()) {
        cout << output.top()->value << " ";
        output.pop();
    }
}

int main() { postorder(sample()); cout << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 12 | `Node* root = new Node(8);` | Build a sample binary tree: 8 (root) → 3 → 1 → 4 → 7 → 6 → 10 → 13 → 14 |
| 15 | `Node* root = new Node(8);` | Build a sample binary tree: 8 (root) → 3 → 1 → 4 → 7 → 6 → 10 → 13 → 14 |
| 20 | `pending.push(node);` | Push the current node onto the pending stack for later processing |
| 21 | `while (!pending.empty()) {` | Pop nodes from the stack and output their values in postorder |
| 22 | `Node* current = pending.top();` | current is the node that will be processed next |
| 23 | `pending.pop();` | Remove the node from the pending stack |
| 24 | `output.push(current);` | Push the node onto the output stack so its value is printed later |
| 25 | `if (current->left) pending.push(current->left);` | Push left child onto the pending stack if it exists |
| 26 | `if (current->right) pending.push(current->right);` | Push right child onto the pending stack if it exists |
| 30 | `while (!output.empty()) {` | Output the values of the nodes in postorder |
| 31 | `cout << output.top()->value << " ";` | Print the value followed by a space |
| 32 | `output.pop();` | Remove the node from the output stack |
| 35 | `return 0;` | Return success code |

**Explanation**

Purpose: Prints the values of a binary tree in postorder (left‑right‑root) using a stack.  
Input: Node* root – pointer to the root of the binary tree (or nullptr for an empty tree).  
Output: void – writes the postorder sequence to standard output.  
Algorithm: Perform a depth‑first traversal using a stack, pushing each node onto the stack while also pushing its children onto the output stack. After the traversal, pop the output stack to output the nodes in postorder order.

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
| 10 | `Node* root = new Node(8);` | Create the root node with value 8 |
| 11 | `root->left = new Node(3);` | Left child of root is 3 |
| 12 | `root->right = new Node(10);` | Right child of root is 10 |
| 13 | `root->left->left = new Node(1);` | Left child of left child is 1 |
| 14 | `root->left->right = new Node(6);` | Right child of left child is 6 |
| 15 | `root->left->right->left = new Node(4);` | Left child of right child of left child is 4 |
| 16 | `root->left->right->right = new Node(7);` | Right child of right child of left child is 7 |
| 17 | `root->right->right = new Node(14);` | Right child of right child is 14 |
| 18 | `root->right->right->left = new Node(13);` | Left child of right child of right child is 13 |
| 21 | `if (node == nullptr) return 0;` | Base case: empty subtree has height 0 |
| 22 | `int left = height(node->left);` | Recursively compute height of left subtree |
| 23 | `int right = height(node->right);` | Recursively compute height of right subtree |
| 24 | `return 1 + (left > right ? left : right);` | Return 1 plus the larger height |
| 27 | `cout << height(sample()) << "\n";` | Print the height of the sample tree |

**Explanation**

Purpose: Compute the height of a binary tree.  
Input: Node* root – pointer to the root of the tree (or nullptr for an empty tree).  
Output: int – the maximum depth of the tree (0 for an empty tree).  
Algorithm: Perform a post‑order traversal, recursively obtaining the height of each subtree, and return 1 + the larger of the two heights. The recursion naturally handles the empty‑tree case.

---

## tree_height — iterative

- anchors: 0 exact, 22 relocated, **1 quoting a line that is not in the file**, of 23
- containers in the code: queue

  - *container named*: Create the root node with value 8 Left child of root is 3 Right child of root is 10 Left child of left child is 1 Right child of left child is 6 Left child of right child of left child is 4 Right child of right child of left child is 7 Right child of right child is 14 Left child of right child of right child is 13 Base case: empty subtree has height 0 BFS queue for level traversal Start BFS from the root Counter for the number of levels Process each level of the tree Number of nodes in the current level Traverse all nodes in the current level Front node of the current level Remove the front node from the queue Enqueue left child if it exists Enqueue right child if it exists Increment level counter Return the total number of levels Print the height of the generated sample tree Purpose: Compute the height of a binary tree using a breadth‑first traversal.
  - *container named*: Algorithm: Perform a level‑order traversal using a queue, counting each level as a new height level.

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
| 10 | `Node* root = new Node(8);` | Create the root node with value 8 |
| 11 | `root->left = new Node(3);` | Left child of root is 3 |
| 12 | `root->right = new Node(10);` | Right child of root is 10 |
| 13 | `root->left->left = new Node(1);` | Left child of left child is 1 |
| 14 | `root->left->right = new Node(6);` | Right child of left child is 6 |
| 15 | `root->left->right->left = new Node(4);` | Left child of right child of left child is 4 |
| 16 | `root->left->right->right = new Node(7);` | Right child of right child of left child is 7 |
| 17 | `root->right->right = new Node(14);` | Right child of right child is 14 |
| 18 | `root->right->right->left = new Node(13);` | Left child of right child of right child is 13 |
| 21 | `if (node == nullptr) return 0;` | Base case: empty subtree has height 0 |
| 22 | `queue<Node*> level;` | BFS queue for level traversal |
| 23 | `level.push(node);` | Start BFS from the root |
| 24 | `int levels = 0;` | Counter for the number of levels |
| 25 | `while (!level.empty()) {` | Process each level of the tree |
| 26 | `int width = level.size();` | Number of nodes in the current level |
| 27 | `for (int i = 0; i < width; i++) {` | Traverse all nodes in the current level |
| 28 | `Node* current = level.front();` | Front node of the current level |
| 29 | `level.pop();` | Remove the front node from the queue |
| 30 | `if (current->left) level.push(current->left);` | Enqueue left child if it exists |
| 31 | `if (current->right) level.push(current->right);` | Enqueue right child if it exists |
| 33 | `levels++;` | Increment level counter |
| 36 | `return levels;` | Return the total number of levels |
| 40 | `cout << height(sample()) << "\n";` | Print the height of the generated sample tree |

**Explanation**

Purpose: Compute the height of a binary tree using a breadth‑first traversal.  
Input: Node* root – pointer to the root of the binary tree (may be nullptr).  
Output: int – the number of levels (height) in the tree.  
Algorithm: Perform a level‑order traversal using a queue, counting each level as a new height level. Return the final count after processing all nodes.

---

## tree_count_leaves — recursive

- anchors: 0 exact, 12 relocated, **1 quoting a line that is not in the file**, of 13
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

int leaves(Node* node) {
    if (node == nullptr) return 0;
    if (node->left == nullptr && node->right == nullptr) return 1;
    return leaves(node->left) + leaves(node->right);
}

int main() { cout << leaves(sample()) << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 12 | `Node* root = new Node(8);` | Create the root node with value 8 |
| 13 | `root->left = new Node(3);` | Left child of root is 3 |
| 14 | `root->right = new Node(10);` | Right child of root is 10 |
| 15 | `root->left->left = new Node(1);` | Left child of left child is 1 |
| 16 | `root->left->right = new Node(6);` | Right child of left child is 6 |
| 17 | `root->left->right->left = new Node(4);` | Left child of right child of left child is 4 |
| 18 | `root->left->right->right = new Node(7);` | Right child of right child of left child is 7 |
| 19 | `root->right->right = new Node(14);` | Right child of right child is 14 |
| 20 | `root->right->right->left = new Node(13);` | Left child of right child of right child is 13 |
| 22 | `if (node == nullptr) return 0;` | Base case: empty subtree contributes 0 leaves |
| 23 | `if (node->left == nullptr && node->right == nullptr) return 1;` | Leaf node: count it |
| 24 | `return leaves(node->left) + leaves(node->right);` | Recursive case: sum leaves of left and right subtrees |
| 27 | `cout << leaves(sample()) << "\n";` | Print the number of leaf nodes in the sample tree |

**Explanation**

Purpose: Counts the number of leaf nodes in a binary tree.  
Input: Node* root – pointer to the root of the binary tree (may be nullptr).  
Output: int – total count of leaf nodes in the tree.  
Algorithm: Perform a depth‑first traversal using recursion; at each node, if both children are null, increment a counter; otherwise recurse on both children and sum their results. The base case returns 0 for null nodes.

---

## tree_count_leaves — iterative

> output hit the token budget and was cut off

- anchors: 0 exact, 0 relocated, **0 quoting a line that is not in the file**, of 0
- containers in the code: stack

  - *container named*: Algorithm: Perform a depth‑first traversal using a stack, incrementing a counter each time a node has no children.

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

int leaves(Node* node) {
    if (node == nullptr) return 0;
    stack<Node*> pending;
    pending.push(node);
    int found = 0;
    while (!pending.empty()) {
        Node* current = pending.top();
        pending.pop();
        if (current->left == nullptr && current->right == nullptr) found++;
        if (current->left) pending.push(current->left);
        if (current->right) pending.push(current->right);
    }
    return found;
}

int main() { cout << leaves(sample()) << "\n"; return 0; }
```

</details>

*no usable line comments (output was cut off or malformed)*

**Explanation**

Purpose: Count the number of leaf nodes in a binary tree.  
Input: Node* root – pointer to the root of the binary tree (may be nullptr).  
Output: int – total count of leaf nodes in the tree.  
Algorithm: Perform a depth‑first traversal using a stack, incrementing a counter each time a node has no children. The traversal visits nodes in post‑order, ensuring that leaf nodes are counted before their children.

---

## tree_invert — recursive

> output hit the token budget and was cut off

- anchors: 0 exact, 0 relocated, **0 quoting a line that is not in the file**, of 0
- containers in the code: stack

  - *container named*: `main()` uses a stack to perform a post‑order traversal, printing each node’s value.

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

void invert(Node* node) {
    if (node == nullptr) return;
    Node* spare = node->left;
    node->left = node->right;
    node->right = spare;
    invert(node->left);
    invert(node->right);
}

int main() {
    Node* root = sample();
    invert(root);
    stack<Node*> s; s.push(root);
    while (!s.empty()) {
        Node* c = s.top(); s.pop();
        cout << c->value << " ";
        if (c->right) s.push(c->right);
        if (c->left) s.push(c->left);
    }
    cout << "\n";
    return 0;
}
```

</details>

*no usable line comments (output was cut off or malformed)*

**Explanation**

Purpose: Invert a binary tree in‑place and then print its post‑order traversal.  
Input: None (main reads a sample tree via `sample()`).  
Output: Prints the tree’s post‑order sequence to `std::cout`.  
Algorithm: `sample()` builds a predefined binary tree; `invert()` recursively swaps each node’s left and right children, effectively reversing the tree. `main()` uses a stack to perform a post‑order traversal, printing each node’s value.

---

## tree_invert — iterative

- anchors: 0 exact, 21 relocated, **0 quoting a line that is not in the file**, of 21
- containers in the code: queue, stack

  - *container named*: Create the sample binary tree: 8 / \ \ 3 / \ \ 10 / \ \ 1 / \ \ 6 / \ \ 4 / \ \ 7 / \ \ 14 / \ \ 13 Base case: empty subtree – nothing to invert BFS traversal using a queue Start BFS from the root Dequeue the current node Remove it from the queue Store left child before swapping Swap left and right children Restore original left child Enqueue children for further processing Enqueue children for further processing Build the sample tree Invert the tree Perform a post‑order traversal using a stack Pop nodes from the stack and output their values Pop the current node Output the node's value Push right child before left child to achieve post‑order Push left child before right child to achieve post‑order End of traversal Final newline for clean output Purpose: Inverts a binary tree and prints its post‑order traversal.
  - *container named*: Create the sample binary tree: 8 / \ \ 3 / \ \ 10 / \ \ 1 / \ \ 6 / \ \ 4 / \ \ 7 / \ \ 14 / \ \ 13 Base case: empty subtree – nothing to invert BFS traversal using a queue Start BFS from the root Dequeue the current node Remove it from the queue Store left child before swapping Swap left and right children Restore original left child Enqueue children for further processing Enqueue children for further processing Build the sample tree Invert the tree Perform a post‑order traversal using a stack Pop nodes from the stack and output their values Pop the current node Output the node's value Push right child before left child to achieve post‑order Push left child before right child to achieve post‑order End of traversal Final newline for clean output Purpose: Inverts a binary tree and prints its post‑order traversal.

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

void invert(Node* node) {
    if (node == nullptr) return;
    queue<Node*> pending;
    pending.push(node);
    while (!pending.empty()) {
        Node* current = pending.front();
        pending.pop();
        Node* spare = current->left;
        current->left = current->right;
        current->right = spare;
        if (current->left) pending.push(current->left);
        if (current->right) pending.push(current->right);
    }
}

int main() {
    Node* root = sample();
    invert(root);
    stack<Node*> s; s.push(root);
    while (!s.empty()) {
        Node* c = s.top(); s.pop();
        cout << c->value << " ";
        if (c->right) s.push(c->right);
        if (c->left) s.push(c->left);
    }
    cout << "\n";
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 12 | `Node* root = new Node(8);` | Create the sample binary tree: 8 / \ \ 3 / \ \ 10 / \ \ 1 / \ \ 6 / \ \ 4 / \ \ 7 / \ \ 14 / \ \ 13 |
| 17 | `if (node == nullptr) return;` | Base case: empty subtree – nothing to invert |
| 18 | `queue<Node*> pending;` | BFS traversal using a queue |
| 19 | `pending.push(node);` | Start BFS from the root |
| 22 | `Node* current = pending.front();` | Dequeue the current node |
| 23 | `pending.pop();` | Remove it from the queue |
| 24 | `Node* spare = current->left;` | Store left child before swapping |
| 25 | `current->left = current->right;` | Swap left and right children |
| 26 | `current->right = spare;` | Restore original left child |
| 27 | `if (current->left) pending.push(current->left);` | Enqueue children for further processing |
| 28 | `if (current->right) pending.push(current->right);` | Enqueue children for further processing |
| 32 | `Node* root = sample();` | Build the sample tree |
| 33 | `invert(root);` | Invert the tree |
| 34 | `stack<Node*> s; s.push(root);` | Perform a post‑order traversal using a stack |
| 35 | `while (!s.empty()) {` | Pop nodes from the stack and output their values |
| 36 | `Node* c = s.top(); s.pop();` | Pop the current node |
| 37 | `cout << c->value << " ";` | Output the node's value |
| 38 | `if (c->right) s.push(c->right);` | Push right child before left child to achieve post‑order |
| 39 | `if (c->left) s.push(c->left);` | Push left child before right child to achieve post‑order |
| 40 | `}` | End of traversal |
| 41 | `cout << "\n";` | Final newline for clean output |

**Explanation**

Purpose: Inverts a binary tree and prints its post‑order traversal.  
Input: `Node* root` – pointer to the root of the binary tree (may be nullptr).  
Output: Prints the values of the tree in post‑order; returns 0.  
Algorithm: Uses a breadth‑first search (BFS) to traverse the tree level‑by‑level, swapping each node’s left and right children. After inversion, a depth‑first search (DFS) visits the tree in post‑order, printing each node’s value.

---

## quicksort_ranges — recursive

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
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
| 10 | `swap(values[boundary + 1], values[high]);` | Place pivot at its final sorted position |
| 11 | `return boundary + 1;` | Return index of pivot after partition |
| 15 | `if (low >= high) return;` | Base case: subarray of size 0 or 1 is already sorted |
| 16 | `int split = partition(values, low, high);` | Partition the subarray around the pivot |
| 17 | `quicksort(values, low, split - 1);` | Recursively sort the left partition |
| 18 | `quicksort(values, split + 1, high);` | Recursively sort the right partition |
| 22 | `for (int v : values) cout << v << " ";` | Print the sorted array |

**Explanation**

Purpose: Sorts a vector of integers in ascending order using the quicksort algorithm.  
Input: `vector<int>& values` – the mutable list to be sorted; `int low` and `int high` – inclusive indices defining the current sub‑array.  
Output: `void` – the vector is reordered in‑place; `int` – the pivot index after partitioning.  
Algorithm: `partition` selects the last element as pivot, partitions the sub‑array so that all elements ≤ pivot appear before it, and places it at the pivot position. `quicksort` recursively sorts the left and right partitions until the sub‑array size is ≤ 1. The `main` demonstrates sorting a sample vector.

---

## quicksort_ranges — iterative

> **describes this loop as recursive**

- anchors: 0 exact, 7 relocated, **1 quoting a line that is not in the file**, of 8
- containers in the code: stack

  - *recursion claim*: Place pivot at its final sorted position Return index of pivot after partitioning Recursively sort left sub‑array Recursively sort right sub‑array Sample dataset to sort Sort the entire vector in‑place Output sorted elements End with newline for clean output Purpose: Sorts a vector of integers in ascending order using the quicksort algorithm.
  - *recursion claim*: Subsequent calls process the left and right partitions, recursively sorting them until the stack is empty.
  - *container named*: Algorithm: Uses a stack to perform a depth‑first traversal of the array, applying the `partition` routine to select a pivot and rearrange elements so that all elements ≤ pivot appear before it and all > pivot appear after.
  - *container named*: Subsequent calls process the left and right partitions, recursively sorting them until the stack is empty.

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
| 10 | `swap(values[boundary + 1], values[high]);` | Place pivot at its final sorted position |
| 11 | `return boundary + 1;` | Return index of pivot after partitioning |
| 16 | `ranges.push({range.first, split - 1});` | Recursively sort left sub‑array |
| 17 | `ranges.push({split + 1, range.second});` | Recursively sort right sub‑array |
| 21 | `vector<int> values = {9, 4, 17, 3, 8, 1, 12, 5, 20, 2, 11};` | Sample dataset to sort |
| 22 | `quicksort(values, 0, values.size() - 1);` | Sort the entire vector in‑place |
| 23 | `for (int v : values) cout << v << " ";` | Output sorted elements |
| 24 | `cout << '\n';` | End with newline for clean output |

**Explanation**

Purpose: Sorts a vector of integers in ascending order using the quicksort algorithm.  
Input: `vector<int>& values` – the array to be sorted; `int low` and `int high` – inclusive indices defining the current sub‑array.  
Output: `void` – the vector `values` is reordered in‑place; `int` – the index of the pivot after partitioning.  
Algorithm: Uses a stack to perform a depth‑first traversal of the array, applying the `partition` routine to select a pivot and rearrange elements so that all elements ≤ pivot appear before it and all > pivot appear after. Subsequent calls process the left and right partitions, recursively sorting them until the stack is empty.

---

## graph_dfs — recursive

- anchors: 0 exact, 7 relocated, **0 quoting a line that is not in the file**, of 7
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <vector>
using namespace std;

vector<vector<int>> graph = {
    {1, 2}, {0, 3, 4}, {0, 5}, {1}, {1, 5}, {2, 4, 6}, {5}
};

void dfs(int node, vector<bool>& seen) {
    if (seen[node]) return;
    seen[node] = true;
    cout << node << " ";
    for (int next : graph[node]) dfs(next, seen);
}

int main() {
    vector<bool> seen(graph.size(), false);
    dfs(0, seen);
    cout << "\n";
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if (seen[node]) return;` | skip already visited vertices to avoid cycles |
| 11 | `seen[node] = true;` | mark current vertex as visited |
| 12 | `cout << node << " ";` | output vertex label (node is 0‑based) |
| 13 | `for (int next : graph[node]) dfs(next, seen);` | recurse on all adjacent vertices |
| 17 | `vector<bool> seen(graph.size(), false);` | initialize visited flag for each vertex |
| 18 | `dfs(0, seen);` | start DFS from vertex 0 |
| 19 | `cout << "\n";` | terminate with newline |

**Explanation**

Purpose: Perform a depth‑first search on an undirected graph and print visited nodes.  
Input: `graph` – adjacency list of the graph; `seen` – vector tracking visited nodes.  
Output: Prints node values in the order they are visited to `std::cout`.  
Algorithm: Initialize a visited flag vector, then recursively visit each node, marking it as seen and outputting it. The recursion stops when a node is already marked, preventing cycles.

---

## graph_dfs — iterative

- anchors: 0 exact, 13 relocated, **0 quoting a line that is not in the file**, of 13
- containers in the code: stack

  - *container named*: stack holds nodes to be explored in reverse post‑order start DFS from the source node process nodes until the stack is empty current node at the top of the stack remove the node from the stack skip already visited nodes to avoid cycles mark the node as visited output the node label visit successors in reverse order to achieve post‑order push only unvisited successors onto the stack mark all nodes as unvisited start DFS from node 0 end with a newline Purpose: Perform a depth‑first traversal of an undirected graph starting from node 0 and print each visited vertex.
  - *container named*: Algorithm: Initialize a stack with the start node and a boolean vector marking visited vertices.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <vector>
using namespace std;

vector<vector<int>> graph = {
    {1, 2}, {0, 3, 4}, {0, 5}, {1}, {1, 5}, {2, 4, 6}, {5}
};

void dfs(int node, vector<bool>& seen) {
    stack<int> pending;
    pending.push(node);
    while (!pending.empty()) {
        int current = pending.top();
        pending.pop();
        if (seen[current]) continue;
        seen[current] = true;
        cout << current << " ";
        for (int i = graph[current].size() - 1; i >= 0; i--)
            if (!seen[graph[current][i]]) pending.push(graph[current][i]);
    }
}

int main() {
    vector<bool> seen(graph.size(), false);
    dfs(0, seen);
    cout << "\n";
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `stack<int> pending;` | stack holds nodes to be explored in reverse post‑order |
| 11 | `pending.push(node);` | start DFS from the source node |
| 12 | `while (!pending.empty()) {` | process nodes until the stack is empty |
| 13 | `int current = pending.top();` | current node at the top of the stack |
| 14 | `pending.pop();` | remove the node from the stack |
| 15 | `if (seen[current]) continue;` | skip already visited nodes to avoid cycles |
| 16 | `seen[current] = true;` | mark the node as visited |
| 17 | `cout << current << " ";` | output the node label |
| 18 | `for (int i = graph[current].size() - 1; i >= 0; i--)` | visit successors in reverse order to achieve post‑order |
| 19 | `if (!seen[graph[current][i]]) pending.push(graph[current][i]);` | push only unvisited successors onto the stack |
| 23 | `vector<bool> seen(graph.size(), false);` | mark all nodes as unvisited |
| 24 | `dfs(0, seen);` | start DFS from node 0 |
| 25 | `cout << "\n";` | end with a newline |

**Explanation**

Purpose: Perform a depth‑first traversal of an undirected graph starting from node 0 and print each visited vertex.  
Input: `graph` – adjacency list of the graph; `seen` – vector tracking visited vertices.  
Output: Prints the vertices in the order they are visited, separated by spaces, followed by a newline.  
Algorithm: Initialize a stack with the start node and a boolean vector marking visited vertices. While the stack is non‑empty, pop the top vertex, mark it visited, output it, and push all unvisited neighbors onto the stack in reverse order to achieve depth‑first traversal. The loop terminates when the stack is empty.

---

## flood_fill — recursive

- anchors: 0 exact, 12 relocated, **0 quoting a line that is not in the file**, of 12
- containers in the code: none

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <utility>
#include <vector>
using namespace std;

int rows, cols;
vector<vector<int>> grid;

void fill(int row, int col, int from, int to) {
    if (row < 0 || row >= rows || col < 0 || col >= cols) return;
    if (grid[row][col] != from) return;
    grid[row][col] = to;
    fill(row + 1, col, from, to);
    fill(row - 1, col, from, to);
    fill(row, col + 1, from, to);
    fill(row, col - 1, from, to);
}

int main() {
    cin >> rows >> cols;
    grid.assign(rows, vector<int>(cols));
    for (int r = 0; r < rows; r++)
        for (int c = 0; c < cols; c++) cin >> grid[r][c];
    fill(0, 0, grid[0][0], 9);
    for (int r = 0; r < rows; r++) {
        for (int c = 0; c < cols; c++) cout << grid[r][c] << " ";
        cout << "\n";
    }
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if (row < 0 \|\| row >= rows \|\| col < 0 \|\| col >= cols) return;` | Reject out‑of‑bounds coordinates; no action needed. |
| 11 | `if (grid[row][col] != from) return;` | Stop recursion if the current cell does not match the source value. |
| 12 | `grid[row][col] = to;` | Replace the cell with the target value. |
| 13 | `fill(row + 1, col, from, to);` | Propagate the fill to all four adjacent cells. |
| 14 | `fill(row - 1, col, from, to);` | Note: the original code had a typo here – should be row‑1. |
| 15 | `fill(row, col + 1, from, to);` | Note: the original code had a typo here – should be col+1. |
| 16 | `fill(row, col - 1, from, to);` | Note: the original code had a typo here – should be col‑1. |
| 20 | `cin >> rows >> cols;` | Read the grid dimensions. |
| 21 | `grid.assign(rows, vector<int>(cols));` | Allocate the grid; using assign avoids manual loop. |
| 22 | `for (int r = 0; r < rows; r++)` | Read the grid cell‑wise; assumes the input fits within the allocated size. |
| 24 | `fill(0, 0, grid[0][0], 9);` | Start the flood‑fill from the top‑left corner. |
| 25 | `for (int r = 0; r < rows; r++) {` | Output the transformed grid. |

**Explanation**

Purpose: Replace the starting cell of a 2‑D grid with a target value while preserving the rest of the grid.  
Input: `rows` and `cols` – dimensions of the grid; `grid` – 2‑D vector of integers representing the original grid.  
Output: Prints the modified grid to standard output.  
Algorithm: Read the grid, locate the starting cell, and recursively flood‑fill it with the target value, propagating to all four orthogonal neighbors. The flood‑fill stops at out‑of‑bounds, non‑matching cells, or already‑visited cells.

---

## flood_fill — iterative

> **names a container the code does not use**

- anchors: 0 exact, 19 relocated, **2 quoting a line that is not in the file**, of 21
- containers in the code: stack

  - *container named*: Algorithm: Perform a depth‑first search using a stack, pushing neighbours only when they are within bounds, have the same original value, and are not yet visited.
  - *container NOT in the code*: BFS queue for flood‑filling.
  - *container NOT in the code*: Remove it from the queue.

<details><summary>the code it was given</summary>

```cpp
#include <iostream>
#include <stack>
#include <utility>
#include <vector>
using namespace std;

int rows, cols;
vector<vector<int>> grid;

void fill(int row, int col, int from, int to) {
    if (from == to) return;
    stack<pair<int, int>> pending;
    pending.push({row, col});
    while (!pending.empty()) {
        pair<int, int> cell = pending.top();
        pending.pop();
        int r = cell.first, c = cell.second;
        if (r < 0 || r >= rows || c < 0 || c >= cols) continue;
        if (grid[r][c] != from) continue;
        grid[r][c] = to;
        pending.push({r - 1, c});
        pending.push({r, c - 1});
        pending.push({r, c + 1});
        pending.push({r + 1, c});
    }
}

int main() {
    cin >> rows >> cols;
    grid.assign(rows, vector<int>(cols));
    for (int r = 0; r < rows; r++)
        for (int c = 0; c < cols; c++) cin >> grid[r][c];
    fill(0, 0, grid[0][0], 9);
    for (int r = 0; r < rows; r++) {
        for (int c = 0; c < cols; c++) cout << grid[r][c] << " ";
        cout << "\n";
    }
    return 0;
}
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `if (from == to) return;` | If the target value is already present, nothing to do. |
| 11 | `stack<pair<int, int>> pending;` | BFS queue for flood‑filling. |
| 12 | `pending.push({row, col});` | Start BFS from the source cell. |
| 14 | `pair<int, int> cell = pending.top();` | Pop the next cell to process. |
| 15 | `pending.pop();` | Remove it from the queue. |
| 16 | `int r = cell.first, c = cell.second;` | Extract coordinates. |
| 17 | `if (r < 0 \|\| r >= rows \|\| c < 0 \|\| c >= cols) continue;` | Skip out‑of‑bounds cells. |
| 18 | `if (grid[r][c] != from) continue;` | Skip cells that are not the source value. |
| 19 | `grid[r][c] = to;` | Replace the source value with the target value. |
| 20 | `pending.push({r - 1, c});` | Enqueue neighbours in clockwise order. |
| 21 | `pending.push({r, c - 1});` | Note: assumes grid is 1‑based; otherwise the neighbour coordinates are incorrect. |
| 22 | `pending.push({r, c + 1});` | Note: assumes grid is 1‑based; otherwise the neighbour coordinates are incorrect. |
| 23 | `pending.push({r + 1, c});` | Note: assumes grid is 1‑based; otherwise the neighbour coordinates are incorrect. |
| 27 | `cin >> rows >> cols;` | Read grid dimensions. |
| 28 | `grid.assign(rows, vector<int>(cols));` | Allocate grid. |
| 29 | `for (int r = 0; r < rows; r++) cin >> grid[r][c];` | Read grid values. |
| 30 | `fill(0, 0, grid[0][0], 9);` | Perform flood‑fill from the top‑left corner. |
| 31 | `for (int r = 0; r < rows; r++) {` | Output the modified grid. |
| 32 | `for (int c = 0; c < cols; c++) cout << grid[r][c] << " ";` | Note: assumes grid is 1‑based; otherwise the neighbour coordinates are incorrect. |
| 33 | `cout << '\n';` | Note: assumes grid is 1‑based; otherwise the neighbour coordinates are incorrect. |
| 34 | `}` | Note: assumes grid is 1‑based; otherwise the neighbour coordinates are incorrect. |

**Explanation**

Purpose: Flood‑fill a 2‑D grid from a starting cell to a target value.  
Input: `rows` and `cols` – grid dimensions; `grid` – 2‑D vector of integers; `fill` parameters – start row, start column, and target value.  
Output: Modifies `grid` in‑place; prints the transformed grid to standard output.  
Algorithm: Perform a depth‑first search using a stack, pushing neighbours only when they are within bounds, have the same original value, and are not yet visited. The search stops when the target value is reached.

---

## sum_digits_tree — recursive

> output hit the token budget and was cut off

- anchors: 0 exact, 0 relocated, **0 quoting a line that is not in the file**, of 0
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

int paths(Node* node, int carried) {
    if (node == nullptr) return 0;
    carried = carried * 10 + node->value;
    if (node->left == nullptr && node->right == nullptr) return carried;
    return paths(node->left, carried) + paths(node->right, carried);
}

int main() { cout << paths(sample(), 0) << "\n"; return 0; }
```

</details>

*no usable line comments (output was cut off or malformed)*

**Explanation**

Purpose: Count all root‑to‑leaf paths whose node values form a decimal number divisible by 10.  
Input: Node* node – pointer to the root of a binary tree; int carried – accumulated value of the current path.  
Output: int – total number of such paths.  
Algorithm: Perform a depth‑first traversal, appending each node’s value to the accumulated carry. When a leaf is reached, test the carry for divisibility by 10; if so, increment the result. The recursion accumulates paths for every node, yielding the final count.

---

## sum_digits_tree — iterative

> output hit the token budget and was cut off

- anchors: 0 exact, 0 relocated, **0 quoting a line that is not in the file**, of 0
- containers in the code: stack

  - *container named*: Algorithm: Perform a depth‑first traversal using a stack, maintaining the accumulated value.
  - *container named*: For each node, push its left child with the new value onto the stack and its right child with the same value, then continue processing the stack.

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

int paths(Node* node, int carried) {
    if (node == nullptr) return 0;
    stack<pair<Node*, int>> pending;
    pending.push({node, carried});
    int total = 0;
    while (!pending.empty()) {
        pair<Node*, int> item = pending.top();
        pending.pop();
        Node* current = item.first;
        int running = item.second * 10 + current->value;
        if (current->left == nullptr && current->right == nullptr) {
            total += running;
            continue;
        }
        if (current->left) pending.push({current->left, running});
        if (current->right) pending.push({current->right, running});
    }
    return total;
}

int main() { cout << paths(sample(), 0) << "\n"; return 0; }
```

</details>

*no usable line comments (output was cut off or malformed)*

**Explanation**

Purpose: Count all paths in a binary tree whose node values form a number that is a multiple of 10.  
Input: Node* root – pointer to the tree’s root (or nullptr for an empty tree); int carried – accumulator for the current number formed by the path so far.  
Output: int – total count of such paths.  
Algorithm: Perform a depth‑first traversal using a stack, maintaining the accumulated value. When a leaf is reached, test if the accumulated number is a multiple of 10 and add it to the result. For each node, push its left child with the new value onto the stack and its right child with the same value, then continue processing the stack.

---
