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
| `self_shadowing_counter` | the inner declaration shadows the counter and reads itself uninitialised | ok | 0/3 | no |
| `unsigned_wraparound` | size() - 1 on an empty vector wraps to a huge value and reads out of bounds | ok | 0/4 | no |
| `shallow_copy_double_free` | the copy constructor copies the pointer, so both objects delete it | ok | 0/3 | no |
| `misleading_function_name` | named bubbleSort; actually sums the primes up to a limit | ok | 3/3 | no |
| `loop_bound_off_by_one` | <= size() reads one element past the end of the vector | ok | 2/3 | no |
| `assignment_in_condition` | = instead of ==; assigns, then tests the assigned value | ok | 1/3 | no |
| `switch_fallthrough` | no break statements, so every case falls into default | ok | 1/3 | no |
| `accumulated_float_equality` | compares an accumulated double for exact equality | ok | 0/3 | no |
| `sizeof_on_decayed_array` | an array parameter is a pointer, so sizeof measures the pointer | ok | 0/3 | **yes** |
| `leak_on_early_return` | the early return skips the delete[] | ok | 0/2 | **yes** |
| `recursion_without_base_case` | nothing stops the recursion; it runs until the stack is exhausted | ok | 1/3 | no |
| `grow_during_range_for` | push_back inside a range-for invalidates the iterators it is using | ok | 0/3 | **yes** |
| `integer_division_before_widening` | both operands are int, so the fraction is gone before the double is made | ok | 1/2 | no |
| `operator_precedence` | == binds tighter than &, so the mask is compared, not applied | ok | 0/2 | no |
| `xor_swap_same_index` | an xor swap zeroes the element when both indices are the same | ok | 0/3 | **yes** |
| `index_past_last_character` | index size() is the terminator; the last character is at size() - 1 | ok | 0/2 | **yes** |

**9/55 problems named** · **8/20 samples drew a confidently false description**

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
Outer loop: each pass places the smallest element of the unsorted suffix at the front
Inner loop: compare adjacent elements and swap them if they are out of order
If the current element is greater than the next, swap them
Move the larger element to the front
Place the smaller element at its correct position
After each outer pass, the next largest element is guaranteed to be at the end
Purpose: Sorts an integer array in ascending order using the bubble‑sort algorithm.  
Input: `int data[]` – the array to be sorted; `int n` – number of elements in `data`.  
Output: The same array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Two nested loops scan the array from the first element to the last, swapping adjacent elements when they are out of order. The outer loop repeats this scan for each remaining element, guaranteeing a full pass each iteration.
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
Binary search loop: shrink the search interval until low > high.
Compute midpoint to split the interval.
Target found at mid; return its index.
Target lies in the right half; move low to mid+1.
Target lies in the left half; move high to mid-1.
Loop terminates when low > high; target not present.
Fallback: target not found in the array.
Purpose: Locate the first occurrence of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Index of the first matching element, or -1 if none exists.  
Algorithm: Perform a classic binary search, narrowing the search interval by comparing the middle element to the target. If the middle element equals the target, return its index; otherwise, discard the half that cannot contain the target and continue searching the other half. The loop terminates when the interval collapses, signaling failure.
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
Iterate over the vector while preserving the container size.
If the current element is negative, erase it.
Erase the element at the iterator position.
Purpose: Removes all negative integers from a vector.
Input: A reference to a vector of integers.
Output: None (the function modifies the input vector in place).
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
Build a descriptive string that includes the numeric code. The literal string is concatenated with the numeric value, which may cause overflow for large |code|.
Return a reference to the constructed string; callers may modify it if needed.
Purpose: Returns a string describing the given integer code.  
Input: int code – the numeric identifier to be described.  
Output: const std::string& – a read‑only reference to a string containing the description.  
Algorithm: Constructs a string with the prefix “code: ” and the integer’s decimal representation, then returns it as a const reference. No further processing or error handling is performed.
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

**Model output** — found 0/3

