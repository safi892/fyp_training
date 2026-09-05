# Hard-example evaluation

Code where the plausible answer is the wrong one. Each sample resembles a
familiar algorithm and behaves differently. **finds** is how many of the real
problems were named; **false claim** means the model asserted the code does
something it does not, without naming the defect.

| sample | the trap | JSON | finds | false claim |
| --- | --- | :---: | :---: | :---: |
| `broken_swap` | looks exactly like bubble sort; the swap has no temporary and destroys data | ok | 0/3 | **yes** |
| `overflow_mid` | textbook binary search, but (low + high) overflows on large inputs | ok | 0/1 | no |
| `erase_while_iterating` | erase() invalidates the iterator; the loop is undefined behaviour | ok | 1/3 | no |
| `dangling_reference` | returns a reference to a local that dies at the closing brace | ok | 0/3 | **yes** |
| `self_shadowing_counter` | the inner declaration shadows the counter and reads itself uninitialised | ok | 0/3 | **yes** |
| `unsigned_wraparound` | size() - 1 on an empty vector wraps to a huge value and reads out of bounds | ok | 0/4 | no |
| `shallow_copy_double_free` | the copy constructor copies the pointer, so both objects delete it | ok | 1/3 | no |
| `misleading_function_name` | named bubbleSort; actually sums the primes up to a limit | ok | 3/3 | no |
| `loop_bound_off_by_one` | <= size() reads one element past the end of the vector | ok | 1/3 | no |
| `assignment_in_condition` | = instead of ==; assigns, then tests the assigned value | ok | 1/3 | no |
| `switch_fallthrough` | no break statements, so every case falls into default | ok | 1/3 | no |
| `accumulated_float_equality` | compares an accumulated double for exact equality | ok | 0/3 | no |
| `sizeof_on_decayed_array` | an array parameter is a pointer, so sizeof measures the pointer | ok | 0/3 | **yes** |
| `leak_on_early_return` | the early return skips the delete[] | ok | 0/2 | no |
| `recursion_without_base_case` | nothing stops the recursion; it runs until the stack is exhausted | ok | 1/3 | no |
| `grow_during_range_for` | push_back inside a range-for invalidates the iterators it is using | ok | 0/3 | **yes** |
| `integer_division_before_widening` | both operands are int, so the fraction is gone before the double is made | ok | 1/2 | no |
| `operator_precedence` | == binds tighter than &, so the mask is compared, not applied | ok | 0/2 | **yes** |
| `xor_swap_same_index` | an xor swap zeroes the element when both indices are the same | ok | 0/3 | **yes** |
| `index_past_last_character` | index size() is the terminator; the last character is at size() - 1 | ok | 1/2 | no |

**11/55 problems named** · **7/20 samples drew a confidently false description**

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
Outer loop: each pass moves the largest unsorted element to its correct position
Inner loop: compare adjacent elements and swap if they are in the wrong order
If the current element is greater than the next, they are out of order
Swap the elements to bring the larger one to the front
Place the smaller element at its correct position
After each outer pass, the largest element is at the end of the array
Purpose: Sorts an array of integers in ascending order using bubble sort.  
Input: `int data[]` – the array to be sorted; `int n` – number of elements in `data`.  
Output: The array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Repeatedly iterates over the array, comparing each pair of adjacent elements and swapping them if they are out of order. The outer loop runs `n‑1` times, the inner loop runs `n‑i‑1` times, ensuring each element is moved to its correct position in the remaining unsorted segment.
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
initialise search bounds to whole array
binary search loop
compute midpoint
exact match found
target lies in right half
target lies in left half
target not present in array
Purpose: Locate the first occurrence of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Index of the first matching element, or -1 if none exists.  
Algorithm: Perform a classic binary search, narrowing the search interval based on comparison of the middle element with the target. Continue until the interval is empty, then return -1.
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

**Model output** — found 1/3

```
Iterate over the vector; each iteration may invalidate the iterator.
If the current element is negative, erase it.
Note: erase() returns an iterator to the element after the erased one, which is not used here.
Purpose: Removes all negative integers from a vector.  
Input: A reference to a std::vector<int> containing the elements to be processed.  
Output: The same vector is modified in‑place; no value is returned.  
Algorithm: Iterate over the vector with an iterator; when an element is negative, erase the iterator position. The loop naturally handles the case where the vector is empty, leaving it unchanged.
```

