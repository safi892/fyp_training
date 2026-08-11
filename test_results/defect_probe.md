# Defect-awareness probe

Does explicit wording get the model to report what a line *does* rather than
what the function looks like it was meant to do? The trained wording is the
control: it is exactly what `/analyze` sends today.

A phrasing only helps if it moves the first two columns without moving the
third — correct code is the product's normal input, and inventing defects in
it would be a worse failure than missing real ones.

| phrasing | problems named | false claims (of 8) | defects invented on correct code (of 4) | anchor validity |
| --- | :---: | :---: | :---: | :---: |
| `trained_wording` | 3/23 | 4 | 0 | 60/60 |
| `describe_effect` | 3/23 | 4 | 0 | 62/62 |
| `assume_nothing` | 5/23 | 3 | 0 | 65/65 |

---

## trained_wording

> *(the trained instruction, unchanged)*

### broken_swap — found 0/3, **asserted something false**

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

### overflow_mid — found 0/1

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

### erase_while_iterating — found 0/3, **asserted something false**

```
Iterate over the vector while preserving the original order.
If the current element is negative, erase it.
Erase the element at the iterator position.
Purpose: Removes all negative integers from a vector.
Input: A reference to a vector of integers.
Output: None (modifies the input vector in place).
Algorithm: Iterates through the vector and erases elements that are less than zero.
```

### dangling_reference — found 0/3, **asserted something false**

```
Build a descriptive string by concatenating a fixed prefix with the numeric code.
Return a reference to the constructed string; the caller may modify it.
Purpose: Returns a string describing the given integer code.
Input: An integer `code`.
Output: A `const std::string&` representing the description.
Algorithm: Concatenates the string "code: " with the integer's string representation.
```

### self_shadowing_counter — found 0/3, **asserted something false**

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

### unsigned_wraparound — found 0/4

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

### shallow_copy_double_free — found 0/3

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

### misleading_function_name — found 3/3

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

### correct_swap — clean, as it should be

```
Purpose: Sorts an integer array in ascending order using the bubble sort algorithm.  
Input: `int data[]` – the array to be sorted; `int n` – number of elements in the array.  
Output: The array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Repeatedly iterates over the array, comparing each pair of adjacent elements and swapping them if they are out of order. The outer loop repeats `n‑1` times, each inner loop processes the remaining unsorted segment. This bubble‑sort runs in O(n²) time and O(1) extra space.
```

### correct_binary_search — clean, as it should be

```
initialise search bounds
binary‑search loop
compute middle index safely
target found at mid
target lies in the right half
target lies in the left half
target not present in the array
Purpose: Locate the first occurrence of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Index of the first matching element, or -1 if none exists.  
Algorithm: Perform a classic binary search, narrowing the search interval by comparing the middle element to the target. If the middle element equals the target, return its index; otherwise, discard the half that cannot contain the target and continue searching the other half. The loop terminates when the interval collapses, signaling failure.
```

### correct_erase — clean, as it should be

```
Iterate over the vector while preserving the container size.
If the current element is negative, erase it and advance the iterator.
Erase the element at the current position and re‑compute the iterator.
If the element is non‑negative, simply advance the iterator.
Purpose: Removes all negative integers from a vector in‑place.  
Input: std::vector<int>& values – the vector to be modified.  
Output: void – the vector is mutated so that only non‑negative elements remain.  
Algorithm: Iterate with a forward iterator; if the element is negative, erase it and advance the iterator; otherwise, simply advance the iterator. This yields O(n²) time and O(1) extra space.
```

### correct_counter — clean, as it should be

```
accumulator for the number of occurrences of 'wanted'
iterate over the entire collection; using size_t avoids signed/unsigned warnings
compare each element with the target value
increment the counter when a match is found
NOTE: if the vector is empty, the loop body never executes and found remains 0
return the total count of matches
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the target value.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Initialize a counter to zero. Iterate over the vector with a size_t index, incrementing the counter each time the current element equals wanted. Return the final counter value.
```

## describe_effect

> Describe what each line actually does when executed. Do not describe what the function appears intended to do.

### broken_swap — found 0/3, **asserted something false**

```
Outer loop: each pass places the smallest element of the unsorted suffix at the front
Inner loop: compare adjacent elements and swap them if they are in the wrong order
If the current element is larger than the next, swap them
Move the larger element to the front
Place the original element at its correct position
After each outer pass, the next smallest element is guaranteed to be at the front
Purpose: Sorts an integer array in ascending order using the bubble sort algorithm.  
Input: `int data[]` – pointer to the first element of the array; `int n` – number of elements to sort.  
Output: The array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Repeatedly iterates over the array, comparing each pair of adjacent elements and swapping them if they are out of order. The outer loop repeats `n‑1` times, the inner loop runs `n‑i‑1` times per outer iteration, ensuring the largest remaining element bubbles to the end each pass.
```

