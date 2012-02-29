class Function(object):
    def __init__(self, name, arguments, start_pos, end_pos, line_number):
        self.name = name
        self.arguments = arguments
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.line_number = line_number

    def __repr__(self):
        return "Function " + self.name + "(" + self.arguments + ")"


class Variable(object):
    def __init__(self, name, start_pos, end_pos, line_number):
        self.name = name
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.line_number = line_number

    def __repr__(self):
        return "Variable " + self.name


class EntitiesVisitor(object):
    def __init__(self):
        self.functions = []
        self.variables = []

    def _is_in_function(self, start_pos, end_pos):
        for function in self.functions:
            if start_pos >= function.start_pos and end_pos <= function.end_pos:
                return True
        return False

    def add_function(self, name, arguments, start_pos, end_pos, line_number):
        if not self._is_in_function(start_pos, end_pos):
            self.functions.append(Function(name, arguments, start_pos, end_pos, line_number))

    def add_variable(self, name, start_pos, end_pos, line_number):
        if not self._is_in_function(start_pos, end_pos):
            self.variables.append(Variable(name, start_pos, end_pos, line_number))

    def visit_FUNCTION(self, node, source):
        # Named functions only, the getattr returns None if name doesn't exist
        if node.type == "FUNCTION" and getattr(node, "name", None):
            self.add_function(node.name, node.params, node.start, node.end, node.lineno)

    def is_var_function_initializer(node):
        return node.type == "IDENTIFIER" and hasattr(node, "initializer") and node.initializer.type == "FUNCTION"

    def visit_IDENTIFIER(self, node, source):
        # Anonymous functions declared with var name = function() {};
        try:
            if self.is_var_function_initializer(node):
                self.add_function(node.name, node.initializer.params, node.start, node.initializer.end, node.lineno)
        except Exception as e:
            pass

    def visit_ASSIGN(self, node, source):
        if node[1].type == "FUNCTION":
            self.add_function(node[0].value, node[1].params, node[1].start, node[1].end, node[1].lineno)

    def visit_PROPERTY_INIT(self, node, source):
        # Anonymous functions declared as a property of an object
        try:
            if node.type == "PROPERTY_INIT" and node[1].type == "FUNCTION":
                self.add_function(node[0].value, node[1].params, node[1].start, node[1].end, node[0].lineno)
        except Exception as e:
            pass

    def is_var_being_initialized(self, node):
        return getattr(node, "initializer", False)

    def extract_variables(self, node):
        variables = []
        for subvar_node in node:
            if self.is_var_being_initialized(subvar_node):
                variables.append({
                    "name": subvar_node.value,
                    "line_number": subvar_node.lineno,
                    "start_pos": subvar_node.start,
                    "end_pos": subvar_node.initializer.end
                })
            else:
                variables.append({
                    "name": subvar_node.value,
                    "line_number": subvar_node.lineno,
                    "start_pos": subvar_node.start,
                    "end_pos": subvar_node.end
                })
        return variables

    def visit_VAR(self, node, source):
        variables = self.extract_variables(node)
        for variable in variables:
            self.add_variable(variable["name"], variable["start_pos"], variable["end_pos"], variable["line_number"])