Scored on:

- …iterate over the vector; each iteration may invalidate the iterator. if the current element i…

Concepts not named: `undefined behavi|\bUB\b`, `skips? (over |an? )?(element|item|value|entry|negative)|miss(es)? (an? )?(element|item|negative)|consecutive|adjacent`

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
Input: An `int` value `code` to be described.  
Output: A `const std::string&` containing the formatted description.  
Algorithm: Constructs a string by concatenating a fixed prefix with the integer’s decimal representation, then returns a reference to that string. No side effects or error handling are performed.
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
accumulator for occurrences of wanted
iterate over each element; size_t avoids signed/unsigned warnings
compare current element with wanted value
increment accumulator; this is a no‑op because the variable is re‑declared
note: the loop body is empty; the intent is to count matches
note: the loop body is empty; the intent is to count matches
return the total count of matches
Purpose: Counts how many times a specific integer appears in a vector.  
Input: `items` – a vector of integers; `wanted` – the target integer to count.  
Output: An `int` representing the number of occurrences of `wanted` in `items`.  
Algorithm: Iterate over the vector with a size‑based index, increment a counter each time the current element equals `wanted`. The final counter value is returned.
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
If any element is greater than the following one, the sequence is not ascending.
Early exit: no need to check further.
All elements were strictly increasing.
Purpose: Determines whether a numeric sequence is strictly increasing.  
Input: const std::vector<int>& series – the sequence to examine.  
Output: bool – true if every element is less than or equal to the next, false otherwise.  
Algorithm: Iterate from the first element to the second‑last, comparing each element with its successor. If any pair violates the ascending order, return false immediately; otherwise return true after the loop.
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

**Model output** — found 1/3

```
pointer to the allocated integer array
number of elements in the buffer
Constructor: allocate n integers and store the size. Note: no bounds checking is performed; caller must ensure n is non‑negative.
Copy constructor: copy the raw pointer and size from the source buffer. This copies the pointer, not the underlying data, leading to undefined behavior if the source buffer is modified after copying.
Purpose: Provides a simple, exception‑safe wrapper for a dynamically allocated integer array.  
Input: A std::size_t specifying the desired length of the buffer.  
Output: Constructs a Buffer object owning a heap‑allocated int array of that size.  
Algorithm: In the constructor, allocate a new int array of length n and store the pointer and length. In the destructor, safely deallocate the array. In the copy constructor, copy the raw pointer and length from the source object, which is a shallow copy.
```

Scored on:

- …e raw pointer and length from the source object, which is a shallow copy.…