### overflow_mid — found 0/1, **asserted something false**

```
initialise search bounds
binary‑search loop: stop when the interval is empty
compute midpoint to avoid overflow
exact match found
target lies in the right half
target lies in the left half
target not present in the array
Purpose: Locate the first occurrence of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Index of the first matching element, or -1 if none exists.  
Algorithm: Perform a classic binary search, narrowing the search interval by comparing the middle element to the target. If the middle element equals the target, return its index; otherwise, discard the half that cannot contain the target and continue searching the other half. The loop terminates when the interval collapses, signaling failure.
```

### erase_while_iterating — found 0/3, **asserted something false**

```
Iterate over the vector while preserving the original order.
If the current element is negative, erase it.
Erase the element at the iterator position.
Purpose: Removes all negative integers from a vector.  
Input: A reference to a std::vector<int> containing the elements to be processed.  
Output: The same vector is modified in‑place; no value is returned.  
Algorithm: Iterate with a forward iterator; when an element is found to be negative, erase the iterator position to skip it. The loop naturally handles the case where the vector is empty or contains only non‑negative values.
```

### dangling_reference — found 0/3, **asserted something false**

```
Build a string that describes the integer; the format is fixed and immutable.
Return a reference to the constructed string; callers may modify it.
Purpose: Returns a string describing the given integer code.  
Input: int code – the numeric identifier to be described.  
Output: const std::string& – a read‑only reference to a string containing the description.  
Algorithm: Constructs a literal string “code: ”, appends the integer’s decimal representation via std::to_string, and returns the resulting string by value. No side effects beyond the return value.
```

### self_shadowing_counter — found 0/3

```
accumulator for the number of occurrences of wanted
iterate over the entire list; using size_t avoids signed/unsigned warnings
compare each element with the target value
increment the counter when a match is found
return the total count of matches
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to locate.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Initialize a counter to zero. Iterate over the vector with a size_t index; each time the current element equals wanted, increment the counter. After the loop, return the counter.
```

### unsigned_wraparound — found 0/4

```
Iterate over the vector, comparing each element with the next one.
If any element is greater than the next, the series is not strictly ascending.
Early exit: the series cannot be ascending.
All elements were strictly increasing, so the series is ascending.
Purpose: Determines whether a numeric sequence is strictly increasing.  
Input: const std::vector<int>& series – a sequence of integers to be examined.  
Output: bool – true if every element is less than or equal to the next, false otherwise.  
Algorithm: Iterate from the first element to the second‑last; compare each element with its successor. If any pair violates the ascending order, return false immediately; otherwise return true after the loop.
```

### shallow_copy_double_free — found 0/3

```
raw pointer to the allocated integer array
number of elements currently stored
public interface for Buffer
constructor: allocate n elements and store the size
destructor: release the allocated memory
copy constructor: copy the raw pointer and size from another Buffer
Purpose: Provides a simple, lightweight buffer class that owns an int array.  
Input: `std::size_t n` – the number of elements the buffer should allocate.  
Output: Constructs a `Buffer` object; no return value.  
Algorithm: In the constructor, allocate `n` ints on the heap and store the pointer and length. In the destructor, deallocate the memory. In the copy‑constructor, copy the raw pointer and length from the source buffer.
```

### misleading_function_name — found 3/3

```
accumulator for sum of all perfect squares up to limit
iterate over each integer i from 2 up to limit
flag tracks whether i is a perfect square
test divisibility up to sqrt(i); if any divisor exists, i is composite
found a divisor → i is composite
i is a perfect square → add it to the total
return the sum of all perfect squares ≤ limit
Purpose: Counts how many positive integers up to a given limit are prime.  
Input: int limit – the inclusive upper bound for the search.  
Output: int – the sum of all prime numbers ≤ limit.  
Algorithm: For each integer i from 2 to limit, a flag is used to detect primality; if i is not divisible by any j ≤ √i, i is added to the total. The outer loop runs O(limit) times, yielding O(limit²) time complexity.
```

### correct_swap — clean, as it should be

```
Outer loop: each pass places the smallest element in the unsorted prefix
Inner loop: compare adjacent elements and swap if they are out of order
If the current element is greater than the next, they are out of order
Store the current element temporarily
Move the next element into the current position
Place the stored element at its correct position
After each outer pass, the next smallest element is guaranteed to be at the end of the unsorted segment
Purpose: Sorts an integer array in ascending order using the bubble‑sort algorithm.  
Input: `int data[]` – the array to be sorted; `int n` – number of elements in `data`.  
Output: The same array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Repeatedly compares adjacent elements and swaps them if they are out of order, moving the largest element to the end of the unsorted segment. This process repeats `n‑1` times, guaranteeing a fully sorted array.
```

