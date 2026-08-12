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
| `loop_bound_off_by_one` | <= size() reads one element past the end of the vector | ok | 0/3 | no |
| `assignment_in_condition` | = instead of ==; assigns, then tests the assigned value | ok | 1/3 | no |
| `switch_fallthrough` | no break statements, so every case falls into default | ok | 0/3 | **yes** |
| `accumulated_float_equality` | compares an accumulated double for exact equality | ok | 0/3 | no |
| `sizeof_on_decayed_array` | an array parameter is a pointer, so sizeof measures the pointer | ok | 0/3 | **yes** |
| `leak_on_early_return` | the early return skips the delete[] | ok | 0/2 | **yes** |
| `recursion_without_base_case` | nothing stops the recursion; it runs until the stack is exhausted | ok | 1/3 | no |
| `grow_during_range_for` | push_back inside a range-for invalidates the iterators it is using | ok | 0/3 | **yes** |
| `integer_division_before_widening` | both operands are int, so the fraction is gone before the double is made | ok | 1/2 | no |
| `operator_precedence` | == binds tighter than &, so the mask is compared, not applied | ok | 0/2 | **yes** |
| `xor_swap_same_index` | an xor swap zeroes the element when both indices are the same | ok | 0/3 | **yes** |
| `index_past_last_character` | index size() is the terminator; the last character is at size() - 1 | ok | 0/2 | **yes** |

**6/55 problems named** · **11/20 samples drew a confidently false description**

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

Scored on:

- …imit purpose: counts how many positive integers ≤ limit are prime.   input: int limit – the inclusive upp…
- …accumulator for sum of all perfect squares up to…
- …up to limit flag tracks whether i is a perfect square test divisibility up to sqrt(i); if any divisor exis…

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

**Model output** — found 0/3

```
Initialise accumulator to zero
Loop over all indices up to the vector size; the extra element is intentionally ignored to avoid out‑of‑bounds access.
Add current element to total
Return the accumulated sum
Purpose: Computes the cumulative sum of all elements in a vector.  
Input: const std::vector<int>& values – a read‑only reference to the integer sequence.  
Output: int – the sum of all elements (including the element at index values.size()).  
Algorithm: Initializes a running total to zero, then iterates over the vector up to one element past its size, adding each element to the total. The final total is returned.
```

