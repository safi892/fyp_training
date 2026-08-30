# What the model wrote about each program

Each pair is one algorithm written twice, recursively and with an explicit
container, under the **same function name**. A description that follows the
name rather than the code says the same thing about both halves, and is
therefore wrong about one of them.

## Totals

| | |
| --- | ---: |
| programs | 20 |
| valid JSON, of output that finished | 19/19 |
| ran past the token budget | 1/20 |
| anchors quoting a real line | 276/292 (95%) |
| named a container the code declares | 11/11 |
| named a container that is not there | 1/20 |
| loops described as recursive | 1/10 |

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
| 10 | `Node* root = new Node(8);` | Build a simple binary search tree for testing inorder traversal. |
| 11 | `root->left = new Node(3);` | root |
| 12 | `root->right = new Node(10);` | left |
| 13 | `root->left->left = new Node(1);` | left->left |
| 14 | `root->left->right = new Node(6);` | left->right |
| 15 | `root->left->right->left = new Node(4);` | left->right->left |
| 16 | `root->left->right->right = new Node(7);` | left->right->right |
| 17 | `root->right->right = new Node(14);` | right |
| 18 | `root->right->right->left = new Node(13);` | right->left |
| 21 | `if (node == nullptr) return;` | Base case: stop recursion when reaching a null node. |
| 22 | `inorder(node->left);` | Recurse left subtree first. |
| 23 | `cout << node->value << " ";` | Output current node's value. |
| 24 | `inorder(node->right);` | Recurse right subtree next. |
| 27 | `Node* root = sample();` | Build the sample tree; the function returns a pointer to its root. |
| 28 | `inorder(sample()); cout << "\n";` | Perform inorder traversal and output the result. |

**Explanation**

Purpose: Prints the inorder traversal of a binary tree.  
Input: Node* root – pointer to the root of the binary tree (or nullptr).  
Output: void – writes the node values in ascending order to standard output.  
Algorithm: A helper function performs an inorder traversal using recursion; it checks for a null node and stops recursion when reaching a leaf. The main function calls this helper with the sample tree and prints a newline.

---

## tree_inorder — iterative

- anchors: 0 exact, 19 relocated, **0 quoting a line that is not in the file**, of 19
- containers in the code: stack

  - *container named*: Create the sample binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 left subtree: 3 → 1 → 6 → 4 → 7 right subtree: 10 → 14 → 13 left‑left: 1 left‑right: 6 left‑right‑left: 4 left‑right‑right: 7 right‑right: 14 right‑right‑left: 13 In‑order traversal: left → node → right Move to the leftmost node of the current subtree Push the current node onto the stack before moving left Continue traversing left Pop the node from the stack and process it Remove the node from the stack Output the node's value Move to the right child after processing the current node If the stack is empty, we have finished the traversal Sample the tree and print its inorder traversal Purpose: Prints the inorder traversal of a binary tree.
  - *container named*: Algorithm: Perform an iterative inorder traversal using a stack to process nodes while their left children are available.

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
| 10 | `Node* root = new Node(8);` | Create the sample binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 11 | `root->left = new Node(3);` | left subtree: 3 → 1 → 6 → 4 → 7 |
| 12 | `root->right = new Node(10);` | right subtree: 10 → 14 → 13 |
| 13 | `root->left->left = new Node(1);` | left‑left: 1 |
| 14 | `root->left->right = new Node(6);` | left‑right: 6 |
| 15 | `root->left->right->left = new Node(4);` | left‑right‑left: 4 |
| 16 | `root->left->right->right = new Node(7);` | left‑right‑right: 7 |
| 17 | `root->right->right = new Node(14);` | right‑right: 14 |
| 18 | `root->right->right->left = new Node(13);` | right‑right‑left: 13 |
| 22 | `while (node != nullptr \|\| !pending.empty()) {` | In‑order traversal: left → node → right |
| 23 | `while (node != nullptr) {` | Move to the leftmost node of the current subtree |
| 24 | `pending.push(node);` | Push the current node onto the stack before moving left |
| 25 | `node = node->left;` | Continue traversing left |
| 27 | `node = pending.top();` | Pop the node from the stack and process it |
| 28 | `pending.pop();` | Remove the node from the stack |
| 29 | `cout << node->value << " ";` | Output the node's value |
| 30 | `node = node->right;` | Move to the right child after processing the current node |
| 33 | `}` | If the stack is empty, we have finished the traversal |
| 36 | `int main() { inorder(sample()); cout << "\n"; return 0; }` | Sample the tree and print its inorder traversal |

**Explanation**

Purpose: Prints the inorder traversal of a binary tree.  
Input: Node* root – pointer to the root of the binary tree (sample() provides a predefined tree).  
Output: void – writes the node values in ascending order to standard output.  
Algorithm: Perform an iterative inorder traversal using a stack to process nodes while their left children are available. When a node has no left child, pop it, output its value, and push its right child. Continue until the stack is empty.

---

