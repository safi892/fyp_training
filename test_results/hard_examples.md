# Hard-example evaluation

Code where the plausible answer is the wrong one. Each sample resembles a
familiar algorithm and behaves differently. **finds** is how many of the real
problems were named; **false claim** means the model asserted the code does
something it does not, without naming the defect.

| sample | the trap | JSON | finds | false claim |
| --- | --- | :---: | :---: | :---: |
| `broken_swap` | looks exactly like bubble sort; the swap has no temporary and destroys data | ok | 0/3 | **yes** |
| `overflow_mid` | textbook binary search, but (low + high) overflows on large inputs | ok | 0/1 | no |
| `erase_while_iterating` | erase() invalidates the iterator; the loop is undefined behaviour | ok | 0/3 | **yes** |
| `dangling_reference` | returns a reference to a local that dies at the closing brace | ok | 0/3 | **yes** |
| `self_shadowing_counter` | the inner declaration shadows the counter and reads itself uninitialised | ok | 0/3 | **yes** |
| `unsigned_wraparound` | size() - 1 on an empty vector wraps to a huge value and reads out of bounds | ok | 0/4 | no |
| `shallow_copy_double_free` | the copy constructor copies the pointer, so both objects delete it | ok | 0/3 | no |
| `misleading_function_name` | named bubbleSort; actually sums the primes up to a limit | ok | 3/3 | no |

**3/23 problems named** · **4/8 samples drew a confidently false description**

---

## broken_swap

*looks exactly like bubble sort; the swap has no temporary and destroys data*

```cpp
void sortValues(int data[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (data[j] > data[j + 1]) {
                data[j] = data[j + 1];
                data[j + 1] = data[j];
            }
        }
    }
}
```

**Model output** — found 0/3, **asserted something false**

```
Outer loop: each pass places the smallest element in the unsorted region
Inner loop: compare adjacent elements and swap if they are out of order
If the current element is greater than the next, swap them
Move the larger element to the front
Place the smaller element at its correct position
After each outer pass, the next largest element is guaranteed to be at the end
Purpose: Sorts an integer array in ascending order using the bubble sort algorithm.  
Input: `int data[]` – pointer to the first element of the array; `int n` – number of elements to sort.  
Output: The array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Two nested loops traverse the array, comparing adjacent elements and swapping them if they are out of order. The outer loop repeats until no more swaps occur, guaranteeing a fully sorted array.
```

Concepts not named: `overwrit|destroy|lose|lost|clobber|duplicat`, `no temporar|without a temporar|missing temporar|third variable`, `\bbug|incorrect|broken|does not (work|sort)|fails to|is not a( real)? swap`

## overflow_mid

*textbook binary search, but (low + high) overflows on large inputs*

```cpp
int findValue(int arr[], int size, int target) {
    int low = 0, high = size - 1;
    while (low <= high) {
        int mid = (low + high) / 2;
        if (arr[mid] == target) return mid;
        if (arr[mid] < target) low = mid + 1;
        else high = mid - 1;
    }
    return -1;
}
```

**Model output** — found 0/1

```
initialise search bounds
binary‑search loop: stop when the interval is empty
compute middle index (integer division)
target found at mid
target lies in the right half
target lies in the left half
target not present in the array
Purpose: Locate the first occurrence of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Index of the first matching element, or -1 if none exists.  
Algorithm: Perform a classic binary search, narrowing the search interval based on comparison of the middle element with the target. Continue until the interval collapses, then return -1 if the loop ends.
```

Concepts not named: `overflow`

## erase_while_iterating

*erase() invalidates the iterator; the loop is undefined behaviour*

```cpp
void removeNegatives(std::vector<int>& values) {
    for (auto it = values.begin(); it != values.end(); ++it) {
        if (*it < 0)
            values.erase(it);
    }
}
```

**Model output** — found 0/3, **asserted something false**

```
Iterate over the vector while preserving the original order.
If the current element is negative, erase it.
Erase the element at the iterator position.
Purpose: Removes all negative integers from a vector.
Input: A reference to a vector of integers.
Output: None (modifies the input vector in place).
Algorithm: Iterates through the vector and erases elements that are less than zero.
```

Concepts not named: `invalidat`, `undefined behavi|\bUB\b`, `skips? (over |an? )?(element|item|value|entry|negative)|miss(es)? (an? )?(element|item|negative)|consecutive|adjacent`

## dangling_reference

*returns a reference to a local that dies at the closing brace*

```cpp
const std::string& describe(int code) {
    std::string result = "code: " + std::to_string(code);
    return result;
}
```

**Model output** — found 0/3, **asserted something false**

