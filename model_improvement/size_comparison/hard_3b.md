# Hard-example evaluation

Code where the plausible answer is the wrong one. Each sample resembles a
familiar algorithm and behaves differently. **finds** is how many of the real
problems were named; **false claim** means the model asserted the code does
something it does not, without naming the defect.

| sample | the trap | JSON | finds | false claim |
| --- | --- | :---: | :---: | :---: |
| `broken_swap` | looks exactly like bubble sort; the swap has no temporary and destroys data | ok | 0/3 | **yes** |
| `overflow_mid` | textbook binary search, but (low + high) overflows on large inputs | ok | 0/1 | **yes** |
| `erase_while_iterating` | erase() invalidates the iterator; the loop is undefined behaviour | ok | 1/3 | no |
| `dangling_reference` | returns a reference to a local that dies at the closing brace | ok | 0/3 | no |
| `self_shadowing_counter` | the inner declaration shadows the counter and reads itself uninitialised | ok | 0/3 | no |
| `unsigned_wraparound` | size() - 1 on an empty vector wraps to a huge value and reads out of bounds | ok | 0/4 | no |
| `shallow_copy_double_free` | the copy constructor copies the pointer, so both objects delete it | ok | 0/3 | no |
| `misleading_function_name` | named bubbleSort; actually sums the primes up to a limit | ok | 3/3 | no |
| `loop_bound_off_by_one` | <= size() reads one element past the end of the vector | ok | 2/3 | no |
| `assignment_in_condition` | = instead of ==; assigns, then tests the assigned value | ok | 1/3 | no |
| `switch_fallthrough` | no break statements, so every case falls into default | ok | 2/3 | no |
| `accumulated_float_equality` | compares an accumulated double for exact equality | ok | 0/3 | no |
| `sizeof_on_decayed_array` | an array parameter is a pointer, so sizeof measures the pointer | ok | 0/3 | **yes** |
| `leak_on_early_return` | the early return skips the delete[] | ok | 0/2 | no |
| `recursion_without_base_case` | nothing stops the recursion; it runs until the stack is exhausted | ok | 2/3 | no |
| `grow_during_range_for` | push_back inside a range-for invalidates the iterators it is using | ok | 0/3 | **yes** |
| `integer_division_before_widening` | both operands are int, so the fraction is gone before the double is made | ok | 1/2 | no |
| `operator_precedence` | == binds tighter than &, so the mask is compared, not applied | ok | 0/2 | **yes** |
| `xor_swap_same_index` | an xor swap zeroes the element when both indices are the same | ok | 0/3 | **yes** |
| `index_past_last_character` | index size() is the terminator; the last character is at size() - 1 | ok | 1/2 | no |

**13/55 problems named** · **6/20 samples drew a confidently false description**

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
Outer loop runs n‑1 times to ensure at least one pass is made
Inner loop compares adjacent elements and swaps them if they are out of order
Swaps only when the current element is greater than the next one
Move larger value to the right position
Move smaller value to the left position
Purpose: Sorts an array of integers in ascending order using the bubble sort algorithm.
Input: An integer array `data` and its size `n`.
Output: The sorted array `data`.
Algorithm: Repeatedly steps through the list, compares adjacent elements, and swaps them if they are in the wrong order. The pass through the list is repeated until the list is sorted.
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

**Model output** — found 0/1, **asserted something false**

```
Binary search loop continues while the search interval is valid
Compute midpoint without overflow; works for small sizes
Target found at the midpoint index
If current element is smaller, discard left half
Otherwise discard right half
Target not present in the array
Purpose: To locate the index of a given target value within an integer array.
Input: An integer array `arr`, its size `size`, and the target value `target`.
Output: Returns the index of the target if found, otherwise returns -1.
Algorithm: Uses binary search to efficiently find the target. It repeatedly divides the search interval in half until the target is found or the interval is empty.
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
Iterate over the vector with an iterator; erasing while iterating invalidates iterators, so we use a range‑based loop instead.
If the current element is negative, erase it. This works because erase returns an iterator to the next element after the erased one; the loop automatically adjusts for the shift.
Purpose: Removes all negative integers from a vector in place.  
Input: A reference to a std::vector<int> containing the collection of integers.  
Output: The same vector with all negative elements removed; the function returns void.  
Algorithm: Iterate through the vector with an iterator, checking each element; if it is negative, erase it using the iterator. This approach works because erasing an element invalidates iterators only for elements that follow the erased position.
```