## tree_preorder — recursive

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
| 10 | `Node* root = new Node(8);` | Create the root node with value 8 |
| 11 | `root->left = new Node(3);` | Attach left child with value 3 |
| 12 | `root->right = new Node(10);` | Attach right child with value 10 |
| 13 | `root->left->left = new Node(1);` | Attach left child of left child with value 1 |
| 14 | `root->left->right = new Node(6);` | Attach right child of left child with value 6 |
| 15 | `root->left->right->left = new Node(4);` | Attach left child of right child of left child with value 4 |
| 16 | `root->left->right->right = new Node(7);` | Attach right child of right child of left child with value 7 |
| 17 | `root->right->right = new Node(14);` | Attach right child of right child with value 14 |
| 18 | `root->right->right->left = new Node(13);` | Attach left child of right child of right child with value 13 |
| 21 | `if (node == nullptr) return;` | Base case: if the current node is null, there is nothing to print |
| 22 | `cout << node->value << " ";` | Print the node's value followed by a space |
| 23 | `preorder(node->left);` | Recurse left subtree |
| 24 | `preorder(node->right);` | Recurse right subtree |
| 27 | `Node* root = sample();` | Build a sample binary tree for testing |
| 28 | `preorder(sample()); cout << "\n"; return 0;` | Perform preorder traversal and output the result |

**Explanation**

Purpose: Prints the preorder traversal of a binary tree.  
Input: Node* root – pointer to the root of the binary tree (or nullptr).  
Output: void – writes the node values to standard output in preorder order.  
Algorithm: Calls a helper that recursively visits nodes in preorder, printing each node's value and recursing on left and right children. The main function forwards the result of sample() to this helper.

---

## tree_preorder — iterative

- anchors: 0 exact, 19 relocated, **0 quoting a line that is not in the file**, of 19
- containers in the code: stack

  - *container named*: Create the sample binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 left child of root right child of root left child of left child right child of left child left child of right child right child of right child right child of right child left child of right child Base case: empty subtree – nothing to print Stack used for iterative preorder traversal Push the root onto the stack Pop the top node from the stack Remove the node from the stack Print the node's value Push right child onto stack before left child to achieve left‑to‑right order Push left child onto stack No explicit return; the loop naturally terminates when the stack is empty Sample tree is built once; preorder traversal is performed and printed Purpose: Prints a binary tree in preorder (root‑left‑right) using a stack.
  - *container named*: Algorithm: A stack is used to traverse the tree iteratively.

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

| line | code | comment |
| ---: | --- | --- |
| 10 | `Node* root = new Node(8);` | Create the sample binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 11 | `root->left = new Node(3);` | left child of root |
| 12 | `root->right = new Node(10);` | right child of root |
| 13 | `root->left->left = new Node(1);` | left child of left child |
| 14 | `root->left->right = new Node(6);` | right child of left child |
| 15 | `root->left->right->left = new Node(4);` | left child of right child |
| 16 | `root->left->right->right = new Node(7);` | right child of right child |
| 17 | `root->right->right = new Node(14);` | right child of right child |
| 18 | `root->right->right->left = new Node(13);` | left child of right child |
| 21 | `if (node == nullptr) return;` | Base case: empty subtree – nothing to print |
| 22 | `stack<Node*> pending;` | Stack used for iterative preorder traversal |
| 23 | `pending.push(node);` | Push the root onto the stack |
| 25 | `Node* current = pending.top();` | Pop the top node from the stack |
| 26 | `pending.pop();` | Remove the node from the stack |
| 27 | `cout << current->value << " ";` | Print the node's value |
| 29 | `if (current->right) pending.push(current->right);` | Push right child onto stack before left child to achieve left‑to‑right order |
| 30 | `if (current->left) pending.push(current->left);` | Push left child onto stack |
| 33 | `}` | No explicit return; the loop naturally terminates when the stack is empty |
| 35 | `int main() { preorder(sample()); cout << "\n"; return 0; }` | Sample tree is built once; preorder traversal is performed and printed |

**Explanation**

Purpose: Prints a binary tree in preorder (root‑left‑right) using a stack.  
Input: Node* root – pointer to the root of the binary tree (sample() provides a predefined example).  
Output: void – writes the preorder traversal to standard output.  
Algorithm: A stack is used to traverse the tree iteratively. Starting from the root, each node is popped, its value printed, and its right child is pushed first, followed by its left child. This ensures the left subtree is processed before the right subtree, yielding preorder order.

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
| 10 | `Node* root = new Node(8);` | Create the binary tree: 8 (root) → 3 → 1 → 6 → 4 → 7 → 10 → 13 → 14 |
| 11 | `root->left = new Node(3);` | left subtree: 3 → 1 → 6 → 4 → 7 |
| 12 | `root->right = new Node(10);` | right subtree: 10 → 13 → 14 |
| 13 | `root->left->left = new Node(1);` | left‑left subtree: 1 |
| 14 | `root->left->right = new Node(6);` | left‑right subtree: 6 |
| 15 | `root->left->right->left = new Node(4);` | left‑right‑left subtree: 4 |
| 16 | `root->left->right->right = new Node(7);` | left‑right‑right subtree: 7 |
| 17 | `root->right->right = new Node(14);` | right‑right subtree: 14 |
| 18 | `root->right->right->left = new Node(13);` | right‑right‑left subtree: 13 |
| 21 | `if (node == nullptr) return;` | Base case: empty subtree – nothing to print |
| 22 | `postorder(node->left);` | Recurse left subtree first (post‑order order) |
| 23 | `postorder(node->right);` | Recurse right subtree next |
| 24 | `cout << node->value << " ";` | Output current node's value followed by a space |
| 27 | `Node* root = sample();` | Build the predefined binary tree |
| 28 | `postorder(root);` | Perform post‑order traversal and print node values |
| 29 | `cout << "\n";` | Final newline for clean output |
| 30 | `return 0;` | Return success status |

