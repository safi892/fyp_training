# Identifier robustness — model output review

Every section below is the **same algorithm** with the variables renamed. If the model understands the code, the comments should say the same thing in each one.

## Summary

| variant | what changed | JSON | anchors kept | concepts | agreement |
| --- | --- | ---: | ---: | ---: | ---: |
| `original` | as written, meaningful names | 100% | 30/30 | 94% | 1.00 |
| `terse` | single letters: a, b, x, n | 88% | 19/19 | 81% (-12%) | 0.56 |
| `noise` | visually confusing: lllIII, O0OoO0 | 88% | 19/19 | 94% (+0%) | 0.53 |
| `mixed` | half descriptive, half noise | 88% | 19/19 | 88% (-6%) | 0.42 |
| `misleading` | names that suggest the wrong operation | 100% | 29/29 | 94% (+0%) | 0.48 |

**concepts** is the headline: the share of ideas the model named, scored against words that never appear as identifiers, so a point cannot be earned by echoing a variable name. **agreement** is word overlap with the same sample's `original` output.

## digit_count

*difficulty: easy — a correct answer should mention: add, digit, divide, loop*

### `original` — as written, meaningful names

**Input**

```cpp
  1  int howMany(int first, int second)
  2  {
  3    int total = first + second;
  4    int tally = 0;
  5    while (total != 0)
  6    {
  7      total /= 10;
  8      tally++;
  9    }
 10    return tally;
 11  }
```

**Line-by-line comments**

| line | code | comment |
| ---: | --- | --- |
| 3 | `int total = first + second;` | Compute the sum of the two integers. |
| 4 | `int tally = 0;` | Initialize counter for digit count. |
| 5 | `while (total != 0)` | Loop until all digits have been processed. |
| 7 | `total /= 10;` | Remove the least‑significant digit. |
| 8 | `tally++;` | Increment the digit count. |
| 10 | `return tally;` | Return the total number of decimal digits. |

**Explanation**

> Purpose: Counts the number of decimal digits in the sum of two integers.  
> Input: Two ints `first` and `second`, representing the numbers whose digit count is to be determined.  
> Output: An int indicating how many decimal digits appear in `first + second`.  
> Algorithm: Add the inputs, then repeatedly divide by 10 until the result becomes zero, incrementing a counter each time; the final counter value equals the digit count.

*4/4 concepts · anchors 6/6 kept (3 exact) · agreement 1.00*

### `terse` — single letters: a, b, x, n

**Input**

```cpp
  1  int a(int b, int c)
  2  {
  3    int d = b + c;
  4    int e = 0;
  5    while (d != 0)
  6    {
  7      d /= 10;
  8      e++;
  9    }
 10    return e;
 11  }
```

**Line-by-line comments**

| line | code | comment |
| ---: | --- | --- |
| 3 | `int d = b + c;` | Compute sum of the two integers; this may overflow if b+c exceeds INT_MAX. |
| 4 | `int e = 0;` | Count digits in the resulting sum. |
| 5 | `while (d != 0)` | Loop until all decimal places have been processed. |
| 7 | `d /= 10;` | Remove the least‑significant digit. |
| 8 | `e++;` | Increment count of remaining digits. |
| 10 | `return e;` | Return total digit count. |

**Explanation**

> Purpose: Counts the number of decimal digits in an integer.
> Input: Two integers `b` and `c`, representing the sum to be analyzed.
> Output: An integer representing the count of digits in the sum.
> Algorithm: Adds `b` and `c`, then iteratively divides by 10 until it becomes zero, incrementing a counter each time.

*4/4 concepts · anchors 6/6 kept (3 exact) · agreement 0.50*

### `noise` — visually confusing: lllIII, O0OoO0

**Input**

```cpp
  1  int lllIII(int IllIlI, int l1lIl1)
  2  {
  3    int O0OoO0 = IllIlI + l1lIl1;
  4    int oO0Oo0 = 0;
  5    while (O0OoO0 != 0)
  6    {
  7      O0OoO0 /= 10;
  8      oO0Oo0++;
  9    }
 10    return oO0Oo0;
 11  }
```

**Line-by-line comments**