### correct_binary_search — clean, as it should be

```
Binary search loop: shrink the search interval until low > high.
Compute middle index to avoid overflow when low and high are large.
Target found at mid; return its index.
Target lies in the right half; shrink left boundary.
Target lies in the left half; shrink right boundary.
Loop exited because low > high; target not present.
Purpose: Locate the first occurrence of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Index of the first matching element, or -1 if none exists.  
Algorithm: Perform a classic binary search, narrowing the search interval by comparing the middle element to the target. If the middle element equals the target, return its index; otherwise, discard the half that cannot contain the target and continue searching the other half. The loop terminates when the interval collapses, signaling failure.
```

### correct_erase — clean, as it should be

```
Iterate over the vector while preserving the original order.
If the current element is negative, erase it and advance the iterator.
Erase the element at the current position and advance the iterator to the next element.
If the element is non‑negative, simply advance the iterator.
Purpose: Removes all negative integers from a vector while preserving the order of non‑negative elements.  
Input: A reference to a std::vector<int> containing the elements to be processed.  
Output: The same vector is modified in‑place; no value is returned.  
Algorithm: Iterate with a forward iterator; if the current element is negative, erase it and advance the iterator to avoid skipping the next element. If the element is non‑negative, simply advance the iterator. This runs in O(n) time and O(1) extra space.
```

### correct_counter — clean, as it should be

```
accumulator for the number of occurrences of 'wanted'
iterate over the entire vector; using size_t avoids signed/unsigned warnings
compare each element with the target value
increment the counter when a match is found
return the total count of matches
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to locate.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Initialize a counter to zero. Iterate over the vector with a size_t index; each time the current element equals wanted, increment the counter. Return the final counter value.
```

## assume_nothing

> This code may contain defects. Do not assume it is correct. Describe what each line actually does when executed, and where a line's effect differs from what the surrounding code appears intended to achieve, say so plainly.

### broken_swap — found 0/3, **asserted something false**

```
Outer loop runs n‑1 times, each iteration sorts the next largest element from the unsorted prefix
Inner loop compares adjacent elements and swaps them if they are out of order
If the current element is greater than the next, swap them
Swap the elements
Preserve the original order of the next element
After the inner loop finishes, the next largest element is now at the end of the unsorted prefix
Purpose: Sorts an integer array in ascending order using the bubble‑sort algorithm.  
Input: `int data[]` – the array to be sorted; `int n` – number of elements in `data`.  
Output: The same array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Repeatedly compares adjacent elements and swaps them if they are out of order, moving the largest unsorted element to the end of the array. The outer loop repeats this process `n‑1` times, guaranteeing a fully sorted array.
```

### overflow_mid — found 0/1