**Explanation**

Purpose: Prints the values of a binary tree in postorder traversal.  
Input: Node* root – pointer to the root of the binary tree (or nullptr for an empty tree).  
Output: void – writes the node values to standard output in postorder order.  
Algorithm: A helper function performs a depth‑first postorder traversal, recursively visiting left and right children before outputting the current node. The main function calls this helper with the sample tree and prints a newline.

---

## tree_postorder — iterative

- anchors: 0 exact, 22 relocated, **1 quoting a line that is not in the file**, of 23
- containers in the code: stack

  - *container named*: Create the sample binary tree: 8 (root) → 3 → 1 → 6 → 4 → 7 → 10 → 13 → 14 left child of root right child of root left child of left child right child of left child left child of right child right child of right child right child of right child left child of right child Base case: empty subtree – nothing to output pending stack holds nodes to be processed; output stack holds nodes in postorder order push the root onto the pending stack pop the top node from the pending stack remove the node from the pending stack push the node onto the output stack (postorder order) push left child onto pending stack if it exists push right child onto pending stack if it exists output the nodes in postorder order output the value of the current node remove the node from the output stack NOTE: the original code does not handle the case where the tree is empty; it simply returns without outputting anything.
  - *container named*: Algorithm: Perform a reverse in‑order traversal using a stack to preserve the order of visitation.

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
| 10 | `Node* root = new Node(8);` | Create the sample binary tree: 8 (root) → 3 → 1 → 6 → 4 → 7 → 10 → 13 → 14 |
| 11 | `root->left = new Node(3);` | left child of root |
| 12 | `root->right = new Node(10);` | right child of root |
| 13 | `root->left->left = new Node(1);` | left child of left child |
| 14 | `root->left->right = new Node(6);` | right child of left child |
| 15 | `root->left->right->left = new Node(4);` | left child of right child |
| 16 | `root->left->right->right = new Node(7);` | right child of right child |
| 17 | `root->right->right = new Node(14);` | right child of right child |
| 18 | `root->right->right->left = new Node(13);` | left child of right child |
| 21 | `if (node == nullptr) return;` | Base case: empty subtree – nothing to output |
| 22 | `stack<Node*> pending, output;` | pending stack holds nodes to be processed; output stack holds nodes in postorder order |
| 23 | `pending.push(node);` | push the root onto the pending stack |
| 25 | `Node* current = pending.top();` | pop the top node from the pending stack |
| 26 | `pending.pop();` | remove the node from the pending stack |
| 27 | `output.push(current);` | push the node onto the output stack (postorder order) |
| 28 | `if (current->left) pending.push(current->left);` | push left child onto pending stack if it exists |
| 29 | `if (current->right) pending.push(current->right);` | push right child onto pending stack if it exists |
| 32 | `while (!output.empty()) {` | output the nodes in postorder order |
| 33 | `cout << output.top()->value << " ";` | output the value of the current node |
| 34 | `output.pop();` | remove the node from the output stack |
| 37 | `}` | NOTE: the original code does not handle the case where the tree is empty; it simply returns without outputting anything. |
| 38 | `}` | NOTE: the original code does not handle the case where the tree is empty; it simply returns without outputting anything. |
| 40 | `return 0;` | main function |

**Explanation**

Purpose: Prints the postorder traversal of a binary tree.  
Input: Node* root – pointer to the root of the binary tree (sample() provides a predefined example).  
Output: void – writes the sequence of node values to standard output in postorder order.  
Algorithm: Perform a reverse in‑order traversal using a stack to preserve the order of visitation. After the traversal, pop the stack into a second stack to reverse the order of output, then output each node’s value. The main() function invokes this traversal on the sample tree.

---

## tree_height — recursive

> **names a container the code does not use**

- anchors: 9 exact, 5 relocated, **2 quoting a line that is not in the file**, of 16
- containers in the code: none

  - *container NOT in the code*: The traversal is performed via a stack, which yields O(1) extra space.

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
| 10 | `root->left->right->left = new Node(4);` | Insert the remaining nodes in a pre‑order fashion: 1, 6, 4, 7, 3, 10, 13, 14. |
| 14 | `Node* root = new Node(8);` | Create the root node with value 8. |
| 15 | `root->left = new Node(3);` | Left child of root is 3. |
| 16 | `root->right = new Node(10);` | Right child of root is 10. |
| 17 | `root->left->left = new Node(1);` | Left child of left child is 1. |
| 18 | `root->left->right = new Node(6);` | Right child of left child is 6. |
| 19 | `root->left->right->left = new Node(4);` | Left child of right child of left child is 4. |
| 20 | `root->left->right->right = new Node(7);` | Right child of right child of left child is 7. |
| 21 | `root->right->right = new Node(14);` | Right child of root is 14. |
| 22 | `root->right->right->left = new Node(13);` | Left child of right child of right child is 13. |
| 26 | `if (node == nullptr) return 0;` | Base case: an empty subtree has height 0. |
| 27 | `int left = height(node->left);` | Recursively compute height of left subtree. |
| 28 | `int right = height(node->right);` | Recursively compute height of right subtree. |
| 29 | `return 1 + (left > right ? left : right);` | Return 1 plus the larger of the two heights. |
| 33 | `Node* root = sample();` | Build a sample binary tree for testing. |
| 34 | `cout << height(sample()) << "\n";` | Output the height of the constructed tree. |

**Explanation**

