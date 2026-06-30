import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from compiler.runner import run_code
from config import Config

Config.init_app()

print("Testing Python Runner...")
py_code = """
import sys
name = sys.stdin.readline().strip()
print(f"Hello, {name}!")
"""
res = run_code('python', py_code, 'World')
print(res)
assert "Hello, World!" in res['stdout']

print("\nTesting JavaScript Runner...")
js_code = """
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
});
rl.on('line', (line) => {
    console.log("Hello, " + line + "!");
    process.exit(0);
});
"""
res = run_code('javascript', js_code, 'JS-World')
print(res)
assert "Hello, JS-World!" in res['stdout']

print("\nTesting C Runner...")
c_code = """
#include <stdio.h>
int main() {
    char name[100];
    if (scanf("%99s", name) == 1) {
        printf("Hello, %s!\\n", name);
    }
    return 0;
}
"""
res = run_code('c', c_code, 'C-World')
print(res)
assert "Hello, C-World!" in res['stdout']

print("\nTesting C++ Runner...")
cpp_code = """
#include <iostream>
#include <string>
int main() {
    std::string name;
    if (std::cin >> name) {
        std::cout << "Hello, " << name << "!" << std::endl;
    }
    return 0;
}
"""
res = run_code('cpp', cpp_code, 'CPP-World')
print(res)
assert "Hello, CPP-World!" in res['stdout']

print("\nTesting Java Runner...")
java_code = """
import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        if (scanner.hasNext()) {
            System.out.println("Hello, " + scanner.next() + "!");
        }
    }
}
"""
res = run_code('java', java_code, 'Java-World')
print(res)
assert "Hello, Java-World!" in res['stdout']

print("\nTesting Timeout Protection...")
timeout_code = """
import time
while True:
    time.sleep(1)
"""
res = run_code('python', timeout_code)
print(res)
assert "Timeout" in res['stderr'] or "exceeded limit" in res['stderr']

print("\nAll Runners PASSED successfully!")