Scored on:

- …e over the vector with an iterator; erasing while iterating invalidates iterators, so we use a range-based lo…

Concepts not named: `undefined behavi|\bUB\b`, `skips? (over |an? )?(element|item|value|entry|negative)|miss(es)? (an? )?(element|item|negative)|consecutive|adjacent`

## dangling_reference

*returns a reference to a local that dies at the closing brace*

```cpp
const std::string& describe(int code) {
    std::string result = "code: " + std::to_string(code);
    return result;
}
```

**Model output** — found 0/3

```
Build a descriptive string by concatenating a fixed prefix with the numeric code.
Return a reference to the temporary string; callers must not modify it.
Purpose: Returns a descriptive string for a given integer code.  
Input: An `int` `code` representing the value to describe.  
Output: A `const std::string&` containing the formatted description.  
Algorithm: The function constructs a string by concatenating "code: " with the decimal representation of `code`, then returns a reference to that temporary string.
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
Iterate over each element in the vector
If the current element matches the target value, increment the counter
BUG: This line re‑declares a new local variable 'found' and assigns it 1; the original intent was to increment the global 'found'. The re‑declaration hides the outer variable, leading to incorrect counting.
Return the total count of matches
Purpose: Counts how many times a specific integer appears in a given vector.  
Input: `items` – a constant reference to a vector of ints; `wanted` – the target value to search for.  
Output: Returns an int representing the number of occurrences of `wanted`.  
Algorithm: Initialize a counter to zero, then iterate over each element of `items`, incrementing the counter whenever the current element equals `wanted`. After the loop, return the counter.
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
Compare each element with its successor; if any pair is out of order, the sequence is not strictly ascending.
If a larger element follows a smaller one, the condition fails immediately.
No out‑of‑order pair found – the sequence is strictly ascending.
Purpose: Determines whether a given integer sequence is strictly ascending.
Input: A constant reference to a vector of integers representing the sequence.
Output: Returns true if the sequence is strictly ascending, otherwise false.
Algorithm: Iterates through the sequence from the first element to the second-to-last element. For each pair of adjacent elements, checks if the current element is greater than the next one. If any such pair is found, returns false immediately. If the loop completes without finding any such pair, returns true.
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
pointer to the raw integer storage
number of elements allocated
allocate a new array of ints and store its address
store the requested size
deallocate the array when the object is destroyed
copy the raw pointer and size from the source
Purpose: Provides a simple dynamic integer buffer with copy semantics.  
Input: <code>std::size_t n</code> – size of the buffer to allocate.  
Output: Constructs a buffer of length n; destructor deallocates it.  
Algorithm: The constructor allocates an array of <code>int</code> using <code>new[]</code>, copies the size, and stores the pointer. The copy constructor copies both the pointer and size, allowing deep copies. The destructor releases the allocated memory.
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
iterate over all integers from 2 up to limit
assume prime until proven otherwise
test divisibility only up to sqrt(i) for efficiency
found a divisor → composite, stop early
add prime only if no divisors were found
Purpose: Compute the sum of all prime numbers up to a given limit using trial division.  
Input: <code>int limit</code> – the upper bound for prime candidates (inclusive).  
Output: <code>int</code> – the sum of all primes ≤ limit.  
Algorithm: For each integer i from 2 to limit, test primality by trial division up to √i; if no divisor is found, i is prime and added to the running total. The loop runs O(limit·√limit) time.
```

Scored on:

- …iterate over all integers from 2 up to limit assume prime until proven otherwise test divisibilit…
- …d prime only if no divisors were found purpose: compute the sum of all prime numbers up to a given limi…
- …from 2 up to limit assume prime until proven otherwise test divisibility only up to sqrt(i) for efficiency…

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
The loop runs one iteration too many because the condition checks i <= size() instead of i < size(). This causes undefined behavior when i == size(), as accessing values[i] is out‑of‑range.
Each iteration adds the current element to total; the loop runs one extra time, adding an extra zero (values[values.size()]) which is not intended.
Purpose: Computes the sum of all integers in a given vector.  
Input: const std::vector<int>& values – the collection to be summed.  
Output: int – the total sum of the elements; undefined if values is empty.  
Algorithm: Initializes a running total to zero, then iterates from index 0 up to (size + 1) using a simple for‑loop that adds each element to the total. The loop runs one extra iteration, which causes an out‑of‑range access when i equals size.
```

Scored on:

- …iteration adds the current element to total; the loop runs one extra time, adding an extra zero (values[valu…
- …ition checks i <= size() instead of i < size(). this causes undefined behavior when i == size(), as accessing values…

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
The intended logic is to compare the two integers; however, the assignment operator '=' is used instead of the equality operator '==' which would be correct. The assignment also returns the assigned value, causing the condition to always evaluate to true.
This branch is never reached because the assignment in the if statement always evaluates to true.
The function returns false when the condition is false, which is the intended behavior for non‑matching values.
Purpose: Determines whether a given integer matches a specified target.
Input: Two integers, `value` and `target`, representing the values to compare.
Output: A boolean value indicating whether `value` equals `target`.
Algorithm: The function checks if `value` is equal to `target`. If they are equal, it returns true; otherwise, it returns false.
```

Scored on:

- …the intended logic is to   the two integers; however, the assignment operator '=' is used instead of the equ…

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

**Model output** — found 2/3

```
Determine the numeric score for a given letter grade.
A is the highest, so set points to 4 and fall through to B
B is next, so set points to 3 and fall through to C
C is the lowest grade, so set points to 2
Any other character (e.g., 'D', 'F') is considered invalid and gets 0 points
Purpose: Convert a letter grade to its corresponding numerical score.  
Input: `char grade` – the letter grade ('A', 'B', 'C', or any other character).  
Output: `int` – the numeric score (4 for 'A', 3 for 'B', 2 for 'C', 0 otherwise).  
Algorithm: The function initializes a zero score, then uses a series of `case` statements to set the score based on the grade. The first matching case sets the score and falls through to subsequent cases, which are ignored because they have no `break`. The default case handles any unrecognized grade.
```

Scored on:

- …iven letter grade. a is the highest, so set points to 4 and fall through to b b is next, so set points to 3 and…
- …o subsequent cases, which are ignored because they have no `break`. the default case handles any unrecogn…