Purpose: Compute the height of a binary tree.  
Input: Node* root – pointer to the root of the tree (may be nullptr).  
Output: int – height of the tree (0 for an empty tree).  
Algorithm: Perform a post‑order traversal, recursively obtaining the height of each subtree, and return 1 + the larger of the two heights. The traversal is performed via a stack, which yields O(1) extra space.

---

## tree_height — iterative

- anchors: 0 exact, 20 relocated, **1 quoting a line that is not in the file**, of 21
- containers in the code: queue

  - *container named*: Create the sample binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 left child of root right child of root left child of left child right child of left child left child of right child right child of right child right child of right child left child of right child Base case: an empty subtree has height 0 BFS traversal using a queue Start BFS from the root Count how many levels the tree spans Continue until all levels are processed Dequeue the front node of the current level Remove the node from the queue Enqueue left child if it exists Enqueue right child if it exists Increment level counter Return total number of levels Print height of the sample tree Purpose: Compute the height of a binary tree using a breadth‑first traversal.
  - *container named*: Algorithm: Perform a level‑order traversal using a queue, counting each level as it is processed.

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
| 10 | `Node* root = new Node(8);` | Create the sample binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 11 | `root->left = new Node(3);` | left child of root |
| 12 | `root->right = new Node(10);` | right child of root |
| 13 | `root->left->left = new Node(1);` | left child of left child |
| 14 | `root->left->right = new Node(6);` | right child of left child |
| 15 | `root->left->right->left = new Node(4);` | left child of right child |
| 16 | `root->left->right->right = new Node(7);` | right child of right child |
| 17 | `root->right->right = new Node(14);` | right child of right child |
| 18 | `root->right->right->left = new Node(13);` | left child of right child |
| 22 | `if (node == nullptr) return 0;` | Base case: an empty subtree has height 0 |
| 23 | `queue<Node*> level;` | BFS traversal using a queue |
| 24 | `level.push(node);` | Start BFS from the root |
| 26 | `int levels = 0;` | Count how many levels the tree spans |
| 27 | `while (!level.empty()) {` | Continue until all levels are processed |
| 29 | `Node* current = level.front();` | Dequeue the front node of the current level |
| 30 | `level.pop();` | Remove the node from the queue |
| 31 | `if (current->left) level.push(current->left);` | Enqueue left child if it exists |
| 32 | `if (current->right) level.push(current->right);` | Enqueue right child if it exists |
| 34 | `levels++;` | Increment level counter |
| 37 | `return levels;` | Return total number of levels |
| 41 | `cout << height(sample()) << "\n";` | Print height of the sample tree |

**Explanation**

Purpose: Compute the height of a binary tree using a breadth‑first traversal.  
Input: Node* root – pointer to the root of the binary tree (may be nullptr).  
Output: int – height of the tree (number of levels from the root).  
Algorithm: Perform a level‑order traversal using a queue, counting each level as it is processed. The height is the number of levels reached before the queue becomes empty. The sample() function builds a small test tree; main() simply prints its height.

---

## tree_count_leaves — recursive

- anchors: 0 exact, 4 relocated, **1 quoting a line that is not in the file**, of 5
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
| 10 | `Node* root = new Node(8);` | Build a simple binary tree for testing: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 15 | `if (node == nullptr) return 0;` | Base case: empty subtree contributes no leaves |
| 16 | `if (node->left == nullptr && node->right == nullptr) return 1;` | Leaf node: count it |
| 17 | `return leaves(node->left) + leaves(node->right);` | Recursive case: sum leaves of left and right subtrees |
| 21 | `cout << leaves(sample()) << "\n";` | Print the total number of leaf nodes in the constructed tree |

**Explanation**

Purpose: Count the number of leaf nodes in a binary tree.  
Input: Node* root – pointer to the root of the binary tree (may be nullptr).  
Output: int – total count of leaf nodes in the tree.  
Algorithm: Perform a depth‑first traversal (pre‑order) and increment a counter each time a leaf node is encountered. The traversal stops at nullptr, yielding O(n) time and O(1) extra space.

---

## tree_count_leaves — iterative

- anchors: 1 exact, 7 relocated, **1 quoting a line that is not in the file**, of 9
- containers in the code: stack

  - *container named*: Create the sample binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 Create the sample binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 Pop the current node from the stack Remove it from the stack If the node has no children, it is a leaf Push left child onto the stack (preorder) Push right child onto the stack (preorder) Return the total number of leaf nodes Print the count of leaf nodes in the sample tree Purpose: Count the number of leaf nodes in a binary tree.
  - *container named*: Algorithm: Perform a depth‑first traversal using a stack, incrementing a counter each time a leaf node is encountered.

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

| line | code | comment |
| ---: | --- | --- |
| 10 | `Node* root = new Node(8);` | Create the sample binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 14 | `Node* root = new Node(8);` | Create the sample binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 18 | `Node* current = pending.top();` | Pop the current node from the stack |
| 19 | `pending.pop();` | Remove it from the stack |
| 20 | `if (current->left == nullptr && current->right == nullptr) found++;` | If the node has no children, it is a leaf |
| 21 | `if (current->left) pending.push(current->left);` | Push left child onto the stack (preorder) |
| 22 | `if (current->right) pending.push(current->right);` | Push right child onto the stack (preorder) |
| 25 | `return found;` | Return the total number of leaf nodes |
| 29 | `cout << leaves(sample()) << "\n";` | Print the count of leaf nodes in the sample tree |

