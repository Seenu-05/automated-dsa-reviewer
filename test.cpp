#include <iostream>

using namespace std;

// Inefficient recursive approach
int fibonacci(int n) {
    // Base cases
    if (n <= 1) {
        return n;
    }
    // Branching recursively without storing previous results
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main() {
    int n = 35; // A number high enough to make the inefficiency obvious
    
    cout << "Calculating Fibonacci number for " << n << "..." << endl;
    
    cout << n << "th Fibonacci number is: " << fibonacci(n) << endl;
    
    return 0;
}