Concepts not named: `double (free|delete)|twice|same (memory|pointer|buffer|array)`, `deep copy|rule of (three|3|five|5)`

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
accumulator for the sum of perfect squares
iterate over each integer i from 2 up to (and including) limit
flag tracks whether i is a perfect square
test divisibility up to sqrt(i); if any divisor exists, i is not a perfect square
if i is a perfect square, add it to the total
note: the original code had a typo: flag = false; break; which would always terminate the inner loop early
return the sum of all perfect squares ≤ limit
Purpose: Counts how many integers up to a given limit are prime.  
Input: int limit – the inclusive upper bound for the search.  
Output: int – the sum of all prime numbers ≤ limit.  
Algorithm: For each i from 2 to limit, a nested loop tests divisibility by all j from 2 to √i; if i is prime, it is added to the total. The outer loop runs O(limit) time, and the inner loop runs O(√i) time per i.
```

Scored on:

- …t purpose: counts how many integers up to a given limit are prime.   input: int limit - the inclusive upp…
- …accumulator for the sum of perfect squares iterat…
- …uding) limit flag tracks whether i is a perfect square test divisibility up to sqrt(i); if any divisor exis…

## loop_bound_off_by_one

*<= size() reads one element past the end of the vector*

```cpp
int sumAll(const std::vector<int>& values) {
    int total = 0;
    for (std::size_t i = 0; i <= values.size(); ++i)
        total += values[i];
    return total;
}
```

**Model output** — found 1/3

```
Initialize accumulator to zero
Iterate over every index up to the vector's size, including the out‑of‑range element at size() + 1
Add the element at position i to the total; this will include the out‑of‑range element, which may be undefined behavior for non‑empty vectors
Return the accumulated sum
Purpose: Computes the sum of all elements in a vector, including out‑of‑range indices.  
Input: const std::vector<int>& values – the collection of integers to sum.  
Output: int – the total sum of the vector elements.  
Algorithm: Initializes a running total to zero, then iterates over the vector indices from 0 up to the vector size (inclusive). For each index it adds the element at that position to the total, which results in an incorrect sum because the loop never stops and the final total is the sum of the vector plus the out‑of‑range element.
```

Scored on:

- …l; this will include the out-of-range element, which may be undefined behavior for non-empty vectors return the accu…

Concepts not named: `out of (bounds|range)|out-of-bounds|past the end|beyond the (last|end)`, `off.?by.?one|one (too many|extra|past)`

## assignment_in_condition

*= instead of ==; assigns, then tests the assigned value*

```cpp
bool isTarget(int value, int target) {
    if (value = target)
        return true;
    return false;
}
```

**Model output** — found 1/3

```
Compare the two integers; the assignment operator (=) is used instead of the equality operator (==). This results in a side‑effect of assigning the target to value, which is then compared to the original value. The assignment operator returns the value of the right‑hand side, so the expression evaluates to true (1) when the target equals the value, otherwise false (0).
This line is unreachable because the assignment already returns a boolean.
This line is unreachable because the assignment already returns a boolean.
Purpose: Determines whether a given integer equals a target value.  
Input: `int value` – the integer to compare; `int target` – the reference value.  
Output: `bool` – `true` if `value` equals `target`, otherwise `false`.  
Algorithm: The function performs a simple equality check using the assignment operator; if the condition is true, it returns `true`; otherwise it returns `false`. This results in a false positive for the equality case, which is the intended behavior.
```

Scored on:

- …the two integers; the assignment operator (=) is used instead of the equ…

Concepts not named: `always (true|returns true|be true)|never (returns? )?false`, `modif|overwrit|changes the`

## switch_fallthrough

*no break statements, so every case falls into default*

```cpp
int scoreOf(char grade) {
    int points = 0;
    switch (grade) {
        case 'A': points = 4;
        case 'B': points = 3;
        case 'C': points = 2;
        default: points = 0;
    }
    return points;
}
```

**Model output** — found 1/3

```
initialize accumulator for total points
map letter grade to numeric score
A is the highest grade, worth 4 points
B is the next highest, worth 3 points
C is the third highest, worth 2 points
any other grade yields 0 points
fall‑through: the switch body is unreachable for valid grades
return accumulated score
Purpose: Converts a letter grade to its corresponding numeric score.  
Input: A single character `grade` representing the letter grade (e.g., 'A', 'B').  
Output: An `int` score where 'A' maps to 4, 'B' to 3, 'C' to 2, and any other character defaults to 0.  
Algorithm: Initializes a result variable to 0, then uses a switch statement to assign the appropriate score based on the grade. The default case handles unrecognized grades gracefully.
```

Scored on:

- …ird highest, worth 2 points any other grade yields 0 points fall-through: the switch body is unreachable for val…

Concepts not named: `\bbreak\b`, `always (return|be|yield|give)s?.{0,12}(0|zero)`

## accumulated_float_equality

*compares an accumulated double for exact equality*

```cpp
bool reachesOne(double step, int steps) {
    double running = 0.0;
    for (int i = 0; i < steps; ++i)
        running += step;
    return running == 1.0;
}
```

**Model output** — found 0/3

```
Iterate 'steps' times, accumulating 'step' each iteration.
Add the current step to the running total.
Note: If 'step' is negative, the loop will underflow, leading to undefined behavior.
After the loop, compare the accumulated sum to 1.0.
Purpose: Determines whether a sequence of adding step to a running total reaches exactly 1.0 after steps iterations.  
Input: double step – the amount added each iteration; int steps – number of iterations.  
Output: bool – true if the total equals 1.0 after steps iterations, false otherwise.  
Algorithm: Initialise a running total to 0.0, then loop steps times, adding step to it each iteration. Finally, compare the total to 1.0 and return the result.
```

Concepts not named: `floating.?point|rounding|precision|epsilon`, `never (be )?(exactly )?equal|will not be exact|rarely|almost never|cannot be represented`, `toleran|approximat`

## sizeof_on_decayed_array

*an array parameter is a pointer, so sizeof measures the pointer*

```cpp
int countItems(int arr[]) {
    return sizeof(arr) / sizeof(arr[0]);
}
```

**Model output** — found 0/3, **asserted something false**

```
Returns the number of elements in the array. The size of the array is divided by the size of a single element, which yields the count. This works for arrays of any size, including empty arrays, but may produce undefined behavior for non‑array pointers.
Purpose: Returns the number of elements in an integer array.  
Input: An array of ints (passed as a pointer to the first element).  
Output: An int representing the array's length (number of elements).  
Algorithm: Computes the total size of the array in bytes and divides by the size of a single int, yielding the count.  
Defects: Assumes the caller passes a valid, non‑null array; no bounds checking is performed. The function assumes the array is contiguous in memory, which may not be true for non‑standard storage layouts.
```

Concepts not named: `decay`, `always (return|be|give)s?.{0,10}(2|the same)|not the (number|count|length)`, `(size|length) is (lost|not known|unavailable)|cannot (determine|know)`

## leak_on_early_return

*the early return skips the delete[]*

```cpp
int totalUnder(const std::vector<int>& values, int limit) {
    int* seen = new int[values.size()]();
    int sum = 0;
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (values[i] > limit)
            return -1;
        sum += values[i];
    }
    delete[] seen;
    return sum;
}
```

**Model output** — found 0/2

```
Allocate a temporary array to mark which elements have been seen; each element is initialized to 0.
Accumulate the sum of all values that are not greater than the limit.
Iterate over the input vector; the loop variable is unsigned to avoid signed/unsigned warnings.
If any value exceeds the limit, the total cannot be computed; signal failure.
Return -1 to indicate invalid input.
Add the value to the running sum.
Deallocate the temporary array; this is the only memory allocated in this function.
Return the total sum of all values that did not exceed the limit.
Purpose: Compute the sum of all elements in a vector that are strictly less than a given limit.  
Input: `values` – a vector of integers; `limit` – an integer threshold.  
Output: Returns the accumulated sum if all elements are ≤ limit, otherwise returns -1.  
Algorithm: Allocate a temporary array of size `values.size()` and initialize it to zero. Iterate over `values`, skipping any element > `limit` and adding the rest to the accumulator. After the loop, deallocate the temporary array and return the accumulated sum.
```

Concepts not named: `leak`, `early return|returns? early|not reached|never (deleted|freed|reached)|skips? the`

## recursion_without_base_case

*nothing stops the recursion; it runs until the stack is exhausted*

```cpp
int countDown(int n) {
    return n + countDown(n - 1);
}
```

**Model output** — found 1/3

```
Purpose: Counts down from n to 0, accumulating the result.  
Input: int n – the starting integer (must be non‑negative).  
Output: int – the sum of all integers from n down to 0.  
Algorithm: The function calls itself recursively, decrementing n each time, adding the current n to the result of the recursive call. The recursion terminates when n reaches 0, yielding 0 + countDown(1) + ... + countDown(n‑1).
Purpose: Counts down from n to 0, accumulating the total steps taken.  
Input: int n – the starting integer (must be non‑negative).  
Output: int – the sum of all integers from n down to 0.  
Algorithm: The function recursively calls itself with n‑1, adding the current n to the result of the recursive call. The recursion terminates when n reaches 0, yielding 0 + 0 = 0.
```

Scored on:

- …urrent n to the result of the recursive call. the recursion terminates when n reaches 0, yielding 0 + countd…

Concepts not named: `infinite|never (end|stop)|forever|unbounded`, `stack overflow|exhaust|crash`

## grow_during_range_for

*push_back inside a range-for invalidates the iterators it is using*

```cpp
void duplicate(std::vector<int>& values) {
    for (int value : values)
        values.push_back(value);
}
```

**Model output** — found 0/3, **asserted something false**

```
Iterate over each element in the input vector.
Append the current element to the end of the vector, effectively duplicating it.
Purpose: Duplicate each element in a vector by appending it to the end.  
Input: A reference to a std::vector<int> containing the source values.  
Output: The same vector is modified in place; no value is returned.  
Algorithm: Iterate over the vector with a range‑based loop, inserting each element into the vector using push_back. This results in each element appearing twice, preserving the original order.
```

Concepts not named: `invalidat`, `undefined behavi|\bUB\b`, `infinite|grow(s|ing)? (forever|without)|reallocat|never (end|terminat)`

## integer_division_before_widening

*both operands are int, so the fraction is gone before the double is made*

```cpp
double meanOf(int total, int count) {
    return total / count;
}
```

**Model output** — found 1/2

```
This implementation assumes that both total and count are non‑negative integers; division by zero would be undefined. The result is an integer, which may be truncated to zero if total is zero.
Purpose: Computes the arithmetic mean of a total and a count.  
Input: `total` – the sum of the values; `count` – the number of elements.  
Output: Returns a `double` representing the mean (total / count).  
Algorithm: Performs integer division, which truncates towards zero, yielding an integer result. No floating‑point arithmetic is performed, so the division is exact for integral inputs.
```

Scored on:

- …would be undefined. the result is an integer, which may be truncated to zero if total is zero. purpose: co…

Concepts not named: `cast|static_cast|convert|widen`

## operator_precedence

*== binds tighter than &, so the mask is compared, not applied*

```cpp
bool hasFlag(int flags, int mask) {
    return flags & mask == mask;
}
```

**Model output** — found 0/2, **asserted something false**

```
Returns true if the flag represented by 'mask' is set in 'flags'. The expression evaluates to true only when the bitwise AND of 'flags' and 'mask' equals 'mask', i.e., when 'mask' is a subset of 'flags'.
Purpose: Determines whether a specific flag is set in a given integer mask.
Input: `flags` (int) - The integer containing the flags.
       `mask` (int) - The integer mask to check against.