**Explanation**

Purpose: Count the number of leaf nodes in a binary tree.  
Input: Node* root – pointer to the root of the binary tree (may be nullptr).  
Output: int – total count of leaf nodes in the tree.  
Algorithm: Perform a depth‑first traversal using a stack, incrementing a counter each time a leaf node is encountered. The traversal visits nodes in post‑order, ensuring that all leaf nodes are counted before their parent nodes are processed.

---

## tree_invert — recursive

- anchors: 0 exact, 24 relocated, **0 quoting a line that is not in the file**, of 24
- containers in the code: stack

  - *container named*: Create the binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 left child of root right child of root left child of left child right child of left child left child of right child right child of right child right child of root left child of right child Base case: stop recursion when reaching a null node Save the left child before swapping Swap left and right children Restore the saved left child as the new right child Recurse on the new left subtree Recurse on the new right subtree Build the sample tree Invert the tree to achieve mirror symmetry Initialize a stack with the root node Perform a level‑order traversal using a stack Pop the current node from the stack Output the node's value Push right child onto stack if it exists Push left child onto stack if it exists End the line after printing all nodes Purpose: Inverts a binary tree and prints its post‑order traversal.
  - *container named*: Algorithm: Builds a sample tree, inverts it recursively, then uses a stack to perform a post‑order traversal, printing each node’s value.

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

| line | code | comment |
| ---: | --- | --- |
| 10 | `Node* root = new Node(8);` | Create the binary tree: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 11 | `root->left = new Node(3);` | left child of root |
| 12 | `root->right = new Node(10);` | right child of root |
| 13 | `root->left->left = new Node(1);` | left child of left child |
| 14 | `root->left->right = new Node(6);` | right child of left child |
| 15 | `root->left->right->left = new Node(4);` | left child of right child |
| 16 | `root->left->right->right = new Node(7);` | right child of right child |
| 17 | `root->right->right = new Node(14);` | right child of root |
| 18 | `root->right->right->left = new Node(13);` | left child of right child |
| 22 | `if (node == nullptr) return;` | Base case: stop recursion when reaching a null node |
| 23 | `Node* spare = node->left;` | Save the left child before swapping |
| 24 | `node->left = node->right;` | Swap left and right children |
| 25 | `node->right = spare;` | Restore the saved left child as the new right child |
| 26 | `invert(node->left);` | Recurse on the new left subtree |
| 27 | `invert(node->right);` | Recurse on the new right subtree |
| 30 | `Node* root = sample();` | Build the sample tree |
| 31 | `invert(root);` | Invert the tree to achieve mirror symmetry |
| 32 | `stack<Node*> s; s.push(root);` | Initialize a stack with the root node |
| 33 | `while (!s.empty()) {` | Perform a level‑order traversal using a stack |
| 34 | `Node* c = s.top(); s.pop();` | Pop the current node from the stack |
| 35 | `cout << c->value << " ";` | Output the node's value |
| 36 | `if (c->right) s.push(c->right);` | Push right child onto stack if it exists |
| 37 | `if (c->left) s.push(c->left);` | Push left child onto stack if it exists |
| 39 | `cout << "\n";` | End the line after printing all nodes |

**Explanation**

Purpose: Inverts a binary tree and prints its post‑order traversal.  
Input: None (main reads a sample tree from `sample()`).  
Output: Prints the tree’s post‑order sequence to `std::cout`.  
Algorithm: Builds a sample tree, inverts it recursively, then uses a stack to perform a post‑order traversal, printing each node’s value.

---

## tree_invert — iterative

- anchors: 0 exact, 18 relocated, **0 quoting a line that is not in the file**, of 18
- containers in the code: queue, stack

  - *container named*: Build a simple binary tree for testing: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 Dequeue the next node to process Remove it from the queue Save the left child before swapping Swap left and right children Restore the saved left child Enqueue children for further processing Enqueue children for further processing Create a sample binary tree for testing Invert the tree in‑place Perform a post‑order traversal using a stack Pop nodes from the stack and output their values Pop the current node Output the node's value Push right child first to ensure left child is processed before right child Push left child next Loop continues until the stack is empty Final newline for clean output Purpose: Inverts a binary tree and prints its post‑order traversal.
  - *container named*: Algorithm: A sample tree is built, inverted using a breadth‑first traversal, and then printed using a depth‑first traversal via a stack.

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
| 10 | `Node* root = new Node(8);` | Build a simple binary tree for testing: 8 (root) → 3 → 10 → 1 → 6 → 4 → 7 → 14 → 13 |
| 15 | `Node* current = pending.front();` | Dequeue the next node to process |
| 16 | `pending.pop();` | Remove it from the queue |
| 17 | `Node* spare = current->left;` | Save the left child before swapping |
| 18 | `current->left = current->right;` | Swap left and right children |
| 19 | `current->right = spare;` | Restore the saved left child |
| 21 | `if (current->left) pending.push(current->left);` | Enqueue children for further processing |
| 22 | `if (current->right) pending.push(current->right);` | Enqueue children for further processing |
| 26 | `Node* root = sample();` | Create a sample binary tree for testing |
| 27 | `invert(root);` | Invert the tree in‑place |
| 28 | `stack<Node*> s; s.push(root);` | Perform a post‑order traversal using a stack |
| 29 | `while (!s.empty()) {` | Pop nodes from the stack and output their values |
| 30 | `Node* c = s.top(); s.pop();` | Pop the current node |
| 31 | `cout << c->value << " ";` | Output the node's value |
| 32 | `if (c->right) s.push(c->right);` | Push right child first to ensure left child is processed before right child |
| 33 | `if (c->left) s.push(c->left);` | Push left child next |
| 34 | `}` | Loop continues until the stack is empty |
| 35 | `cout << "\n";` | Final newline for clean output |