| line | code | comment |
| ---: | --- | --- |
| 3 | `int O0OoO0 = IllIlI + l1lIl1;` | Compute the sum of the two integers. |
| 4 | `int oO0Oo0 = 0;` | Initialize counter for digit count. |
| 5 | `while (O0OoO0 != 0)` | Loop until all digits have been processed. |
| 7 | `O0OoO0 /= 10;` | Remove the least‑significant digit. |
| 8 | `oO0Oo0++;` | Increment the digit count. |
| 10 | `return oO0Oo0;` | Return the total number of decimal digits. |

**Explanation**

> Purpose: Counts the number of decimal digits in an integer.
> Input: Two integers `IllIlI` and `l1lIl1`, representing the numbers whose digit count is to be determined.
> Output: An integer representing the total number of digits in both input numbers combined.
> Algorithm: Adds the two numbers together, then counts how many times the result can be divided by 10 before it becomes zero.

*4/4 concepts · anchors 6/6 kept (3 exact) · agreement 0.59*

### `mixed` — half descriptive, half noise

**Input**

```cpp
  1  int total(int count, int lllIII)
  2  {
  3    int IllIlI = count + lllIII;
  4    int l1lIl1 = 0;
  5    while (IllIlI != 0)
  6    {
  7      IllIlI /= 10;
  8      l1lIl1++;
  9    }
 10    return l1lIl1;
 11  }
```

**Line-by-line comments**

| line | code | comment |
| ---: | --- | --- |
| 3 | `int IllIlI = count + lllIII;` | Compute the sum of the two inputs; this becomes the digit‑counting target. |
| 4 | `int l1lIl1 = 0;` | Initialize counter for the number of decimal digits. |
| 5 | `while (IllIlI != 0)` | Loop until all digits have been processed. |
| 7 | `IllIlI /= 10;` | Remove the least‑significant digit. |
| 8 | `l1lIl1++;` | Increment the digit count. |
| 10 | `return l1lIl1;` | Return the total digit count. |

**Explanation**

> Purpose: Counts the number of decimal digits in an integer.
> Input: Two integers `count` and `lllIII`, where `count` is the initial value and `lllIII` is added to it.
> Output: An integer representing the total number of digits in the combined result.
> Algorithm: Adds `lllIII` to `count`, then iteratively divides by 10 until the result becomes zero, counting each division as one digit.

*4/4 concepts · anchors 6/6 kept (3 exact) · agreement 0.51*

### `misleading` — names that suggest the wrong operation

**Input**

```cpp
  1  int product(int average, int maximum)
  2  {
  3    int minimum = average + maximum;
  4    int sorted_list = 0;
  5    while (minimum != 0)
  6    {
  7      minimum /= 10;
  8      sorted_list++;
  9    }
 10    return sorted_list;
 11  }
```

**Line-by-line comments**

| line | code | comment |
| ---: | --- | --- |
| 3 | `int minimum = average + maximum;` | Compute the sum of the two inputs; this value will be used as the initial digit count. |
| 4 | `int sorted_list = 0;` | Counter for the number of digits in the sum. |
| 5 | `while (minimum != 0)` | Loop until all digits have been processed. |
| 7 | `minimum /= 10;` | Remove the least‑significant digit. |
| 8 | `sorted_list++;` | Increment the digit counter each iteration. |
| 10 | `return sorted_list;` | Return the total number of digits. |

**Explanation**

> Purpose: Counts how many decimal digits are in the sum of an integer’s average and its maximum value. 
> Input: two ints – `average` (the arithmetic mean) and `maximum` (the largest element). 
> Output: an int representing the number of decimal places in `average + maximum`. 
> Algorithm: Compute the sum, then repeatedly divide by ten to count trailing zeros, stopping when the result becomes zero.

*4/4 concepts · anchors 6/6 kept (3 exact) · agreement 0.52*

## reverse_in_place

*difficulty: easy — a correct answer should mention: revers, swap, two pointer, temporary*

### `original` — as written, meaningful names

**Input**

```cpp
  1  void reverseArray(int values[], int size)
  2  {
  3    int left = 0;
  4    int right = size - 1;
  5    while (left < right)
  6    {
  7      int spare = values[left];
  8      values[left] = values[right];
  9      values[right] = spare;
 10      left++;
 11      right--;
 12    }
 13  }
```

**Line-by-line comments**

| line | code | comment |
| ---: | --- | --- |
| 3 | `int left = 0;` | start index |
| 4 | `int right = size - 1;` | end index |
| 5 | `while (left < right)` | continue until pointers meet or cross |
| 7 | `int spare = values[left];` | store current left element temporarily |
| 8 | `values[left] = values[right];` | swap with right element |
| 9 | `values[right] = spare;` | restore original left element |
| 10 | `left++;` | move left pointer forward |
| 11 | `right--;` | move right pointer backward |