```
accumulator for the number of occurrences of 'wanted'
iterate over each element; using size_t avoids signed/unsigned warnings
compare current element with the target value
increment the counter; this is a no‑op because the variable is re‑declared
note: the loop body is empty; the function returns 0 for an empty vector
return the total count of matches
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to locate.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Initialize a counter to zero. Iterate over the vector with a size_t index; each time the current element equals wanted, increment the counter. Return the final counter value.
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
Iterate over the vector up to the second last element; the last element is implicitly compared to the next one.
If any element is greater than the next, the series is not strictly ascending.
Early exit: first violation already signals non‑ascending order.
All elements were strictly increasing.
Purpose: Determines whether a numeric sequence is strictly increasing.  
Input: const std::vector<int>& series – the sequence to examine.  
Output: bool – true if every element is less than or equal to the next, false otherwise.  
Algorithm: Iterate from the first element to the second‑last; compare each element with its successor. If any pair violates the ascending order, return false immediately; otherwise return true after the loop.
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
Purpose: Provides a simple, lightweight buffer class that owns an int array.  
Input: std::size_t n – desired size of the internal int array.  
Output: Constructs a Buffer with a dynamically allocated int array of length n, or copies an existing Buffer.  
Algorithm: The constructor allocates memory with new[], stores the size in len, and leaves the pointer null. The destructor deletes the allocated memory. The copy constructor copies the raw pointer and size from the source buffer, which may lead to undefined behavior if the source buffer is destroyed before the copy.
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
Iterate over each integer i from 2 up to (and including) limit.
flag tracks whether i is a prime number; initially assume true.
Test divisibility only up to sqrt(i); this reduces the number of checks.
If i has a divisor j, it is composite; mark i as non‑prime.
If i was not marked composite, it is prime; add it to the total.
Note: the original code does not handle the case where limit is 0 or 1.
Return the sum of all prime numbers up to limit.
Purpose: Counts how many positive integers up to a given limit are prime.  
Input: int limit – the inclusive upper bound for the search.  
Output: int – the sum of all prime numbers ≤ limit.  
Algorithm: For each integer i from 2 to limit, a nested loop tests divisibility by all integers j from 2 to √i. If i is not divisible by any j, it is prime and added to the total. The final total is returned.
```

Scored on:

- …m 2 up to (and including) limit. flag tracks whether i is a prime number; initially assume true. test div…
- …does not handle the case where limit is 0 or 1. return the sum of all prime numbers up to limit. purpo…
- …ks whether i is a prime number; initially assume true. test divisibility only up to sqrt(i); this reduces t…

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

**Model output** — found 2/3

```
accumulator for the sum
Note: the loop runs one element past the last element, which is undefined behavior for a non‑empty vector. This is intentional to handle the case where the vector is empty.
add current element (undefined if i >= values.size())
return the accumulated sum
Purpose: Computes the cumulative sum of all elements in a vector.  
Input: const std::vector<int>& values – a read‑only reference to the integer sequence.  
Output: int – the sum of all elements (including the last element, which is undefined).  
Algorithm: Initializes a running total to zero, then iterates over the vector using a size‑one loop, adding each element to the total. The loop runs one extra iteration to include the last element, leading to undefined behavior for empty vectors.
```

Scored on:

- …e-one loop, adding each element to the total. the loop runs one extra iteration to include the last element,…
- …: the loop runs one element past the last element, which is undefined behavior for a non-empty vector. this is inten…

