import sys
import re
from colorama import Fore

def iswhitespace(char):
    return char == " " or char == "\t" or char == "\n" or char.isspace()

OPERATORS = ["=", ";", ",", ".", "{", "}", "(", ")"]

class Lexer():

    def __init__(self, code):
        self.code = code

    def next(self):
        found_start = False
        start_index = 0
        end_index = 0
        for i, char in enumerate(self.code):
            if iswhitespace(char):
                if found_start:
                    end_index = i
                    break
            elif char in OPERATORS:
                if found_start:
                    end_index = i
                    break
                else:
                    found_start = True
                    start_index = i
                    end_index = i+1
                    break
            elif not found_start:
                start_index = i
                found_start = True
        
        if not found_start:
            return ""

        if end_index == 0:
            end_index = len(self.code)

        token = self.code[start_index:end_index]
        self.code = self.code[end_index:]
        return token

class CppClassVariable():

    def __init__(self, var_type, var_name, default_value=None):
        self.var_type = var_type
        self.var_name = var_name

    def __repr__(self) -> str:
        return f"Var({self.var_type} {self.var_name})"

class CppClassConstructor():

    def __init__(self, arguments_types) -> None:
        self.arguments_types = arguments_types
    
    def __repr__(self) -> str:
        return f"Constructor({self.arguments_types})"

class CppClassDestractor():

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"Destructor()"

class CppClassFunction():

    def __init__(self, name):
        self.name = name

    def __repr__(self) -> str:
        return f"Function({self.name})"

class CppClass():

    def __init__(self, name):
        self.name = name
        self.constructors = []
        self.destractor = None
        self.variables = []
        self.functions = []

    def __repr__(self) -> str:
        return f"Class({self.name}, {self.constructors}, {self.destractor}, {self.variables}, {self.functions})"

def parse_if_function(line):
    lexer = Lexer(line)
    return_type = lexer.next()
    function_name = lexer.next()
    pare = lexer.next()
    if pare == "(" and ")" in line:
        return CppClassFunction(function_name)
    
    return None

def parse_if_constructor(line, curr_class_name):
    lexer = Lexer(line)
    class_name = lexer.next()
    pare = lexer.next()
    if class_name == curr_class_name and pare == "(" and ")" in line:
        types = []
        while True:
            var_type_list = []
            while not((token := lexer.next()) in [",", ")"]):
                var_type_list.append(token)
            if len(var_type_list) > 1:
                types.append(" ".join(var_type_list[:-1]))
            if token == ")":
                break
        return CppClassConstructor(types)
                
    return None

def parse_if_destractor(line, curr_class_name):
    lexer = Lexer(line)
    class_name = lexer.next()
    if class_name != "" and class_name[0] == "~" and class_name[1:] == curr_class_name:
        return CppClassDestractor()
    return None

def parse_if_variable(line):
    lexer = Lexer(line)
    var_type = lexer.next()
    var_name = lexer.next()
    third_token = lexer.next()
    if var_type != "" and var_name != "":
        if third_token == ";":
            return CppClassVariable(var_type, var_name)

        if third_token == "=":
            default_value = lexer.next()
            semi_colon = lexer.next();
            if default_value != "" and semi_colon == ";":
                return CppClassVariable(var_type, var_name, default_value)
    return None

files = sys.argv[1:-1]
out_file = sys.argv[-1]

input_code = ""
for file in files:
    with open(file, "r") as f:
        print(f"{Fore.MAGENTA}Reading file ", file)
        input_code += f.read() + "\n"

classes = {}

in_class = False
class_name = ""
class_brace_count = 0
class_fields_state = "private"

code_lines = input_code.splitlines()

for line in code_lines:
    lexer = Lexer(line)

    if in_class:
        token = lexer.next()

        match token:
            case "{":
                class_brace_count += 1
            case "}":
                class_brace_count -= 1
                if class_brace_count == 0:
                    in_class = False
            case "public:" | "private:":
                class_fields_state = token[:-1]
                print(f"{Fore.CYAN}Class fields stated changed to {token[:-1]}")
            case _:
                not_in_function = class_brace_count == 1
                if not_in_function:
                    v = parse_if_variable(line)
                    if v != None:
                        print(f"{Fore.BLUE}Found a {class_fields_state} {v}")
                        if class_fields_state == "public":
                            classes[class_name].variables.append(v)
                    elif (c := parse_if_constructor(line, class_name)) != None:
                        print(f"{Fore.BLUE}Found a {c}")
                        classes[class_name].constructors.append(c)
                    elif (d := parse_if_destractor(line, class_name)) != None:
                        print(f"{Fore.BLUE}Found a {d}")
                        classes[class_name].destructor = d
                    elif (f := parse_if_function(line)) != None:
                        print(f"{Fore.BLUE}Found a {class_fields_state} {f}")
                        if class_fields_state == "public":
                            classes[class_name].functions.append(f)


    while (token := lexer.next()) != "":
        match token:
            case "struct" | "class":
                in_class = True
                class_name = lexer.next()
                classes[class_name] = CppClass(class_name)
                print(f"{Fore.GREEN}Found {token} {class_name}")
                if token == "struct":
                    class_fields_state = "public"
                else:
                    class_fields_state = "private"
            case "{":
               if in_class:
                    class_brace_count += 1
            case "}":
               if in_class:
                    class_brace_count -= 1

print(Fore.RESET,classes)