**Explanation**

> Purpose: Reverses the order of elements in an integer array in‑place.
> Input: `int values[]` – pointer to the first element; `int size` – number of elements to process.
> Output: The function modifies `values` in place and returns nothing (`void`).
> Algorithm: Uses two indices starting at each end, swapping the elements they point to until they meet or cross, effectively reversing the array.

*3/4 concepts — missed: two pointer · anchors 8/8 kept (3 exact) · agreement 1.00*

### `terse` — single letters: a, b, x, n

**Input**

```cpp
  1  void a(int b[], int c)
  2  {
  3    int d = 0;
  4    int e = c - 1;
  5    while (d < e)
  6    {
  7      int x = b[d];
  8      b[d] = b[e];
  9      b[e] = x;
 10      d++;
 11      e--;
 12    }
 13  }
```

**Line-by-line comments**

| line | code | comment |
| ---: | --- | --- |
| 3 | `int d = 0;` | start at the first element |
| 4 | `int e = c - 1;` | end at the last element |
| 5 | `while (d < e)` | continue swapping until the two indices meet |
| 6 | `{` | swap elements at positions d and e |
| 8 | `b[d] = b[e];` | move rightmost element to left position |
| 9 | `b[e] = x;` | restore original value at left position |
| 10 | `d++;` | advance left index |
| 11 | `e--;` | decrement right index |

**Explanation**

> Purpose: Reverses the order of elements in an integer array in‑place.
> Input: `b` – pointer to the first element of the array; `c` – number of elements to reverse.
> Output: The function modifies `b` in place and returns nothing (`void`).
> Algorithm: Uses two indices starting at the front and back, swapping elements until they meet or cross each other.

*2/4 concepts — missed: two pointer, temporary · anchors 8/8 kept (4 exact) · agreement 0.63*

### `noise` — visually confusing: lllIII, O0OoO0

**Input**

```cpp
  1  void lllIII(int IllIlI[], int l1lIl1)
  2  {
  3    int O0OoO0 = 0;
  4    int oO0Oo0 = l1lIl1 - 1;
  5    while (O0OoO0 < oO0Oo0)
  6    {
  7      int II1lI1 = IllIlI[O0OoO0];
  8      IllIlI[O0OoO0] = IllIlI[oO0Oo0];
  9      IllIlI[oO0Oo0] = II1lI1;
 10      O0OoO0++;
 11      oO0Oo0--;
 12    }
 13  }
```

**Line-by-line comments**

| line | code | comment |
| ---: | --- | --- |
| 3 | `int O0OoO0 = 0;` | start index |
| 4 | `int oO0Oo0 = l1lIl1 - 1;` | end index |
| 5 | `while (O0OoO0 < oO0Oo0)` | swap elements until the two pointers meet |
| 7 | `int II1lI1 = IllIlI[O0OoO0];` | store current left element |
| 8 | `IllIlI[O0OoO0] = IllIlI[oO0Oo0];` | move right element to left position |
| 9 | `IllIlI[oO0Oo0] = II1lI1;` | restore original left element at right position |
| 10 | `O0OoO0++;` | advance left pointer |
| 11 | `oO0Oo0--;` | decrement right pointer |

**Explanation**

> Purpose: Reverses the order of elements in an integer array in‑place.
> Input: `int IllIlI[]` – pointer to the first element; `int l1lIl1` – number of elements to reverse.
> Output: The function modifies the array in place and returns void.
> Algorithm: Uses two indices starting at the front and back, swapping elements until they meet or cross.

*3/4 concepts — missed: temporary · anchors 8/8 kept (3 exact) · agreement 0.67*

### `mixed` — half descriptive, half noise

**Input**

```cpp
  1  void total(int count[], int index)
  2  {
  3    int lllIII = 0;
  4    int IllIlI = index - 1;
  5    while (lllIII < IllIlI)
  6    {
  7      int l1lIl1 = count[lllIII];
  8      count[lllIII] = count[IllIlI];
  9      count[IllIlI] = l1lIl1;
 10      lllIII++;
 11      IllIlI--;
 12    }
 13  }
```

**Line-by-line comments**