```
Build a descriptive string by concatenating a fixed prefix with the numeric code.
Return a reference to the constructed string; the caller may modify it.
Purpose: Returns a string describing the given integer code.
Input: An integer `code`.
Output: A `const std::string&` representing the description.
Algorithm: Concatenates the string "code: " with the integer's string representation.
```

Concepts not named: `dangl`, `local|out of scope|goes out of|lifetime|destroy`, `undefined behavi|\bUB\b`

## self_shadowing_counter

*the inner declaration shadows the counter and reads itself uninitialised*

```cpp
int countMatches(const std::vector<int>& items, int wanted) {
    int found = 0;
    for (std::size_t i = 0; i < items.size(); ++i) {
        if (items[i] == wanted) {
            int found = found + 1;
        }
    }
    return found;
}
```

**Model output** — found 0/3, **asserted something false**

```
accumulator for the number of occurrences of 'wanted'
iterate over each element; using size_t avoids signed/unsigned warnings
compare current element with the target value
increment the counter; the original code reuses the accumulator variable
note: the loop body is empty; the intent is to count matches
return the total count of 'wanted' found in the vector
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to locate.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Iterate over the vector with a size_t index, increment a counter each time the current element equals wanted, and finally return the counter. Edge cases such as an empty vector or a non‑int element are not handled.
```

Concepts not named: `shadow`, `uninitiali[sz]ed|indeterminate|itself`, `always (return|be|yield)|never (increment|updat|chang)|discarded|inner`

## unsigned_wraparound

*size() - 1 on an empty vector wraps to a huge value and reads out of bounds*

```cpp
bool isAscending(const std::vector<int>& series) {
    for (std::size_t i = 0; i < series.size() - 1; ++i) {
        if (series[i] > series[i + 1])
            return false;
    }
    return true;
}
```

**Model output** — found 0/4

```
Iterate over the vector, comparing each element with the next one.
If any element is greater than the following, the series is not ascending.
Early exit: a single violation already means the series is not ascending.
If the loop completes without finding any descending pair, the series is ascending.
Purpose: Determines whether a sequence of integers is strictly increasing.
Input: A constant reference to a std::vector<int> containing the sequence to check.
Output: A bool indicating whether the sequence is strictly increasing.
Algorithm: Iterates through the vector, comparing each element with the next one. If any element is greater than the next, returns false. If the loop completes without finding such an element, returns true.
```

Concepts not named: `empty`, `wrap|underflow|overflow|huge|enormous|SIZE_MAX|maximum value`, `out of (bounds|range)|out-of-bounds|past the end`, `unsigned`

## shallow_copy_double_free

*the copy constructor copies the pointer, so both objects delete it*

```cpp
class Buffer {
    int* data;
    std::size_t len;
public:
    Buffer(std::size_t n) : data(new int[n]), len(n) {}
    ~Buffer() { delete[] data; }
    Buffer(const Buffer& other) : data(other.data), len(other.len) {}
};
```

**Model output** — found 0/3

```
raw pointer to the allocated integer array
number of elements currently stored
public interface
constructor: allocate n elements and store the size
destructor: release the allocated memory
copy constructor: copy the raw pointer and size from another buffer
Purpose: Provides a simple, lightweight buffer class that owns an int array and manages its lifetime.  
Input: std::size_t n – the desired size of the buffer.  
Output: Constructs a Buffer object owning an int[n] and sets its length.  
Algorithm: In the constructor, allocate a new int array of size n and store the pointer and length. In the destructor, deallocate the array. The copy constructor copies the raw pointer and length from the source buffer, relying on the caller to ensure the source is valid.
```

Concepts not named: `shallow`, `double (free|delete)|twice|same (memory|pointer|buffer|array)`, `deep copy|rule of (three|3|five|5)`

## misleading_function_name

*named bubbleSort; actually sums the primes up to a limit*

```cpp
int bubbleSort(int limit) {
    int total = 0;
    for (int i = 2; i <= limit; i++) {
        bool flag = true;
        for (int j = 2; j * j <= i; j++)
            if (i % j == 0) { flag = false; break; }
        if (flag) total += i;
    }
    return total;
}
```

**Model output** — found 3/3

```
accumulator for sum of all perfect squares up to limit
iterate over each integer i from 2 up to limit
flag tracks whether i is a perfect square
test divisibility up to sqrt(i); if any divisor exists, i is composite
found a divisor → i is composite
i is a perfect square, add it to the total
otherwise i is composite and will be skipped
end outer loop
return the sum of all perfect squares ≤ limit
Purpose: Counts how many positive integers ≤ limit are prime.  
Input: int limit – the inclusive upper bound for the search.  
Output: int – the sum of all prime numbers in the range [2, limit].  
Algorithm: For each i from 2 to limit, a flag is used to detect primality; if i is not divisible by any j ≤ √i, it is added to the total. The outer loop runs O(limit) times, yielding O(limit²) time complexity.
```