Concepts not named: `out of (bounds|range)|out-of-bounds|past the end|beyond the (last|end)`, `off.?by.?one|one (too many|extra|past)`, `undefined behavi|\bUB\b|crash`

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
Compare the two integers using the assignment operator; this is a common mistake because the expression evaluates to the result of the assignment, which is 1 for true and 0 for false. The comparison then returns true if the assignment succeeded, which is not the intended behavior.
If the assignment failed, the comparison is false, so the function returns false.
Purpose: Determines whether a given integer equals a specified target.
Input: Two integers, `value` and `target`.
Output: A boolean indicating whether `value` is equal to `target`.
Algorithm: Compares `value` with `target` using an equality check. Returns true if they are equal, otherwise false.
```

Scored on:

- …the two integers using the assignment operator; this is a common mistake beca…

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

**Model output** — found 0/3, **asserted something false**

```
initialize accumulator for total points
map letter grade to numeric score
A is the highest grade, worth 4 points
B is the next highest, worth 3 points
C is the next lowest, worth 2 points
any other grade yields 0 points
fall‑through: the switch body is empty, so the default case is executed
return accumulated score
Purpose: Converts a letter grade to its corresponding numeric score.
Input: A single character representing a letter grade ('A', 'B', 'C', or any other character).
Output: An integer representing the score associated with the grade.
Algorithm: Uses a switch statement to map each letter grade to its score. If the grade is not recognized, it defaults to 0.
```

Concepts not named: `fall(s|ing)?[ -]?through|fallthrough`, `\bbreak\b`, `always (return|be|yield|give)s?.{0,12}(0|zero)`

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
Iterate 'steps' times, adding 'step' to 'running' each iteration.
Accumulate the next term of the geometric progression.
After the loop, 'running' holds the sum of the series; true iff it equals 1.
Purpose: Determines whether a sequence of adding a constant step to zero eventually reaches exactly 1.0.  
Input: <code>step</code> – the constant increment per iteration; <code>steps</code> – the number of iterations to perform.  
Output: <code>bool</code> – true if the accumulated sum equals 1.0 after <code>steps</code> iterations, false otherwise.  
Algorithm: Initialize a running total to zero, then loop <code>steps</code> times adding <code>step</code> each iteration. After the loop, compare the total to 1.0 and return the result.
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
Returns the number of elements in the array. The size of the pointer itself is multiplied by the element size, yielding the total bytes, which is then divided by the element size to obtain the count.
Purpose: Counts the number of elements in an integer array.  
Input: An array of ints (int arr[]).  
Output: An int representing the array’s length (number of elements).  
Algorithm: The function uses the standard library size_t type for the result, then divides the total bytes of the array by the size of a single element to obtain the count. No bounds checking is performed.
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

**Model output** — found 0/2, **asserted something false**

```
allocate a boolean array to track which elements have been seen
accumulator for the total of all elements
iterate over the input vector
early exit: any element exceeding the limit is invalid
signal error
accumulate the current element
release the allocated storage
return the total sum of all elements that did not exceed the limit
Purpose: Compute the sum of all elements in a vector that are strictly less than a given limit.  
Input: const std::vector<int>& values – the list of integers to sum; int limit – the threshold.  
Output: int – the total sum of qualifying elements, or -1 if any element exceeds the limit.  
Algorithm: Allocate a boolean array of size values.size() to mark seen elements. Iterate over the vector, aborting early if an element exceeds limit, otherwise add it to the running total. Finally, deallocate the array and return the accumulated sum.
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
Recursive definition: adds the current value to the result of the call with one less argument. This leads to an infinite loop because the recursion depth grows without bound.
Purpose: Counts down from a given integer to zero, returning the total number of steps taken.  
Input: int n – the starting integer (must be non‑negative).  
Output: int – the cumulative count of recursive calls (n + countDown(n‑1)).  
Algorithm: The function calls itself with n‑1, adding one to the result each time, effectively performing a full factorial‑style recursion.
```

Scored on:

- …result of the call with one less argument. this leads to an infinite loop because the recursion depth grows…

Concepts not named: `base case|termination|terminat|stop(ping)? condition`, `stack overflow|exhaust|crash`

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
Purpose: Duplicate each element in a vector.  
Input: A reference to a std::vector<int> containing the elements to be duplicated.  
Output: The same vector is modified in‑place; no value is returned.  
Algorithm: Iterate over the vector with a range‑based loop, appending each element to the end of the vector. This effectively duplicates every element.
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
Compute the arithmetic mean by dividing the total by the count. The result is an integer; if count is zero the behavior is undefined (division by zero).
Purpose: Computes the arithmetic mean of a set of values.  
Input: <code>total</code> – the sum of all elements; <code>count</code> – the number of elements.  
Output: <code>double</code> – the mean value (undefined if <code>count == 0</code>).  
Algorithm: Performs integer division <code>total / count</code>, which truncates towards zero, yielding the arithmetic mean. No special handling for zero count is provided.
```

Scored on:

- …ndefined if <code>count == 0</code>).   algorithm: performs integer division <code>total / count</code>, which trunc…

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
Returns true if the specified flag is set in the flags bitmask.
Purpose: Determines whether a specific flag is set in a given integer.
Input: Two integers - `flags` (the current state of flags), `mask` (the flag to check).
Output: Boolean indicating whether the flag is set.
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
XOR swap: the XOR of two values yields the third value when applied twice.
After the first XOR, data[j] now holds the original data[i].
The final XOR yields the original data[j], restoring the original order.
Purpose: Swaps the values at two specified indices in an integer array.
Input: `data` (int array), `i` (index of first element), `j` (index of second element).
Output: None (the function modifies the array in place).
Algorithm: Uses XOR bitwise operation to swap the values without using a temporary variable.
```

Concepts not named: `same (index|position|element)|identical indices|\bi == j\b|self`, `zero(ed|es|s)?|destroy|lose|lost|wipe`, `guard|check|special case`

## index_past_last_character

*index size() is the terminator; the last character is at size() - 1*

```cpp
char lastChar(const std::string& text) {
    return text[text.size()];
}
```

**Model output** — found 0/2, **asserted something false**

```
Access the character at the last position of the string. This assumes the string is non‑empty; otherwise undefined behavior occurs.
Purpose: Returns the last character of a string.
Input: const std::string& text - A constant reference to the string whose last character is to be retrieved.
Output: char - The last character of the input string.
Algorithm: Directly accesses the character at the index equal to the size of the string minus one.
```

Concepts not named: `null|terminator|'\\\\0'`, `size\(\) ?- ?1|one past|off.?by.?one|last .{0,15}is at`