| line | code | comment |
| ---: | --- | --- |
| 3 | `int lllIII = 0;` | start at the first element |
| 4 | `int IllIlI = index - 1;` | end at the last element |
| 5 | `while (lllIII < IllIlI)` | swap elements until the two pointers meet |
| 7 | `int l1lIl1 = count[lllIII];` | store current left value |
| 8 | `count[lllIII] = count[IllIlI];` | move right value to left position |
| 9 | `count[IllIlI] = l1lIl1;` | restore original left value |
| 10 | `lllIII++;` | advance left pointer |
| 11 | `IllIlI--;` | decrement right pointer |

**Explanation**

> Purpose: Reverses the order of elements in an integer array from the start to the specified index.
> Input: `count` is an array of integers; `index` is an integer indicating the position up to which the reversal should occur.
> Output: The function modifies the input array in place and returns nothing.
> Algorithm: Uses two pointers (`lllIII` and `IllIlI`) starting at the beginning and end of the array respectively. Swaps elements at these positions until they meet or cross each other.

*3/4 concepts — missed: temporary · anchors 8/8 kept (3 exact) · agreement 0.52*

### `misleading` — names that suggest the wrong operation

**Input**

```cpp
  1  void product(int average[], int maximum)
  2  {
  3    int minimum = 0;
  4    int sorted_list = maximum - 1;
  5    while (minimum < sorted_list)
  6    {
  7      int is_prime = average[minimum];
  8      average[minimum] = average[sorted_list];
  9      average[sorted_list] = is_prime;
 10      minimum++;
 11      sorted_list--;
 12    }
 13  }
```

**Line-by-line comments**

| line | code | comment |
| ---: | --- | --- |
| 3 | `int minimum = 0;` | start at the first element |
| 4 | `int sorted_list = maximum - 1;` | end at the last element |
| 5 | `while (minimum < sorted_list)` | continue until the two pointers meet |
| 7 | `int is_prime = average[minimum];` | store current smallest value temporarily |
| 8 | `average[minimum] = average[sorted_list];` | move largest remaining value to front |
| 9 | `average[sorted_list] = is_prime;` | restore original smallest value in its new position |
| 10 | `minimum++;` | advance left pointer |
| 11 | `sorted_list--;` | decrement right pointer |

**Explanation**

> Purpose: Rearranges an integer array so that its smallest element becomes the largest and vice‑versa.  
> Input: `average` – pointer to an array of integers; `maximum` – size of the array (number of elements).  
> Output: The function modifies `average` in place; it returns void.  
> Algorithm: Two indices start at the front and back of the array, swapping the values at those positions until they meet or cross each other. This yields a circular permutation where the original minimum moves to the end and the original maximum moves to the front.

*3/4 concepts — missed: revers · anchors 8/8 kept (3 exact) · agreement 0.47*

## binary_search

*difficulty: medium — a correct answer should mention: binary search, sorted, middle, not found*

### `original` — as written, meaningful names

**Input**

```cpp
  1  int findIndex(int table[], int length, int wanted)
  2  {
  3    int low = 0;
  4    int high = length - 1;
  5    while (low <= high)
  6    {
  7      int probe = low + (high - low) / 2;
  8      if (table[probe] == wanted)
  9        return probe;
 10      if (table[probe] < wanted)
 11        low = probe + 1;
 12      else
 13        high = probe - 1;
 14    }
 15    return -1;
 16  }
```

**Line-by-line comments**

| line | code | comment |
| ---: | --- | --- |
| 3 | `int low = 0;` | start search at first element |
| 4 | `int high = length - 1;` | end search at last element |
| 5 | `while (low <= high)` | continue while there is still a valid interval |
| 7 | `int probe = low + (high - low) / 2;` | compute middle index safely to avoid overflow |
| 8 | `if (table[probe] == wanted)` | target found exactly at this position |
| 9 | `return probe;` | return its index |
| 10 | `if (table[probe] < wanted)` | target lies in the upper half |
| 11 | `low = probe + 1;` | discard lower half including current element |
| 12 | `else` | target lies in the lower half |
| 13 | `high = probe - 1;` | discard upper half including current element |
| 15 | `return -1;` | not found – sentinel value |

**Explanation**

> Purpose: Locate the first occurrence of a value in a sorted integer array.  
> Input: `table` – pointer to the first element; `length` – number of elements; `wanted` – target value.  
> Output: Returns the index of the found element, or `-1` if not present.  
> Algorithm: Perform a classic binary search by repeatedly narrowing the half‑open interval `[low, high]`. Compute the midpoint with `(low + high) / 2`, compare the midpoint element with `wanted`, and adjust the interval accordingly until the interval collapses.