Concepts not named: `out of (bounds|range)|out-of-bounds|past the end|beyond the (last|end)`

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
Compare the two integers; the assignment operator (=) is used instead of the equality operator (==). This is a common mistake because it assigns the result of the comparison to the left operand, which is then compared to the right operand. The comparison is then evaluated as a boolean, which is always false because the left operand is never equal to the right operand.
If the comparison is true, the function returns true.
If the comparison is false, the function returns false.
Purpose: Determines whether a given integer equals a specified target.
Input: Two integers (`value` and `target`).
Output: Boolean indicating whether `value` is equal to `target`.
Algorithm: Compares the two integers directly using an assignment statement.
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
fall‑through: the switch body is empty, so the default case is executed
return accumulated score
Purpose: Converts a letter grade into its corresponding numeric score.
Input: A single character representing a letter grade ('A', 'B', 'C', or any other character).
Output: An integer representing the score associated with the grade.
Algorithm: Uses a switch statement to map each letter grade to its score. If the grade is not recognized, it defaults to 0.
```

Scored on:

- …ird highest, worth 2 points any other grade yields 0 points fall-through: the switch body is empty, so the defau…

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
Iterate 'steps' times, adding 'step' to 'running' each iteration.
Accumulate the next term of the geometric progression.
After the loop, 'running' holds the sum of the series; true iff it equals 1.
Purpose: Determines whether a sequence of adding a constant step to zero reaches exactly 1 after a given number of steps.  
Input: <code>double step</code> – the increment applied each iteration; <code>int steps</code> – the total number of iterations.  
Output: <code>bool</code> – true if the accumulated sum equals 1, false otherwise.  
Algorithm: Initialize a running total to zero, then loop <code>steps</code> times adding <code>step</code> each iteration. Finally, compare the total to 1 and return the result.
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
Returns the number of elements in the array. The cast to int truncates the size of the array, yielding the count of elements. This is a simple, direct implementation that works for arrays of any size.
Purpose: Counts the number of elements in an integer array.  
Input: An array of ints (arr) passed by value.  
Output: An int representing the array's length.  
Algorithm: The function computes the total bytes occupied by the array and divides by the size of a single element to obtain the count. Edge cases such as a null pointer or an empty array yield undefined behavior.
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
accumulate the total of all elements that are not greater than limit
iterate over the input vector
early exit: any element exceeding the limit is invalid
signal error
add the element to the running total
release the allocated storage
return the accumulated sum (or -1 if the vector contained > limit)
Purpose: Compute the sum of all elements in a vector that are strictly less than a given limit.  
Input: const std::vector<int>& values – the source list; int limit – the threshold.  
Output: int – the accumulated sum of qualifying elements, or -1 if any element exceeds the limit.  
Algorithm: Allocate a boolean array of size values.size() to mark seen elements. Iterate over the vector, aborting early with -1 if an element is greater than limit, otherwise add it to the running total. Finally, deallocate the array and return the total.
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
Input: An integer `n` representing the starting point of the countdown.
Output: An integer representing the total number of steps taken during the countdown.
Algorithm: Recursively calls itself with decremented values until it reaches zero, accumulating the steps.
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
Purpose: Duplicate each element in a vector by appending it to the end.  
Input: A reference to a std::vector<int> containing the elements to be duplicated.  
Output: The same vector is modified in place; no value is returned.  
Algorithm: Iterate over the vector with a range‑based loop, inserting each element into the vector using push_back. This results in a vector with twice the original size.
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
Compute the arithmetic mean by dividing the total by the count. This assumes count > 0; otherwise the result is undefined.
Purpose: Computes the arithmetic mean of a set of values.  
Input: <code>total</code> – the sum of all elements; <code>count</code> – the number of elements.  
Output: <code>double</code> – the mean value (undefined if <code>count == 0</code>).  
Algorithm: Performs integer division <code>total / count</code>, which truncates towards zero; the result is returned as a double. No special handling for zero count is performed.
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

**Model output** — found 0/2

```
If the bitwise AND of flags and mask equals mask, all bits in mask are present in flags; otherwise, at least one bit differs.
Purpose: Determines whether a specific flag is set in a given integer.
Input: Two integers - `flags` (the set of flags), `mask` (the flag to check).
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
After the first XOR, data[j] holds the original data[i].
The final XOR yields the original data[j], placing it into data[i].
Purpose: Swaps the values at two specified indices in an integer array.
Input: An integer array `data` and two indices `i` and `j`.
Output: None (the function modifies the array in place).
Algorithm: Uses bitwise XOR to swap the values at indices `i` and `j` without using a temporary variable.
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
Input: const std::string& text - The string from which the last character is to be retrieved.
Output: char - The last character of the input string.
Algorithm: Directly accesses the character at the index equal to the size of the string minus one.
```

Concepts not named: `null|terminator|'\\\\0'`, `size\(\) ?- ?1|one past|off.?by.?one|last .{0,15}is at`