Concepts not named: `always (return|be|yield|give)s?.{0,12}(0|zero)`

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
Accumulate the total distance covered after 'steps' steps.
Each iteration adds one unit of 'step'.
The function returns true only if the accumulated distance equals exactly 1.0.
Purpose: Determines whether a cumulative sum of 'step' repeated 'steps' times equals exactly 1.0.
Input: double step - the value to be added each iteration; int steps - the number of iterations.
Output: bool - true if the total sum is exactly 1.0, false otherwise.
Algorithm: Iteratively adds 'step' to a running total for 'steps' iterations and checks if the result equals 1.0.
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
Compute the number of elements in the array by dividing the total size of the array by the size of one element. This works only if arr is a valid pointer to an array and not a null pointer; otherwise, the division would be undefined.
Purpose: Returns the number of elements in a statically‑allocated integer array.  
Input: `arr` – pointer to the first element of an integer array (expected to be non‑null).  
Output: `int` – count of elements in the array.  
Algorithm: The function computes the size of the array via `sizeof(arr)` and divides it by the size of a single element (`sizeof(arr[0])`). This yields the number of elements, assuming the array is not empty.
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
allocate a temporary array to track presence of each value
accumulator for the total sum
iterate over all elements
early exit if any element exceeds the limit
accumulate the current value
deallocate the temporary array
Purpose: Compute the sum of all elements in a vector that are not greater than a given limit.  
Input: const std::vector<int>& values – list of integers; int limit – maximum allowed value.  
Output: int – total sum of qualifying elements, or -1 if any element exceeds the limit.  
Algorithm: Allocate a temporary array to track seen indices (unused), iterate through values, check each against the limit, and accumulate the sum; abort early on a violation. Finally, free the temporary storage and return the sum.
```

Concepts not named: `leak`, `early return|returns? early|not reached|never (deleted|freed|reached)|skips? the`

## recursion_without_base_case

*nothing stops the recursion; it runs until the stack is exhausted*

```cpp
int countDown(int n) {
    return n + countDown(n - 1);
}
```

**Model output** — found 2/3

```
This function is intended to count down from a given number 'n' to 0. However, it contains a logical error that causes an infinite recursion.
Purpose: Computes the sum of all integers from n down to 1 using recursion.  
Input: int n – the starting positive integer (expected to be >0).  
Output: int – the total sum of numbers from n to 1.  
Algorithm: The function calls itself with n‑1, adding the result to n; this builds a recursive chain that eventually returns 1 (base case) and unwinds, producing the cumulative sum.
```

Scored on:

- …n; this builds a recursive chain that eventually returns 1 (base case) and unwinds, producing the cumulative…
- …' to 0. however, it contains a logical error that causes an infinite recursion. purpose: computes the   to 1…

Concepts not named: `stack overflow|exhaust|crash`

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
Append each element to the end of the vector, effectively duplicating it.
Purpose: To duplicate each element in a given vector.
Input: A reference to a vector of integers (`values`).
Output: None (modifies the input vector in place).
Algorithm: Iterates through each element in the input vector and appends it to the end of the same vector.
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
Compute the arithmetic mean by integer division; this truncates towards zero, which is not the intended behavior for floating‑point averages.
Purpose: Compute the arithmetic mean of a set of values given their total sum and count.  
Input: <code>int total</code> – sum of all values; <code>int count</code> – number of values.  
Output: <code>double</code> – the mean value (integer division truncates).  
Algorithm: The function performs integer division of <code>total</code> by <code>count</code>, yielding an integer result that is not the true mean for non‑integer counts.
```

Scored on:

- …compute the arithmetic mean by integer division; this truncates towards zero, which is…

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
Checks if all bits set in 'mask' are also set in 'flags'.
Purpose: Determines whether all bits set in a mask are also set in a given flags value.
Input: `flags` (int) - The integer representing the flags to check. `mask` (int) - The integer representing the mask of bits to look for.
Output: `bool` - Returns true if all bits set in the mask are also set in the flags, false otherwise.
Algorithm: Uses bitwise AND operation to compare the flags with the mask. If the result is equal to the mask, it means all bits in the mask are present in the flags.
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
XOR swap: exchanges the values at positions i and j
second XOR restores original value of data[i]
third XOR restores original value of data[j]
Purpose: Swaps the values at two indices in an integer array.
Input: `data` - pointer to the array of integers; `i` and `j` - indices of the elements to be swapped.
Output: None (void).
Algorithm: Uses bitwise XOR operations to swap the values without using a temporary variable.
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
Accesses the character at position size(), which is out‑of‑range for a string of length size(). This results in undefined behavior (e.g., segmentation fault) because std::string::size() returns size_t, and the expression is evaluated as an int.
Purpose: Returns the last character of a given string.
Input: const std::string& text - The input string from which to retrieve the last character.
Output: char - The last character of the input string.
Algorithm: Accesses the character at index size()-1 of the string.
```

Scored on:

- …he input string. algorithm: accesses the character at index size()-1 of the string.…

Concepts not named: `null|terminator|'\\\\0'`