*4/4 concepts · anchors 11/11 kept (3 exact) · agreement 1.00*

### `terse` — single letters: a, b, x, n

**Input**

```cpp
  1  int a(int b[], int c, int d)
  2  {
  3    int e = 0;
  4    int x = c - 1;
  5    while (e <= x)
  6    {
  7      int y = e + (x - e) / 2;
  8      if (b[y] == d)
  9        return y;
 10      if (b[y] < d)
 11        e = y + 1;
 12      else
 13        x = y - 1;
 14    }
 15    return -1;
 16  }
```

**Line-by-line comments** — none produced (JSON parsed: False)

**Explanation**

> Purpose: Locate the first index of `d` in a sorted integer array `b`.  
> Input: `b[]` – sorted array; `c` – number of elements to consider; `d` – value to search for.  
> Output: Returns the index of `d` if present, otherwise `-1`.  
> Algorithm: Perform a classic binary‑search loop with a middle‑point calculation to avoid overflow. Compare `b[y]` with `d`; move the left bound rightward when `b[y] < d`, otherwise move the right bound leftward. The loop stops when the interval collapses.

*3/4 concepts — missed: binary search · anchors 0/0 kept (0 exact) · agreement 0.32*

### `noise` — visually confusing: lllIII, O0OoO0

**Input**

```cpp
  1  int lllIII(int IllIlI[], int l1lIl1, int O0OoO0)
  2  {
  3    int oO0Oo0 = 0;
  4    int II1lI1 = l1lIl1 - 1;
  5    while (oO0Oo0 <= II1lI1)
  6    {
  7      int ll1I1l = oO0Oo0 + (II1lI1 - oO0Oo0) / 2;
  8      if (IllIlI[ll1I1l] == O0OoO0)
  9        return ll1I1l;
 10      if (IllIlI[ll1I1l] < O0OoO0)
 11        oO0Oo0 = ll1I1l + 1;
 12      else
 13        II1lI1 = ll1I1l - 1;
 14    }
 15    return -1;
 16  }
```

**Line-by-line comments** — none produced (JSON parsed: False)

**Explanation**

> Purpose: Locate the first index of a target value in a sorted integer array.
> Input: `illIlI[]` – sorted array; `l1lIl1` – number of elements to search; `O0OoO0` – target value.
> Output: Index of the first occurrence of `O0OoO0`, or `-1` if absent.
> Algorithm: Perform binary search on the interval `[oO0Oo0, II1lI1]`. Compute the middle index as `(oO0Oo0 + (II1lI1 - oO0Oo0) / 2)` to avoid overflow. Compare the element at that index with `O0OoO0`; if equal, return it; otherwise narrow the interval and repeat until the interval is empty.

*4/4 concepts · anchors 0/0 kept (0 exact) · agreement 0.36*

### `mixed` — half descriptive, half noise

**Input**

```cpp
  1  int total(int count[], int index, int lllIII)
  2  {
  3    int IllIlI = 0;
  4    int l1lIl1 = index - 1;
  5    while (IllIlI <= l1lIl1)
  6    {
  7      int O0OoO0 = IllIlI + (l1lIl1 - IllIlI) / 2;
  8      if (count[O0OoO0] == lllIII)
  9        return O0OoO0;
 10      if (count[O0OoO0] < lllIII)
 11        IllIlI = O0OoO0 + 1;
 12      else
 13        l1lIl1 = O0OoO0 - 1;
 14    }
 15    return -1;
 16  }
```

**Line-by-line comments** — none produced (JSON parsed: False)

**Explanation**

> Purpose: Locate the first index in an ordered integer array where its value equals a specified target.
> Input: `count` is an array of integers sorted in ascending order; `index` is the size of the array; `lllIII` is the target value to find.
> Output: Returns the index of the first occurrence of `lllIII` if found; otherwise, returns -1.
> Algorithm: Uses binary search to efficiently locate the target value.

*3/4 concepts — missed: middle · anchors 0/0 kept (0 exact) · agreement 0.20*

### `misleading` — names that suggest the wrong operation

**Input**