```
Binary search loop: shrink the search interval until low crosses high.
Compute midpoint to decide which half to discard.
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

### erase_while_iterating — found 1/3

```
Iterate over the vector while preserving the original order.
If the current element is negative, erase it.
erase() invalidates the iterator, so we must advance manually.
Purpose: Removes all negative integers from a vector.  
Input: std::vector<int>& values – a mutable reference to the vector to be modified.  
Output: void – the vector is modified in‑place; no value is returned.  
Algorithm: Iterate with a forward iterator; when an element is found to be negative, erase it from the container. The iterator is advanced after each erase to keep it correctly positioned.
```

### dangling_reference — found 0/3, **asserted something false**

```
Build a descriptive string by concatenating a fixed prefix with the integer value.
Return a reference to the constructed string; the caller may modify it.
Purpose: Returns a read‑only string describing the given integer code.  
Input: int code – the numeric identifier to be formatted.  
Output: const std::string& – a reference to a string containing the formatted description.  
Algorithm: Constructs a literal string “code: ”, appends the integer’s decimal representation via std::to_string, and returns the resulting string by value. No mutation occurs; the caller receives a copy.
```

### self_shadowing_counter — found 0/3, **asserted something false**

```
accumulator for the number of occurrences
iterate over the entire collection
compare each element with the target
increment the counter; this is a side‑effect that confuses the caller
NOTE: the loop body is empty; the intent is to count matches, but the side‑effect of re‑assigning found leads to incorrect results
NOTE: the loop body is empty; the intent is to count matches, but the side‑effect of re‑assigning found leads to incorrect results
return the total count of matches
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to locate.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Initialize a counter to zero. Iterate over the vector with a size_t index; each time the current element equals wanted, increment the counter. Return the final counter value.
```

### unsigned_wraparound — found 0/4

```
Iterate over the vector, comparing each element with the next one.
If any element is greater than the following, the series is not strictly ascending.
Early exit: the first violation already signals non‑ascending order.
If the loop finishes without finding any descending pair, the series is ascending.
Purpose: Determines whether a numeric sequence is strictly increasing.  
Input: const std::vector<int>& series – a sequence of integers to examine.  
Output: bool – true if every element is less than or equal to the next, false otherwise.  
Algorithm: Iterate from the first element to the second‑last; compare each element with its successor. If any pair violates the ascending order, return false immediately; otherwise return true after the loop.
```

### shallow_copy_double_free — found 1/3

```
raw pointer to the allocated integer array
number of elements currently stored
Buffer constructor allocates a fixed‑size array and stores its size
Note: the constructor assumes n > 0; otherwise it would leak the allocation.
Destructor releases the allocated memory
Copy constructor copies the raw pointer and size; no deep copy of the elements.
Purpose: Provides a simple, exception‑safe wrapper for a raw integer array.  
Input: `std::size_t n` – desired length of the buffer.  
Output: `Buffer` – a copy‑constructor that copies the raw pointer and length.  
Algorithm: Constructs a raw integer array of size `n` and stores its address and length. The destructor frees the array. The copy constructor simply copies the raw pointer and length, relying on the destructor to clean up the original buffer.
```

### misleading_function_name — found 3/3

```
Iterate over each integer i from 2 up to (and including) limit.
flag tracks whether i is a prime number; initially assume true.
Test divisibility only up to sqrt(i); this reduces the number of checks.
If i has a divisor other than 1 and itself, it is composite.
If i was not divisible by any smaller number, it is prime.
Note: the original code does not handle the case where i is 1 or 2.
Return the sum of all prime numbers up to limit.
Purpose: Counts how many integers up to a given limit are prime.  
Input: int limit – the inclusive upper bound for the search.  
Output: int – the sum of all prime numbers ≤ limit.  
Algorithm: For each integer i from 2 to limit, a flag is used to detect primality; if i is not divisible by any j ≤ √i, i is added to the total. The outer loop runs O(limit) times, yielding O(limit²) time complexity.
```

### correct_swap — clean, as it should be

```
Outer loop runs n‑1 times, each iteration sorts the next largest element from the unsorted prefix.
Inner loop compares adjacent elements and swaps them if they are out of order.
If the current element is greater than the next, a swap is needed.
Store the current element temporarily.
Move the next element into the current position.
Place the stored element at its correct position.
After each outer iteration, the next largest element is guaranteed to be at the end of the processed segment.
Purpose: Sorts an integer array in ascending order using the bubble‑sort algorithm.  
Input: `int data[]` – the array to be sorted; `int n` – number of elements in `data`.  
Output: The same array `data` is reordered in‑place; the function returns `void`.  
Algorithm: Repeatedly compares adjacent elements and swaps them if they are out of order, moving the largest unsorted element to the end of the array. The outer loop repeats this process `n‑1` times, guaranteeing a fully sorted array.
```

### correct_binary_search — clean, as it should be

```
Binary search loop: shrink the search interval until low > high
Compute middle index to avoid overflow
Target found at mid
Target lies in the right half
Target lies in the left half
Target not present in the array
Purpose: Locate the first occurrence of a target value in a sorted integer array.  
Input: `arr` – pointer to the first element of the sorted array; `size` – number of elements; `target` – value to search for.  
Output: Index of the first matching element, or -1 if none exists.  
Algorithm: Perform a classic binary search, narrowing the search interval by comparing the middle element to the target. If the middle element equals the target, return its index; otherwise, discard the half that cannot contain the target and continue searching the other half. The loop terminates when the interval collapses, signaling failure.
```

### correct_erase — clean, as it should be

```
Iterate over the vector while preserving the original order.
If the current element is negative, erase it and advance the iterator.
Erase the element at the current position and advance the iterator to the next element.
If the element is non‑negative, simply advance the iterator.
Purpose: Removes all negative integers from a vector while preserving the order of non‑negative elements.  
Input: A reference to a std::vector<int> containing the elements to be processed.  
Output: The same vector is modified in‑place; no value is returned.  
Algorithm: Iterate with a forward iterator; if the current element is negative, erase it and advance the iterator to avoid skipping the next element. If the element is non‑negative, simply advance the iterator. This yields a vector with only non‑negative values.
```

### correct_counter — clean, as it should be

```
accumulator for the count of occurrences
iterate over the entire vector; using size_t avoids signed/unsigned warnings
compare each element with the target value
increment the counter when a match is found
NOTE: if the vector is empty, the loop body never executes, so found remains 0
return the total count of matches
Purpose: Counts how many times a specific integer appears in a vector.  
Input: const std::vector<int>& items – the collection to search; int wanted – the value to locate.  
Output: int – the number of occurrences of wanted in items.  
Algorithm: Initialize a counter to zero. Iterate over the vector with a size_t index; each time the current element equals wanted, increment the counter. Return the final counter value.
```