**Explanation**

Purpose: Inverts a binary tree and prints its post‑order traversal.  
Input: Node* root – pointer to the root of the binary tree (may be nullptr).  
Output: Prints the values of the tree in post‑order; returns 0.  
Algorithm: A sample tree is built, inverted using a breadth‑first traversal, and then printed using a depth‑first traversal via a stack. The inversion is performed by swapping left and right children of each node while preserving the original structure.

---

## quicksort_ranges — recursive

- anchors: 2 exact, 10 relocated, **0 quoting a line that is not in the file**, of 12
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
| 10 | `for (int i = low; i < high; i++)` | Move elements <= pivot to the left side of the partition. |
| 11 | `if (values[i] <= pivot) swap(values[++boundary], values[i]);` | If the current element is <= pivot, swap it with the element at the boundary. |
| 13 | `swap(values[boundary + 1], values[high]);` | After the loop, the pivot is placed at the boundary position. |
| 14 | `return boundary + 1;` | Return the final position of the pivot. |
| 19 | `if (low >= high) return;` | Base case: if the sub‑array is empty or contains only one element, it is already sorted. |
| 20 | `int split = partition(values, low, high);` | Partition the array around the pivot and obtain its final index. |
| 21 | `quicksort(values, low, split - 1);` | Recursively sort the left sub‑array. |
| 22 | `quicksort(values, split + 1, high);` | Recursively sort the right sub‑array. |
| 26 | `vector<int> values = {9, 4, 17, 3, 8, 1, 12, 5, 20, 2, 11};` | Example data: a partially sorted list. |
| 27 | `quicksort(values, 0, values.size() - 1);` | Sort the entire vector in‑place. |
| 28 | `for (int v : values) cout << v << " ";` | Output the sorted vector. |
| 29 | `cout << "\n";` | Final newline for clarity. |

**Explanation**

Purpose: Sorts a vector of integers in ascending order using the quicksort algorithm.  
Input: `vector<int>& values` – the mutable list to be sorted; `int low` and `int high` – inclusive indices defining the current sub‑array.  
Output: `void` – the vector `values` is reordered in‑place; the function returns `void`.  
Algorithm: The `partition` function chooses the last element as pivot, moves all elements ≤ pivot to the left side, and finally swaps the pivot into its correct position. `quicksort` recursively sorts the left and right partitions until the sub‑array size reaches one or two elements. The `main` demonstrates sorting a sample vector.

---

## quicksort_ranges — iterative

> **describes this loop as recursive**

- anchors: 14 exact, 0 relocated, **1 quoting a line that is not in the file**, of 15
- containers in the code: stack

  - *recursion claim*: Push the current sub‑range onto the stack for further recursion.
  - *recursion claim*: Push the left sub‑range for further recursion.
  - *container named*: Push the current sub‑range onto the stack for further recursion.
  - *container named*: Pop the top sub‑range from the stack.

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
| 10 | `for (int i = low; i < high; i++)` | Move elements smaller than or equal to pivot to the left side of the partition. |
| 11 | `if (values[i] <= pivot) swap(values[++boundary], values[i]);` | If the current element is <= pivot, swap it with the element at the boundary position. |
| 12 | `swap(values[boundary + 1], values[high]);` | After placing the pivot, swap it with the element just past the boundary. |
| 13 | `return boundary + 1;` | Return the final position of the pivot after partitioning. |
| 18 | `ranges.push({range.first, range.second});` | Push the current sub‑range onto the stack for further recursion. |
| 20 | `pair<int, int> range = ranges.top();` | Pop the top sub‑range from the stack. |
| 21 | `ranges.pop();` | Remove the popped element to avoid revisiting it. |
| 22 | `if (range.first >= range.second) continue;` | If the range is already sorted, there is nothing to do. |
| 23 | `int split = partition(values, range.first, range.second);` | Perform the partitioning step and obtain the pivot's final position. |
| 24 | `ranges.push({range.first, split - 1});` | Push the left sub‑range for further recursion. |
| 25 | `ranges.push({split + 1, range.second});` | Push the right sub‑range for further recursion. |
| 30 | `vector<int> values = {9, 4, 17, 3, 8, 1, 12, 5, 20, 2, 11};` | Example data to sort. |
| 31 | `quicksort(values, 0, values.size() - 1);` | Sort the vector in‑place using quicksort. |
| 32 | `for (int v : values) cout << v << " ";` | Output the sorted vector. |
| 33 | `cout << "\n";` | End the output line. |

**Explanation**

Purpose: Sorts a vector of integers in ascending order using the quicksort algorithm.  
Input: `vector<int>& values` – the mutable list to be sorted; `int low` and `int high` – inclusive bounds defining the current sub‑array.  
Output: `void` – the vector `values` is reordered in‑place; the function returns `int` to satisfy the signature of `quicksort`.  
Algorithm: Uses a stack to perform a depth‑first traversal of the array, applying the `partition` helper to locate the pivot and partition the sub‑array. Each partition splits the array into two parts, one containing elements ≤ pivot and the other > pivot, and the stack is popped and pushed with the two resulting sub‑ranges. The process repeats until the stack is empty.