```cpp
  1  int product(int average[], int maximum, int minimum)
  2  {
  3    int sorted_list = 0;
  4    int is_prime = maximum - 1;
  5    while (sorted_list <= is_prime)
  6    {
  7      int buffer_size = sorted_list + (is_prime - sorted_list) / 2;
  8      if (average[buffer_size] == minimum)
  9        return buffer_size;
 10      if (average[buffer_size] < minimum)
 11        sorted_list = buffer_size + 1;
 12      else
 13        is_prime = buffer_size - 1;
 14    }
 15    return -1;
 16  }
```

**Line-by-line comments**

| line | code | comment |
| ---: | --- | --- |
| 3 | `int sorted_list = 0;` | start searching at the first element |
| 4 | `int is_prime = maximum - 1;` | end search just before the last element |
| 5 | `while (sorted_list <= is_prime)` | binary‑search over the candidate range |
| 7 | `int buffer_size = sorted_list + (is_prime - sorted_list) / 2;` | compute middle index to split the interval |
| 8 | `if (average[buffer_size] == minimum)` | exact match found – return its position |
| 10 | `if (average[buffer_size] < minimum)` | minimum lies in the left half |
| 11 | `sorted_list = buffer_size + 1;` | discard right half |
| 12 | `else` | minimum lies in the right half |
| 13 | `is_prime = buffer_size - 1;` | discard left half |
| 15 | `return -1;` | no occurrence within the interval |

**Explanation**

> Purpose: Locate the index of the first element in an ordered average array that equals the minimum value.  
> Input: `average` – pointer to an integer array; `maximum` – size of the array; `minimum` – target value.  
> Output: Returns the index of the matching element, or -1 if none exists.  
> Algorithm: Perform a binary search on the range [0, max‑1]; at each step compute the middle index and compare it with `minimum`. If equal, return the index; otherwise narrow the search window by updating either the lower bound (`sorted_list`) or the upper bound (`is_prime`). The loop terminates when the window collapses.

*4/4 concepts · anchors 10/10 kept (3 exact) · agreement 0.34*

## gcd_euclid

*difficulty: medium — a correct answer should mention: greatest common, euclid, loop, zero*

### `original` — as written, meaningful names

**Input**

```cpp
  1  int greatestCommon(int alpha, int beta)
  2  {
  3    while (beta != 0)
  4    {
  5      int leftover = alpha % beta;
  6      alpha = beta;
  7      beta = leftover;
  8    }
  9    return alpha;
 10  }
```

**Line-by-line comments**

| line | code | comment |
| ---: | --- | --- |
| 3 | `while (beta != 0)` | Repeatedly apply the Euclidean algorithm until beta becomes zero. |
| 5 | `int leftover = alpha % beta;` | Compute remainder; this step implements the division‑by‑remainder method. |
| 6 | `alpha = beta;` | Shift the larger value to become the divisor for the next iteration. |
| 7 | `beta = leftover;` | The current remainder becomes the new dividend. |
| 9 | `return alpha;` | When beta reaches zero, 'alpha' holds the GCD. |

**Explanation**

> Purpose: Compute the greatest common divisor of two integers using Euclid's algorithm.
> Input: Two integers `alpha` and `beta`.
> Output: An integer representing the greatest common divisor of `alpha` and `beta`.
> Algorithm: Repeatedly replace `alpha` with `beta` and `beta` with the remainder of `alpha` divided by `beta`, until `beta` becomes zero. The last non-zero value is the GCD.

*4/4 concepts · anchors 5/5 kept (1 exact) · agreement 1.00*

### `terse` — single letters: a, b, x, n

**Input**

```cpp
  1  int a(int b, int c)
  2  {
  3    while (c != 0)
  4    {
  5      int d = b % c;
  6      b = c;
  7      c = d;
  8    }
  9    return b;
 10  }
```

**Line-by-line comments**

| line | code | comment |
| ---: | --- | --- |
| 3 | `while (c != 0)` | Repeatedly apply the Euclidean algorithm until the remainder becomes zero. |
| 5 | `int d = b % c;` | Compute the current greatest common divisor. |
| 6 | `b = c;` | Shift the larger value to become the new dividend. |
| 7 | `c = d;` | The smaller value becomes the new divisor. |
| 9 | `return b;` | When c reaches zero, b holds the GCD. |

**Explanation**

> Purpose: Compute the greatest common divisor of two integers using Euclid's algorithm.
> Input: Two integers `b` and `c`.
> Output: An integer representing the GCD of `b` and `c`.
> Algorithm: Repeatedly replace `b` with `c` and `c` with the remainder of `b` divided by `c`, until `c` becomes zero. The last non-zero value is the GCD.

