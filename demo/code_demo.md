## Working with C++ Variables

When programming in C++, you often need to declare and initialize variables. Here's a simple example of how to do that:

```
#include <iostream>

int main() {
    int a = 10; 
    int b = 5;  
    
    int result = a + b; 
    
    std::cout << "The result of adding " << a 
    << " and " << b << " is: " 
    << result << std::endl;
    
    return 0;
}
```

In the code block above, we have a simple C++ program that declares two integer variables 'a' and 'b', initializes them with values, calculates their sum, and then prints the result to the console using std::cout. This is just a basic example to demonstrate variable declaration and initialization in C++.