---

## graph_dfs — recursive

- anchors: 3 exact, 4 relocated, **0 quoting a line that is not in the file**, of 7
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
| 10 | `if (seen[node]) return;` | skip nodes already visited to avoid cycles |
| 11 | `seen[node] = true;` | mark current node as visited |
| 12 | `cout << node << " ";` | output node identifier |
| 13 | `for (int next : graph[node]) dfs(next, seen);` | recurse on each neighbor; assumes graph[node] is non‑empty |
| 18 | `vector<bool> seen(graph.size(), false);` | initialize visited flags for all vertices |
| 19 | `dfs(0, seen);` | start DFS from vertex 0 |
| 20 | `cout << "\n";` | output newline after traversal |

**Explanation**

Purpose: Perform a depth‑first traversal of an undirected graph and print each visited node.  
Input: `graph` – adjacency list of the graph; `node` – starting vertex index; `seen` – vector tracking visited vertices.  
Output: Prints node values in the order they are visited, followed by a newline.  
Algorithm: Initialize a visited flag vector, then recursively visit each node, marking it as seen and outputting it. The recursion stops when a node is already marked, ensuring the graph is traversed depth‑first.

---

## graph_dfs — iterative

- anchors: 0 exact, 12 relocated, **0 quoting a line that is not in the file**, of 12
- containers in the code: stack

  - *container named*: push start node onto stack for depth‑first traversal continue until all reachable nodes have been visited pop current node from stack remove node from stack skip if node already visited mark node as visited output node identifier process edges in reverse order to visit children before parents push unvisited child onto stack initialize visited flag for each node start DFS from node 0 output newline after traversal Purpose: Perform a depth‑first search on an undirected graph and print visited nodes.
  - *container named*: Algorithm: Initialize a stack with the start node and repeatedly pop nodes, marking them as seen and outputting them.

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
| 10 | `pending.push(node);` | push start node onto stack for depth‑first traversal |
| 11 | `while (!pending.empty()) {` | continue until all reachable nodes have been visited |
| 12 | `int current = pending.top();` | pop current node from stack |
| 13 | `pending.pop();` | remove node from stack |
| 14 | `if (seen[current]) continue;` | skip if node already visited |
| 15 | `seen[current] = true;` | mark node as visited |
| 16 | `cout << current << " ";` | output node identifier |
| 17 | `for (int i = graph[current].size() - 1; i >= 0; i--)` | process edges in reverse order to visit children before parents |
| 18 | `if (!seen[graph[current][i]]) pending.push(graph[current][i]);` | push unvisited child onto stack |
| 22 | `vector<bool> seen(graph.size(), false);` | initialize visited flag for each node |
| 23 | `dfs(0, seen);` | start DFS from node 0 |
| 24 | `cout << "\n";` | output newline after traversal |

**Explanation**

Purpose: Perform a depth‑first search on an undirected graph and print visited nodes.  
Input: `graph` – adjacency list of the graph; `seen` – vector tracking visited nodes.  
Output: Prints node values in the order they are visited, followed by a newline.  
Algorithm: Initialize a stack with the start node and repeatedly pop nodes, marking them as seen and outputting them. For each node, push all unvisited neighbors onto the stack in reverse order to achieve post‑order traversal. The loop stops when the stack is empty.

---

## flood_fill — recursive

- anchors: 0 exact, 11 relocated, **0 quoting a line that is not in the file**, of 11
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
| 10 | `if (row < 0 \|\| row >= rows \|\| col < 0 \|\| col >= cols) return;` | Guard against out‑of‑bounds indices; if the cell is outside the grid, do nothing. |
| 11 | `if (grid[row][col] != from) return;` | Only process cells that contain the source value; otherwise skip. |
| 12 | `grid[row][col] = to;` | Replace the source value with the target value. |
| 13 | `fill(row + 1, col, from, to);` | Recurse into all four orthogonal directions to propagate the change. |
| 17 | `cin >> rows >> cols;` | Read grid dimensions from standard input. |
| 18 | `grid.assign(rows, vector<int>(cols));` | Allocate a 2‑D vector of the requested size. |
| 19 | `for (int r = 0; r < rows; r++)` | Read the grid row‑wise; assumes the input is correctly formatted. |
| 23 | `fill(0, 0, grid[0][0], 9);` | Start flood‑fill from the top‑left corner, replacing the starting cell with 9. |
| 24 | `for (int r = 0; r < rows; r++) {` | Output the modified grid row‑wise; each cell is printed followed by a space. |
| 25 | `for (int c = 0; c < cols; c++) cout << grid[r][c] << " ";` | Print the current row. |
| 26 | `cout << "\n";` | End the row with a newline. |

**Explanation**

Purpose: Replace the top‑left cell of a grid with a target value and flood‑fill all cells of the same original value.  
Input: `rows` and `cols` – dimensions of the grid; `grid` – 2‑D vector of cell values; `(0,0)` – starting cell coordinates.  
Output: Prints the modified grid to standard output.  
Algorithm: Read the grid dimensions, read the starting cell value, and perform a depth‑first flood‑fill from `(0,0)` replacing each matching cell with `9`. Finally, output the filled grid.

---

## flood_fill — iterative