*4/4 concepts · anchors 5/5 kept (1 exact) · agreement 0.80*

### `noise` — visually confusing: lllIII, O0OoO0

**Input**

```cpp
  1  int lllIII(int IllIlI, int l1lIl1)
  2  {
  3    while (l1lIl1 != 0)
  4    {
  5      int O0OoO0 = IllIlI % l1lIl1;
  6      IllIlI = l1lIl1;
  7      l1lIl1 = O0OoO0;
  8    }
  9    return IllIlI;
 10  }
```

**Line-by-line comments**

| line | code | comment |
| ---: | --- | --- |
| 3 | `while (l1lIl1 != 0)` | Repeatedly apply the Euclidean algorithm until the remainder becomes zero. |
| 5 | `int O0OoO0 = IllIlI % l1lIl1;` | Store the current remainder; this will become the new divisor in the next iteration. |
| 6 | `IllIlI = l1lIl1;` | Update the larger divisor to the smaller one. |
| 7 | `l1lIl1 = O0OoO0;` | The previously stored remainder becomes the new dividend. |
| 9 | `return IllIlI;` | When the loop exits, IllIlI holds the greatest common divisor. |

**Explanation**

> Purpose: Computes the greatest common divisor of two integers using the Euclidean algorithm.
> Input: Two integers `IllIlI` and `l1lIl1`.
> Output: An integer representing the GCD of the input numbers.
> Algorithm: Repeatedly replaces the larger number with its remainder when divided by the smaller number until one of them becomes zero.

*4/4 concepts · anchors 5/5 kept (1 exact) · agreement 0.51*

### `mixed` — half descriptive, half noise

**Input**

```cpp
  1  int total(int count, int lllIII)
  2  {
  3    while (lllIII != 0)
  4    {
  5      int IllIlI = count % lllIII;
  6      count = lllIII;
  7      lllIII = IllIlI;
  8    }
  9    return count;
 10  }
```

**Line-by-line comments**

| line | code | comment |
| ---: | --- | --- |
| 3 | `while (lllIII != 0)` | Repeatedly replace `count` with `lllIII`, then set `lllIII` to the remainder; this yields the greatest common divisor. |
| 5 | `int IllIlI = count % lllIII;` | remainder after dividing by current divisor |
| 6 | `count = lllIII;` | new divisor becomes the previous dividend |
| 7 | `lllIII = IllIlI;` | previous remainder becomes new divisor |
| 9 | `return count;` | final value is GCD |

**Explanation**

> Purpose: Computes the greatest common divisor of two integers using Euclid's algorithm.
> Input: Two integers `count` and `lllIII`.
> Output: An integer representing the GCD of `count` and `lllIII`.
> Algorithm: Repeatedly replaces `count` with `lllIII` and `lllIII` with the remainder of `count` divided by `lllIII`, until `lllIII` becomes zero.

*4/4 concepts · anchors 5/5 kept (1 exact) · agreement 0.45*

### `misleading` — names that suggest the wrong operation

**Input**

```cpp
  1  int product(int average, int maximum)
  2  {
  3    while (maximum != 0)
  4    {
  5      int minimum = average % maximum;
  6      average = maximum;
  7      maximum = minimum;
  8    }
  9    return average;
 10  }
```

**Line-by-line comments**

| line | code | comment |
| ---: | --- | --- |
| 3 | `while (maximum != 0)` | Repeatedly apply Euclid's algorithm until the remainder becomes zero. |
| 5 | `int minimum = average % maximum;` | Compute the new divisor as the remainder of the current division. |
| 6 | `average = maximum;` | Shift the larger value to become the smaller one for the next iteration. |
| 7 | `maximum = minimum;` | The previously computed remainder now becomes the new divisor. |
| 9 | `return average;` | When the loop exits, 'average' holds the greatest common divisor. |

**Explanation**

> Purpose: Compute the greatest common divisor (GCD) of two integers using Euclid's algorithm.
> Input: Two integers `average` and `maximum`.
> Output: An integer representing the GCD of the input numbers.
> Algorithm: Repeatedly replace `average` with `maximum` and `maximum` with the remainder of `average` divided by `maximum`. Continue until `maximum` becomes zero; at that point, `average` will be the GCD.

*4/4 concepts · anchors 5/5 kept (1 exact) · agreement 0.59*
