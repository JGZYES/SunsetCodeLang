#!/usr/bin/env python3
"""
SCL to Python Compiler
Converts SCL code to Python code with interpreter and plugins embedded
"""

import sys
import os
import re
import ast


class PluginAnalyzer:
    """Analyze plugin code to understand its syntax and implementation"""
    
    def __init__(self):
        self.plugins = {}  # Cache for analyzed plugins
        self.plugin_file_cache = {}  # Cache for plugin file contents
    
    def analyze_plugin(self, plugin_name):
        """Analyze a plugin's code"""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name]
        
        # Get the plugins directory path relative to the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        plugin_file = os.path.join(script_dir, 'plugins', f'{plugin_name}.py')
        
        if not os.path.exists(plugin_file):
            print(f"Error: Plugin file '{plugin_file}' not found")
            return None
        
        # Check if file content is cached
        mtime = os.path.getmtime(plugin_file)
        cache_key = (plugin_file, mtime)
        if cache_key in self.plugin_file_cache:
            code = self.plugin_file_cache[cache_key]
        else:
            try:
                with open(plugin_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                # Cache the file content
                self.plugin_file_cache[cache_key] = code
            except Exception as e:
                print(f"Error reading plugin file {plugin_file}: {e}")
                return None
        
        # Parse the code
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            print(f"Error parsing plugin {plugin_name}: Syntax error at line {e.lineno}, column {e.offset}: {e.msg}")
            return None
        
        # Extract information
        try:
            plugin_info = self._extract_plugin_info(tree, plugin_name)
            plugin_info['code'] = code
            self.plugins[plugin_name] = plugin_info
            return plugin_info
        except Exception as e:
            print(f"Error extracting plugin information from {plugin_name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_plugin_info(self, tree, plugin_name):
        """Extract plugin information from AST"""
        info = {
            'name': plugin_name,
            'imports': [],
            'dependencies': [],
            'commands': {},
            'class_name': f'{plugin_name.capitalize()}Plugin'
        }
        
        # Get the plugins directory path relative to the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        plugins_dir = os.path.join(script_dir, 'plugins')
        
        # Extract imports and dependencies
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    info['imports'].append(alias.name)
                    # Check if this is a plugin dependency
                    if os.path.exists(plugins_dir) and alias.name in os.listdir(plugins_dir) and os.path.isfile(os.path.join(plugins_dir, f'{alias.name}.py')):
                        info['dependencies'].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    info['imports'].append(node.module)
                    # Check if this is a plugin dependency
                    if os.path.exists(plugins_dir) and node.module in os.listdir(plugins_dir) and os.path.isfile(os.path.join(plugins_dir, f'{node.module}.py')):
                        info['dependencies'].append(node.module)
            
            # Extract command patterns from parse_statement
            elif isinstance(node, ast.FunctionDef) and node.name == 'parse_statement':
                self._extract_commands_from_parse(node, info)
        
        return info
    
    def _extract_commands_from_parse(self, node, info):
        """Extract command patterns from parse_statement function"""
        for child in ast.walk(node):
            if isinstance(child, ast.Compare) and isinstance(child.left, ast.Subscript):
                # Check for tokens[pos][1] == 'command'
                if self._is_tokens_access(child.left):
                    if isinstance(child.comparators[0], ast.Constant):
                        command = child.comparators[0].value
                        if isinstance(command, str):
                            info['commands'][command] = {'type': 'direct'}
            
            elif isinstance(child, ast.Compare) and isinstance(child.left, ast.Name):
                # Check for command_suffix == 'c'
                if child.left.id == 'command_suffix':
                    if isinstance(child.comparators[0], ast.Constant):
                        suffix = child.comparators[0].value
                        if isinstance(suffix, str):
                            info['commands'][f'sui-{suffix}'] = {'type': 'sui'}
    
    def _is_tokens_access(self, node):
        """Check if node is tokens[pos][1]"""
        if (isinstance(node, ast.Subscript) and 
            isinstance(node.value, ast.Name) and 
            node.value.id == 'tokens'):
            if isinstance(node.slice, ast.Constant) or isinstance(node.slice, ast.Name):
                return True
        return False


class SCLCompiler:
    def __init__(self):
        self.variables = {}
        self.imports = set()
        self.indent_level = 0
        self.plugin_analyzer = PluginAnalyzer()
        self.loaded_plugins = set()
    
    def _detect_plugin_conflicts(self, resolved_plugins):
        """Detect command conflicts between plugins"""
        command_map = {}
        conflicts = []
        
        for plugin_name in resolved_plugins:
            plugin_info = self.plugin_analyzer.analyze_plugin(plugin_name)
            if not plugin_info:
                continue
            
            for command in plugin_info.get('commands', {}):
                if command in command_map:
                    conflicts.append((command, command_map[command], plugin_name))
                else:
                    command_map[command] = plugin_name
        
        return conflicts
    
    def compile(self, scl_code, filename="input.scl", minify=False):
        """Compile SCL code to Python code with embedded interpreter and plugins"""
        lines = scl_code.split('\n')
        
        # First pass: collect plugins
        plugins_to_load = []
        for line in lines:
            if line.startswith('simp{') and line.endswith('}'):
                import_content = line[5:-1].strip()
                if not import_content.startswith('scl :'):
                    plugins_to_load.append(import_content)
        
        # Resolve plugin dependencies
        resolved_plugins = self._resolve_plugin_dependencies(plugins_to_load)
        
        # Detect plugin conflicts
        conflicts = self._detect_plugin_conflicts(resolved_plugins)
        if conflicts:
            print("Warning: Command conflicts detected between plugins:")
            for command, plugin1, plugin2 in conflicts:
                print(f"  Command '{command}' is defined in both {plugin1} and {plugin2}")
            print("  The last loaded plugin will take precedence.")
        
        # Load SCL interpreter code
        scl_interpreter_code = self._load_scl_interpreter()
        
        # Load plugin codes
        plugin_codes = {}
        for plugin_name in resolved_plugins:
            plugin_info = self.plugin_analyzer.analyze_plugin(plugin_name)
            if plugin_info:
                plugin_codes[plugin_name] = plugin_info['code']
        
        # Generate embedded Python code
        python_code = self._generate_embedded_code(scl_code, scl_interpreter_code, plugin_codes, filename, minify)
        return python_code
    
    def _resolve_plugin_dependencies(self, plugins_to_load):
        """Resolve plugin dependencies and return an ordered list"""
        resolved = set()
        unresolved = set(plugins_to_load)
        order = []
        
        print(f"Resolving dependencies for plugins: {plugins_to_load}")
        
        while unresolved:
            # Find plugins with all dependencies resolved
            progress = False
            for plugin_name in list(unresolved):
                plugin_info = self.plugin_analyzer.analyze_plugin(plugin_name)
                if not plugin_info:
                    print(f"Warning: Skipping plugin {plugin_name} due to analysis errors")
                    unresolved.remove(plugin_name)
                    continue
                
                # Check if all dependencies are resolved
                dependencies = plugin_info.get('dependencies', [])
                print(f"Plugin {plugin_name} has dependencies: {dependencies}")
                
                if all(dep in resolved for dep in dependencies):
                    # Add to resolved and order
                    resolved.add(plugin_name)
                    order.append(plugin_name)
                    unresolved.remove(plugin_name)
                    progress = True
                    print(f"Resolved plugin: {plugin_name}")
                    
                    # Add dependencies to unresolved if not already processed
                    for dep in dependencies:
                        if dep not in resolved and dep not in unresolved:
                            print(f"Adding dependency {dep} for plugin {plugin_name}")
                            unresolved.add(dep)
            
            if not progress:
                # No progress made, break to avoid infinite loop
                print(f"Warning: Unable to resolve all dependencies. Remaining: {unresolved}")
                break
        
        print(f"Resolved plugin order: {order}")
        return order
    
    def _minify_code(self, code):
        """Minify Python code by removing comments and whitespace"""
        lines = code.split('\n')
        minified_lines = []
        in_multiline_comment = False
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Handle multiline comments
            if '"""' in line or "''" in line:
                in_multiline_comment = not in_multiline_comment
                continue
            
            if in_multiline_comment:
                continue
            
            # Remove single-line comments
            if '#' in line:
                line = line.split('#')[0].rstrip()
                if not line:
                    continue
            
            # Remove leading and trailing whitespace
            line = line.strip()
            if line:
                minified_lines.append(line)
        
        return '\n'.join(minified_lines)
    
    def _load_scl_interpreter(self):
        """Load SCL interpreter code"""
        try:
            # Get the script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            scl_path = os.path.join(script_dir, 'scl.py')
            
            with open(scl_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Remove the main function execution at the end
            lines = code.split('\n')
            filtered_lines = []
            in_main_block = False
            
            for line in lines:
                if line.strip() == 'if __name__ == "__main__":':
                    in_main_block = True
                    continue
                if in_main_block:
                    if line.strip() and not line.startswith('    '):
                        in_main_block = False
                    else:
                        continue
                filtered_lines.append(line)
            
            return '\n'.join(filtered_lines)
        except Exception as e:
            print(f"Error loading SCL interpreter: {e}")
            return ""
    
    def _generate_header(self, filename):
        """Generate the header for the embedded code"""
        return [
            '#!/usr/bin/env python3',
            f'# Generated from {filename} by SCL Compiler',
            '# Embedded SCL interpreter and plugins',
            ''
        ]
    
    def _generate_interpreter_code(self, scl_interpreter_code, minify):
        """Generate the SCL interpreter code"""
        code = ['\n# ==== SCL INTERPRETER ====\n']
        if minify:
            code.append(self._minify_code(scl_interpreter_code))
        else:
            code.append(scl_interpreter_code)
        code.append('')
        return code
    
    def _generate_plugin_codes(self, plugin_codes, minify):
        """Generate the plugin codes"""
        code = []
        for plugin_name, plugin_code in plugin_codes.items():
            code.append(f'\n# ==== PLUGIN: {plugin_name} ====\n')
            if minify:
                code.append(self._minify_code(plugin_code))
            else:
                code.append(plugin_code)
            code.append('')
        return code
    
    def _generate_main_function(self, plugin_codes, scl_code):
        """Generate the main function code"""
        code = ['\n# ==== MAIN EXECUTION ====\n\ndef main():\n    """Run the embedded SCL code"""\n    print("Running embedded SCL code...")\n    print("=" * 50)\n    \n    # Create SCL interpreter\n    interpreter = SCLInterpreter()\n    \n    # Load plugins\n']
        
        # Add plugin loading code
        for plugin_name in plugin_codes:
            code.append(f"    interpreter.load_plugin('{plugin_name}')\n")
        
        # Add SCL code execution
        code.append('\n    # SCL code to execute\n    scl_code = """')
        # 安全地嵌入 SCL 代码，处理三引号
        for line in scl_code.split('\n'):
            code.append(line.replace('"""', '\\"""'))
            code.append('\n')
        code.append('"""\n')
        
        # Add execution code
        code.append('\n    # Execute SCL code\n    try:\n        success = interpreter.execute(scl_code, "embedded")\n        if not success:\n            print("Error: Failed to execute SCL code")\n    except Exception as e:\n        print(f"Error: {e}")\n    \n    print("=" * 50)\n    print("Execution completed.")\n\n\nif __name__ == "__main__":\n    main()\n')
        
        return code
    
    def _generate_embedded_code(self, scl_code, scl_interpreter_code, plugin_codes, filename, minify=False):
        """Generate embedded Python code"""
        # Use a single string buffer for more efficient concatenation
        code_buffer = []
        
        # Add header
        code_buffer.extend(self._generate_header(filename))
        
        # Add SCL interpreter code
        code_buffer.extend(self._generate_interpreter_code(scl_interpreter_code, minify))
        
        # Add plugin codes
        code_buffer.extend(self._generate_plugin_codes(plugin_codes, minify))
        
        # Add main function
        code_buffer.extend(self._generate_main_function(plugin_codes, scl_code))
        
        return ''.join(code_buffer)


def main():
    """Main function"""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='SCL to Python Compiler')
    parser.add_argument('input_file', help='Input SCL file')
    parser.add_argument('output_file', nargs='?', help='Output Python file (optional, default: stdout)')
    parser.add_argument('-m', '--minify', action='store_true', help='Minify the generated code')
    
    args = parser.parse_args()
    
    input_file = args.input_file
    output_file = args.output_file
    minify = args.minify
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    # Read SCL code
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            scl_code = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Compile to Python
    compiler = SCLCompiler()
    python_code = compiler.compile(scl_code, input_file, minify)
    
    # Output
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(python_code)
            print(f"Successfully compiled {input_file} to {output_file}")
            if minify:
                print("The file has been minified to reduce size.")
            else:
                print("The file includes embedded SCL interpreter and plugins.")
        except Exception as e:
            print(f"Error writing file: {e}")
            sys.exit(1)
    else:
        print(python_code)


if __name__ == '__main__':
    main()