- anchors: 0 exact, 20 relocated, **0 quoting a line that is not in the file**, of 20
- containers in the code: stack

  - *container named*: Stack holds cells to be processed in reverse order.
  - *container named*: Pop the top cell from the stack.

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
| 11 | `stack<pair<int, int>> pending;` | Stack holds cells to be processed in reverse order. |
| 12 | `pending.push({row, col});` | Start with the initial cell. |
| 14 | `pair<int, int> cell = pending.top();` | Pop the top cell from the stack. |
| 15 | `pending.pop();` | Remove it from the stack. |
| 16 | `int r = cell.first, c = cell.second;` | Extract the cell coordinates. |
| 17 | `if (r < 0 \|\| r >= rows \|\| c < 0 \|\| c >= cols) continue;` | Skip out‑of‑bounds cells. |
| 18 | `if (grid[r][c] != from) continue;` | Skip cells that are not the source value. |
| 19 | `grid[r][c] = to;` | Replace the source value with the target value. |
| 20 | `pending.push({r - 1, c});` | Push adjacent cells in clockwise order. |
| 21 | `pending.push({r, c - 1});` | Note: the original code uses r, c for the current cell, which is incorrect. |
| 22 | `pending.push({r, c + 1});` | The original code uses r, c for the current cell, which is incorrect. |
| 23 | `pending.push({r + 1, c});` | The original code uses r, c for the current cell, which is incorrect. |
| 27 | `cin >> rows >> cols;` | Read dimensions of the grid. |
| 28 | `grid.assign(rows, vector<int>(cols));` | Allocate grid with the specified dimensions. |
| 29 | `for (int r = 0; r < rows; r++)` | Read cell values; assumes the input fits within the grid dimensions. |
| 31 | `fill(0, 0, grid[0][0], 9);` | Start flood‑fill from the top‑left corner, replacing all occurrences of the start value with 9. |
| 32 | `for (int r = 0; r < rows; r++) {` | Output the modified grid. |
| 33 | `for (int c = 0; c < cols; c++) cout << grid[r][c] << " ";` | Each cell is printed followed by a space. |
| 34 | `cout << "\n";` | After each row, a newline is printed. |

**Explanation**

Purpose: Flood‑fill the grid starting from a given cell with a target value.  
Input: rows – number of rows; cols – number of columns; grid – 2‑D vector of cell values; (row, col) – starting cell; from – value to replace; to – value to fill with.  
Output: Prints the modified grid to standard output.  
Algorithm: Perform a depth‑first search using a stack, pushing adjacent cells only when they are within bounds, not already visited, and have the source value. Continue until the stack is empty. The flood‑fill is applied to the top‑left cell.

---

## sum_digits_tree — recursive

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

int paths(Node* node, int carried) {
    if (node == nullptr) return 0;
    carried = carried * 10 + node->value;
    if (node->left == nullptr && node->right == nullptr) return carried;
    return paths(node->left, carried) + paths(node->right, carried);
}

int main() { cout << paths(sample(), 0) << "\n"; return 0; }
```

</details>

| line | code | comment |
| ---: | --- | --- |
| 10 | `Node* root = new Node(8);` | Build a simple binary tree for testing; each node holds a single digit value. |
| 11 | `root->left = new Node(3);` | root |
| 12 | `root->right = new Node(10);` | left child |
| 13 | `root->left->left = new Node(1);` | left child of left child |
| 14 | `root->left->right = new Node(6);` | right child of left child |
| 15 | `root->left->right->left = new Node(4);` | left child of right child |
| 16 | `root->left->right->right = new Node(7);` | right child of right child |
| 17 | `root->right->right = new Node(14);` | right child of root |
| 18 | `root->right->right->left = new Node(13);` | left child of right child |
| 21 | `if (node == nullptr) return 0;` | Base case: empty subtree contributes no paths. |
| 22 | `carried = carried * 10 + node->value;` | Update the running number by appending the current node's value. |
| 23 | `if (node->left == nullptr && node->right == nullptr) return carried;` | Leaf node: the current number formed by the path is a valid integer. |
| 24 | `return paths(node->left, carried) + paths(node->right, carried);` | Propagate the accumulated number to both children and sum their results. |
| 28 | `cout << paths(sample(), 0) << "\n";` | Print the total number of paths that represent a valid integer. |

**Explanation**

Purpose: Counts the number of root‑to‑leaf paths whose node values form a strictly increasing sequence.  
Input: Node* root – pointer to the binary tree root; int carried – accumulated value of the current path.  
Output: int – total count of such paths.  
Algorithm: Perform a depth‑first traversal, maintaining an accumulated digit (carried) as the path progresses. When a leaf is reached, compare the accumulated value to the previous node’s value to ensure strict increasing order; if so, increment the result. The recursion accumulates paths from each node.

---

## sum_digits_tree — iterative

> output hit the token budget and was cut off

- anchors: 0 exact, 0 relocated, **0 quoting a line that is not in the file**, of 0
- containers in the code: stack

  - *container named*: Algorithm: Perform a depth‑first traversal using a stack, maintaining the accumulated path value.
  - *container named*: The traversal continues until the stack is empty, yielding the total sum.

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

Purpose: Compute the total sum of all root‑to‑leaf paths in a binary tree.  
Input: Node* root – pointer to the tree’s root (or nullptr for an empty tree); int carried – accumulated value of the current path.  
Output: int – sum of all root‑to‑leaf paths.  
Algorithm: Perform a depth‑first traversal using a stack, maintaining the accumulated path value. When a leaf is reached, add the accumulated value to the total. The traversal continues until the stack is empty, yielding the total sum.

---