Output: `bool` - True if the flag is set, False otherwise.
Algorithm: Performs a bitwise AND operation between `flags` and `mask`. If the result equals `mask`, the flag is set.
```

Concepts not named: `precedence|parenthes|binds? (more )?tight|evaluat.{0,25}(first|before)`, `(lowest|first|least significant) bit|always|\b& 1\b`

## xor_swap_same_index

*an xor swap zeroes the element when both indices are the same*

```cpp
void swapAt(int data[], int i, int j) {
    data[i] ^= data[j];
    data[j] ^= data[i];
    data[i] ^= data[j];
}
```

**Model output** — found 0/3, **asserted something false**

```
XOR swap: data[i] = data[i] ^ data[j]; data[j] = data[i] ^ data[j]; data[i] = data[i] ^ data[j];
After the first XOR, data[j] becomes the original value of data[i].
The final XOR restores the original value of data[j] to data[i].
Purpose: Swaps the values at two specified indices in an integer array.  
Input: `data` – pointer to the first element of the array; `i` and `j` – indices to be swapped.  
Output: The function returns `void`; it modifies the array in place.  
Algorithm: Uses the XOR‑swap trick to exchange the values at `i` and `j`. The first XOR operation exchanges `data[i]` and `data[j]`, the second XOR exchanges `data[j]` and the new `data[i]`, and the third XOR restores `data[i]` to its original value. This yields O(1) time and O(1) extra space.
```

Concepts not named: `same (index|position|element)|identical indices|\bi == j\b|self`, `zero(ed|es|s)?|destroy|lose|lost|wipe`, `guard|check|special case`

## index_past_last_character

*index size() is the terminator; the last character is at size() - 1*

```cpp
char lastChar(const std::string& text) {
    return text[text.size()];
}
```

**Model output** — found 1/2

```
Returns the character at the position equal to the string's length. This is undefined behavior because the index is out of bounds for any non‑empty string.
Purpose: Returns the last character of a string.  
Input: const std::string& text – the string whose last character is required.  
Output: char – the character at index text.size()‑1, or undefined if the string is empty.  
Algorithm: The function computes the string’s size and accesses the element at that index, which is undefined for an empty string because the size is zero. No bounds checking is performed.
```

Scored on:

- …r is required.   output: char - the character at index text.size()-1, or undefined if the string is empty.…

Concepts not named: `null|terminator|'\\\\0'`
