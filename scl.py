#!/usr/bin/env python3
"""
SunsetCodeLang (SCL) Interpreter
Main interpreter for the SCL language
"""

import sys
import os
import re
import importlib.util
import tkinter as tk

class SCLInterpreter:
    def __init__(self):
        self.variables = {}  # 变量存储
        self.functions = {}  # 函数存储
        self.plugins = {}  # 插件存储
        self.loaded_plugins = set()  # 已加载插件
        self.debug_mode = False  # 默认为false，不开启debug模式
        
        # 缓存管理 - 限制缓存大小
        self.expression_cache = {}  # 缓存表达式求值结果
        self.token_cache = {}  # 缓存tokenize结果
        self.code_block_cache = {}  # 缓存代码块执行结果
        self.statement_cache = {}  # 缓存语句解析结果
        
        # 缓存大小限制
        self.MAX_CACHE_SIZE = 1000
        
        # 预编译正则表达式
        import re
        self.comment_pattern = re.compile(r'^\s*(#|//)')
        self.empty_pattern = re.compile(r'^\s*$')
        
        # 预定义常量
        self.multi_line_starts = {
            'sif ', 'swhile :', 'swhile |', 'swhi ', 'srg', 'sdef <', 'sclass <'
        }
        
        # 操作符优先级映射
        self.operator_precedence = {
            '*': 3,
            '/': 3,
            '+': 2,
            '-': 2,
            '>': 1,
            '<': 1,
            '==': 1,
            '!=': 1,
            '>=': 1,
            '<=': 1,
            '&': 0,
            '|': 0
        }
        
        # 快速操作映射
        self.operation_map = {
            '+': lambda a, b: str(a) + str(b) if isinstance(a, str) or isinstance(b, str) else a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b if b != 0 else 0,
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '==': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            '&': lambda a, b: a and b,
            '|': lambda a, b: a or b
        }
    
    def _find_plugin_class(self, plugin_module):
        """Find the plugin class in a module"""
        for name in dir(plugin_module):
            if name.endswith('Plugin') and name[0].isupper():
                return name
        return None
    
    def _manage_cache(self, cache):
        """管理缓存大小，防止内存过度使用"""
        if len(cache) > self.MAX_CACHE_SIZE:
            # 删除最旧的缓存项
            for key in list(cache.keys())[:len(cache) - self.MAX_CACHE_SIZE]:
                del cache[key]

    def _register_plugin_instance(self, plugin_name, plugin_instance, is_web=False, url=None):
        """Register a plugin instance"""
        self.plugins[plugin_name] = plugin_instance
        if hasattr(plugin_instance, 'register_syntax'):
            plugin_instance.register_syntax()
        if self.debug_mode:
            if is_web:
                print(f"Debug: Loaded web plugin: {plugin_name} from {url}, Total plugins: {list(self.plugins.keys())}")
            else:
                print(f"Debug: Loaded plugin: {plugin_name}, Total plugins: {list(self.plugins.keys())}")

    def load_plugin(self, plugin_path):
        """Load a plugin from the given path or URL"""
        try:
            if plugin_path.startswith('web : '):
                return self._load_web_plugin(plugin_path)
            else:
                return self._load_local_plugin(plugin_path)
        except Exception as e:
            print(f"Error loading plugin {plugin_path}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _load_web_plugin(self, plugin_path):
        """Load a plugin from a web URL"""
        import urllib.request
        import tempfile
        import hashlib
        
        url = plugin_path[6:].strip()
        plugin_name = 'web_' + hashlib.md5(url.encode()).hexdigest()[:8]
        
        if plugin_name in self.plugins:
            return True
        
        print(f"Downloading plugin from: {url}")
        try:
            with urllib.request.urlopen(url) as response:
                if hasattr(response, 'status') and response.status is not None and response.status != 200:
                    print(f"Error: Failed to download plugin from {url}, status code: {response.status}")
                    return False
                plugin_code = response.read().decode('utf-8')
        except Exception as e:
            print(f"Error: Failed to download plugin from {url}: {e}")
            return False
        
        temp_plugin_file = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
                temp_file.write(plugin_code.encode('utf-8'))
                temp_plugin_file = temp_file.name
            
            spec = importlib.util.spec_from_file_location(plugin_name, temp_plugin_file)
            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)
            
            plugin_class_name = self._find_plugin_class(plugin_module)
            if not plugin_class_name:
                print(f"Error: Plugin from {url} does not have a proper plugin class")
                return False
            
            plugin_class = getattr(plugin_module, plugin_class_name)
            plugin_instance = plugin_class(self)
            self._register_plugin_instance(plugin_name, plugin_instance, True, url)
            return True
        finally:
            if temp_plugin_file and os.path.exists(temp_plugin_file):
                os.unlink(temp_plugin_file)

    def _load_local_plugin(self, plugin_path):
        """Load a plugin from the local filesystem"""
        module_name = plugin_path.replace('>', '.')
        full_module_name = f'plugins.{module_name}'
        
        if full_module_name in self.loaded_plugins:
            return True
        
        plugin_file = os.path.join('plugins', plugin_path.replace('>', os.sep) + '.py')
        
        if not os.path.exists(plugin_file):
            print(f"Error: Plugin {plugin_path} not found at {plugin_file}")
            return False
        
        spec = importlib.util.spec_from_file_location(full_module_name, plugin_file)
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)
        
        plugin_class = getattr(plugin_module, f'{plugin_path.split(">")[-1].capitalize()}Plugin', None)
        if not plugin_class:
            print(f"Error: Plugin {plugin_path} does not have a proper plugin class")
            return False
        
        plugin_instance = plugin_class(self)
        self.plugins[plugin_path] = plugin_instance
        self.loaded_plugins.add(full_module_name)
        self._register_plugin_instance(plugin_path, plugin_instance)
        return True
    
    def import_scl_file(self, scl_path, line_num):
        """Import and execute another SCL file
        
        Args:
            scl_path: Path to SCL file (local or URL)
            line_num: Current line number for error reporting
        """
        try:
            # Check if path is a URL
            if scl_path.startswith('http://') or scl_path.startswith('https://'):
                # Download from URL
                import urllib.request
                import tempfile
                
                print(f"Downloading SCL file from: {scl_path}")
                
                try:
                    with urllib.request.urlopen(scl_path) as response:
                        code = response.read().decode('utf-8')
                except Exception as e:
                    print(f"Error at line {line_num}: Failed to download SCL file from {scl_path}")
                    print(f"Error: {e}")
                    return False
            else:
                # Load from local file
                if not os.path.exists(scl_path):
                    print(f"Error at line {line_num}: SCL file not found: {scl_path}")
                    return False
                
                with open(scl_path, 'r', encoding='utf-8') as f:
                    code = f.read()
            
            # Execute the imported SCL code
            print(f"Executing imported SCL file: {scl_path}")
            success = self.execute(code, scl_path)
            
            if not success:
                print(f"Error at line {line_num}: Failed to execute imported SCL file: {scl_path}")
                return False
            
            return True
        except Exception as e:
            print(f"Error at line {line_num}: Failed to import SCL file {scl_path}")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def tokenize(self, code):
        """Tokenize the SCL code (optimized with state machine and caching)"""
        # 检查缓存
        code_hash = hash(code)
        if code_hash in self.token_cache:
            return self.token_cache[code_hash]
        
        code = code.strip()
        i = 0
        n = len(code)
        if n == 0:
            self.token_cache[code_hash] = []
            return []
        
        # 预定义常量
        whitespace_chars = {' ', '\t', '\n', '\r'}
        operator_chars = {'+', '-', '*', '/', '=', '<', '>', '!', '&', '|'}
        paren_chars = {'(', ')', '[', ']', '{', '}'}
        
        # 预分配空间，减少列表扩展开销
        tokens = []
        token_count = 0
        
        while i < n:
            # 快速跳过空白字符
            while i < n and code[i] in whitespace_chars:
                i += 1
            
            if i >= n:
                break
            
            char = code[i]
            
            if char == '"':
                # 字符串处理
                j = i + 1
                # 快速查找字符串结束位置
                while j < n:
                    if code[j] == '\\' and j + 1 < n:
                        j += 2
                    elif code[j] == '"':
                        break
                    else:
                        j += 1
                # 处理转义字符
                string_content = code[i+1:j]
                string_content = string_content.replace('\\n', '\n').replace('\\\\', '\\')
                tokens.append(('STRING', string_content))
                i = j + 1 if j < n else n
            
            elif char.isdigit():
                # 数字处理
                j = i
                while j < n and (code[j].isdigit() or code[j] == '.'):
                    j += 1
                tokens.append(('NUMBER', code[i:j]))
                i = j
            
            elif char.isalpha() or char == '_':
                # 标识符处理
                j = i
                while j < n and (code[j].isalnum() or code[j] == '_'):
                    j += 1
                tokens.append(('IDENTIFIER', code[i:j]))
                i = j
            
            elif char == '|':
                tokens.append(('SEPARATOR', char))
                i += 1
            
            elif char == ':':
                tokens.append(('ASSIGN', char))
                i += 1
            
            elif char in operator_chars:
                # 运算符处理
                j = i
                while j < n and code[j] in operator_chars:
                    j += 1
                tokens.append(('OPERATOR', code[i:j]))
                i = j
            
            elif char in paren_chars:
                tokens.append(('PAREN', char))
                i += 1
            
            elif char == '#' or (char == '/' and i + 1 < n and code[i + 1] == '/'):
                # 注释处理
                j = i
                while j < n and code[j] != '\n':
                    j += 1
                i = j
            
            else:
                tokens.append(('UNKNOWN', char))
                i += 1
        
        # 缓存结果
        self.token_cache[code_hash] = tokens
        # 管理缓存大小
        self._manage_cache(self.token_cache)
        
        return tokens
    
    def parse_expression(self, tokens, pos):
        """Parse an expression from the tokens (optimized with precedence handling)"""
        # 检查缓存
        cache_key = (tuple(tokens), pos)
        if cache_key in self.statement_cache:
            return self.statement_cache[cache_key]
        
        if pos >= len(tokens):
            result = (None, pos)
            self.statement_cache[cache_key] = result
            return result
        
        # 递归下降解析器，支持运算符优先级
        def parse_level(level, pos):
            if level == 4:  # 最高优先级：括号和基本表达式
                return self.parse_primary(tokens, pos)
            
            left, pos = parse_level(level + 1, pos)
            if left is None:
                return None, pos
            
            while pos < len(tokens) and tokens[pos][0] == 'OPERATOR':
                op = tokens[pos][1]
                op_prec = self.operator_precedence.get(op, -1)
                
                if op_prec != level:
                    break
                
                pos += 1
                right, pos = parse_level(level + 1, pos)
                if right is None:
                    return None, pos
                
                # 构建二元表达式
                left = [left, tokens[pos-1], right]
            
            return left, pos
        
        # 从最低优先级开始解析
        result = parse_level(0, pos)
        self.statement_cache[cache_key] = result
        return result
    
    def parse_primary(self, tokens, pos):
        """Parse a primary expression"""
        if pos >= len(tokens):
            return None, pos
        
        token = tokens[pos]
        if token[0] == 'STRING' or token[0] == 'NUMBER':
            return token, pos + 1
        elif token[0] == 'IDENTIFIER':
            # Check if this is a function call: identifier(arguments)
            if pos + 1 < len(tokens) and tokens[pos + 1][0] == 'PAREN' and tokens[pos + 1][1] == '(':
                # Parse function name
                func_name = token[1]
                pos += 2  # Skip identifier and '('
                
                # Parse arguments
                args = []
                while pos < len(tokens) and not (tokens[pos][0] == 'PAREN' and tokens[pos][1] == ')'):
                    arg, pos = self.parse_expression(tokens, pos)
                    if arg:
                        args.append(arg)
                    # Skip commas
                    if pos < len(tokens) and (tokens[pos][0] == 'SEPARATOR' and tokens[pos][1] == ',' or tokens[pos][0] == 'UNKNOWN' and tokens[pos][1] == ','):
                        pos += 1
                
                if pos < len(tokens) and tokens[pos][0] == 'PAREN' and tokens[pos][1] == ')':
                    pos += 1
                    # Return a function call expression
                    return ('FUNCTION_CALL', func_name, args), pos
            # Otherwise, return the identifier
            return token, pos + 1
        elif token[0] == 'PAREN' and token[1] == '(':
            expr, pos = self.parse_expression(tokens, pos + 1)
            if pos < len(tokens) and tokens[pos][0] == 'PAREN' and tokens[pos][1] == ')':
                return expr, pos + 1
            return None, pos
        return None, pos
    
    def _skip_whitespace(self, tokens, pos):
        """Skip whitespace tokens"""
        while pos < len(tokens) and (tokens[pos][0] == 'UNKNOWN' and tokens[pos][1].isspace()):
            pos += 1
        return pos

    def parse_statement(self, tokens, pos):
        """Parse a statement from the tokens"""
        # Check for variable assignment with plugin pipeline: set var | var : plugin : command
        if pos < len(tokens) and tokens[pos][0] == 'IDENTIFIER' and tokens[pos][1] == 'set':
            var_pos = pos + 1
            if var_pos < len(tokens) and tokens[var_pos][0] == 'IDENTIFIER':
                var_name = tokens[var_pos][1]
                pipe_pos = var_pos + 1
                if pipe_pos < len(tokens) and tokens[pipe_pos][0] == 'SEPARATOR' and tokens[pipe_pos][1] == '|':
                    after_pipe_pos = pipe_pos + 1
                    if after_pipe_pos < len(tokens) and tokens[after_pipe_pos][0] == 'IDENTIFIER' and tokens[after_pipe_pos][1] == var_name:
                        assign_pos = after_pipe_pos + 1
                        if assign_pos < len(tokens) and tokens[assign_pos][0] == 'ASSIGN' and tokens[assign_pos][1] == ':':
                            plugin_pos = assign_pos + 1
                            if plugin_pos < len(tokens) and tokens[plugin_pos][0] == 'IDENTIFIER':
                                plugin_name = tokens[plugin_pos][1]
                                plugin_assign_pos = plugin_pos + 1
                                if plugin_assign_pos < len(tokens) and tokens[plugin_assign_pos][0] == 'ASSIGN' and tokens[plugin_assign_pos][1] == ':':
                                    command_pos = plugin_assign_pos + 1
                                    if command_pos < len(tokens) and tokens[command_pos][0] == 'IDENTIFIER':
                                        command_name = tokens[command_pos][1]
                                        args_pos = command_pos + 1
                                        
                                        # Parse command arguments in angle brackets
                                        args_tokens = []
                                        if args_pos < len(tokens) and tokens[args_pos][0] == 'OPERATOR' and tokens[args_pos][1] == '<':
                                            current_arg_pos = args_pos + 1
                                            while current_arg_pos < len(tokens) and not (tokens[current_arg_pos][0] == 'OPERATOR' and tokens[current_arg_pos][1] == '>'):
                                                args_tokens.append(tokens[current_arg_pos])
                                                current_arg_pos += 1
                                            if current_arg_pos < len(tokens) and tokens[current_arg_pos][0] == 'OPERATOR' and tokens[current_arg_pos][1] == '>':
                                                current_arg_pos += 1
                                                return ('PLUGIN_ASSIGN', var_name, plugin_name, command_name, args_tokens), current_arg_pos
        
        if pos < len(tokens):
            token = tokens[pos]
            if token[0] == 'IDENTIFIER' and token[1] == 'sdebug':
                if pos + 1 < len(tokens) and tokens[pos + 1][0] == 'ASSIGN' and tokens[pos + 1][1] == ':':
                    if pos + 2 < len(tokens) and tokens[pos + 2][0] == 'IDENTIFIER' and tokens[pos + 2][1] in ['true', 'false']:
                        debug_value = tokens[pos + 2][1] == 'true'
                        return ('DEBUG', debug_value), pos + 3
        

        
        # 处理end语句
        if pos < len(tokens) and tokens[pos][0] == 'IDENTIFIER' and tokens[pos][1] == 'end':
            return ('END',), pos + 1
        
        # 直接处理sif、seif、sel和swhi语句
        if pos < len(tokens) and tokens[pos][0] == 'IDENTIFIER' and tokens[pos][1] == 'sif':
            current_pos = pos + 1  # Skip 'sif'
            
            # Find separator '|' for condition
            cond_end = current_pos
            while cond_end < len(tokens) and not (tokens[cond_end][0] == 'SEPARATOR' and tokens[cond_end][1] == '|'):
                cond_end += 1
            
            if cond_end >= len(tokens):
                return None, pos
            
            # Extract condition
            condition = tokens[current_pos:cond_end]
            current_pos = cond_end + 1  # Skip '|'
            
            # Parse if body
            if_body = []
            body_end = current_pos
            while body_end < len(tokens):
                token = tokens[body_end]
                if token[0] == 'IDENTIFIER' and token[1] in ['seif', 'sel', 'end']:
                    break
                stmt, new_pos = self.parse_statement(tokens, body_end)
                if stmt:
                    if_body.append(stmt)
                    body_end = new_pos
                else:
                    body_end += 1
            
            current_pos = body_end
            
            # Parse elif clauses
            elif_clauses = []
            while current_pos < len(tokens) and tokens[current_pos][0] == 'IDENTIFIER' and tokens[current_pos][1] == 'seif':
                current_pos += 1  # Skip 'seif'
                
                # Find separator '|' for elif condition
                elif_cond_end = current_pos
                while elif_cond_end < len(tokens) and not (tokens[elif_cond_end][0] == 'SEPARATOR' and tokens[elif_cond_end][1] == '|'):
                    elif_cond_end += 1
                
                if elif_cond_end >= len(tokens):
                    return None, pos
                
                # Extract elif condition
                elif_condition = tokens[current_pos:elif_cond_end]
                current_pos = elif_cond_end + 1  # Skip '|'
                
                # Parse elif body
                elif_body = []
                elif_body_end = current_pos
                while elif_body_end < len(tokens):
                    token = tokens[elif_body_end]
                    if token[0] == 'IDENTIFIER' and token[1] in ['seif', 'sel', 'end']:
                        break
                    stmt, new_pos = self.parse_statement(tokens, elif_body_end)
                    if stmt:
                        elif_body.append(stmt)
                        elif_body_end = new_pos
                    else:
                        elif_body_end += 1
                
                elif_clauses.append((elif_condition, elif_body))
                current_pos = elif_body_end
            
            # Parse else clause
            else_body = []
            if current_pos < len(tokens) and tokens[current_pos][0] == 'IDENTIFIER' and tokens[current_pos][1] == 'sel':
                current_pos += 1  # Skip 'sel'
                
                # Check for separator '|'
                if current_pos >= len(tokens) or not (tokens[current_pos][0] == 'SEPARATOR' and tokens[current_pos][1] == '|'):
                    return None, pos
                
                current_pos += 1  # Skip '|'
                
                # Parse else body
                else_body_end = current_pos
                while else_body_end < len(tokens):
                    token = tokens[else_body_end]
                    if token[0] == 'IDENTIFIER' and token[1] == 'end':
                        break
                    stmt, new_pos = self.parse_statement(tokens, else_body_end)
                    if stmt:
                        else_body.append(stmt)
                        else_body_end = new_pos
                    else:
                        else_body_end += 1
                
                current_pos = else_body_end
            
            # Check for end statement
            if current_pos >= len(tokens) or not (tokens[current_pos][0] == 'IDENTIFIER' and tokens[current_pos][1] == 'end'):
                return None, pos
            
            current_pos += 1  # Skip 'end'
            
            return ('IF_ELSE', condition, if_body, elif_clauses, else_body), current_pos
        
        # Handle while statement (swhi)
        elif pos < len(tokens) and tokens[pos][0] == 'IDENTIFIER' and tokens[pos][1] == 'swhi':
            current_pos = pos + 1  # Skip 'swhi'
            
            # Find separator '|' for condition
            cond_end = current_pos
            while cond_end < len(tokens) and not (tokens[cond_end][0] == 'SEPARATOR' and tokens[cond_end][1] == '|'):
                cond_end += 1
            
            if cond_end >= len(tokens):
                return None, pos
            
            # Extract condition
            condition = tokens[current_pos:cond_end]
            current_pos = cond_end + 1  # Skip '|'
            
            # Parse while body
            body = []
            body_end = current_pos
            while body_end < len(tokens):
                token = tokens[body_end]
                if token[0] == 'IDENTIFIER' and token[1] == 'end':
                    break
                stmt, new_pos = self.parse_statement(tokens, body_end)
                if stmt:
                    body.append(stmt)
                    body_end = new_pos
                else:
                    body_end += 1
            
            current_pos = body_end
            
            # Check for end statement
            if current_pos >= len(tokens) or not (tokens[current_pos][0] == 'IDENTIFIER' and tokens[current_pos][1] == 'end'):
                return None, pos
            
            current_pos += 1  # Skip 'end'
            
            return ('WHILE', condition, body), current_pos
        
        if pos < len(tokens):
            token = tokens[pos]
            if token[0] == 'IDENTIFIER':
                local_pos = pos + 1
                local_pos = self._skip_whitespace(tokens, local_pos)
                if local_pos < len(tokens) and tokens[local_pos][0] == 'OPERATOR' and tokens[local_pos][1] == '=':
                    local_pos += 1
                    local_pos = self._skip_whitespace(tokens, local_pos)
                    expr, new_pos = self.parse_expression(tokens, local_pos)
                    if expr:
                        return ('ASSIGNMENT', token[1], expr), new_pos
        
        # 然后调用siew插件，确保它能处理sif和swhile语句
        if 'siew' in self.plugins:
            stmt, new_pos = self.plugins['siew'].parse_statement(tokens, pos)
            if stmt:
                return stmt, new_pos
        
        # 最后调用其他插件
        if self.debug_mode:
            print(f"Debug: Available plugins: {list(self.plugins.keys())}")
        for plugin_name, plugin in self.plugins.items():
            if plugin_name != 'siew':
                if self.debug_mode:
                    print(f"Debug: Checking plugin {plugin_name}")
                if hasattr(plugin, 'parse_statement'):
                    if self.debug_mode:
                        print(f"Debug: Calling {plugin_name}.parse_statement at pos {pos}")
                    stmt, new_pos = plugin.parse_statement(tokens, pos)
                    if stmt:
                        if self.debug_mode:
                            print(f"Debug: {plugin_name} returned statement: {stmt}")
                        return stmt, new_pos
                    else:
                        if self.debug_mode:
                            print(f"Debug: {plugin_name} returned None")
                else:
                    if self.debug_mode:
                        print(f"Debug: {plugin_name} has no parse_statement method")
        return None, pos    
    def evaluate_condition(self, condition_tokens):
        """Evaluate a condition from tokens"""
        if len(condition_tokens) >= 3:
            left = condition_tokens[0]
            op = condition_tokens[1]
            right = condition_tokens[2]
            
            left_value = self.evaluate_expression(left)
            right_value = self.evaluate_expression(right)
            
            if op[1] == '>':
                return left_value > right_value
            elif op[1] == '<':
                return left_value < right_value
            elif op[1] == '==':
                return left_value == right_value
            elif op[1] == '!=':
                return left_value != right_value
            elif op[1] == '>=':
                return left_value >= right_value
            elif op[1] == '<=':
                return left_value <= right_value
            elif op[1] == '&':
                return left_value and right_value
            elif op[1] == '|':
                return left_value or right_value
        return False
    
    def evaluate_expression(self, expr):
        """Evaluate an expression (optimized with caching)"""
        # 检查缓存
        expr_key = str(expr)
        if expr_key in self.expression_cache:
            return self.expression_cache[expr_key]
        
        result = 0
        if isinstance(expr, list):
            if len(expr) == 3 and expr[1][0] == 'OPERATOR':
                # 递归评估左右操作数
                left = self.evaluate_expression(expr[0])
                op = expr[1][1]
                right = self.evaluate_expression(expr[2])
                
                # 使用快速操作映射
                if op in self.operation_map:
                    result = self.operation_map[op](left, right)
        
        elif expr[0] == 'STRING':
            result = expr[1]
        elif expr[0] == 'NUMBER':
            # 快速数字转换
            num_str = expr[1]
            try:
                if '.' in num_str:
                    result = float(num_str)
                else:
                    result = int(num_str)
            except (ValueError, TypeError):
                result = 0
        elif expr[0] == 'IDENTIFIER':
            # 快速变量查找
            result = self.variables.get(expr[1], 0)
        elif expr[0] == 'FUNCTION_CALL':
            # 处理函数调用
            func_name = expr[1]
            args = expr[2]
            
            # 评估参数
            evaluated_args = []
            for arg in args:
                evaluated_args.append(self.evaluate_expression(arg))
            
            # 快速插件查找
            for plugin in self.plugins.values():
                if hasattr(plugin, 'execute_statement'):
                    plugin_result = plugin.execute_statement(('FUNCTION_CALL', func_name, evaluated_args))
                    # 检查结果是否不是布尔值 - 这意味着函数返回了一个值
                    if not isinstance(plugin_result, bool):
                        result = plugin_result
                        break
        
        # 缓存结果
        self.expression_cache[expr_key] = result
        # 管理缓存大小
        self._manage_cache(self.expression_cache)
        
        return result
    
    def execute_statement(self, stmt):
        """Execute a statement"""
        # 检查是否是debug语句
        if stmt[0] == 'DEBUG':
            # 设置debug模式
            self.debug_mode = stmt[1]
            # 打印debug信息
            print(f"Debug mode: {self.debug_mode}")
            return True
        
        # 直接执行PRINT语句，不依赖basic插件
        if stmt[0] == 'PRINT':
            value = self.evaluate_expression(stmt[1])
            print(value)
            return True
        

        
        # 处理END语句
        if stmt[0] == 'END':
            return True
        
        # 处理IF_ELSE语句
        if stmt[0] == 'IF_ELSE':
            if_condition = stmt[1]
            if_body = stmt[2]
            elif_clauses = stmt[3]
            else_body = stmt[4]
            
            if self.evaluate_condition(if_condition):
                for body_stmt in if_body:
                    self.execute_statement(body_stmt)
                return True
            
            for elif_condition, elif_body in elif_clauses:
                if self.evaluate_condition(elif_condition):
                    for body_stmt in elif_body:
                        self.execute_statement(body_stmt)
                    return True
            
            if else_body:
                for body_stmt in else_body:
                    self.execute_statement(body_stmt)
            
            return True
        
        # 处理WHILE语句
        elif stmt[0] == 'WHILE':
            condition_tokens = stmt[1]
            body = stmt[2]
            
            while self.evaluate_condition(condition_tokens):
                for body_stmt in body:
                    self.execute_statement(body_stmt)
            
            return True
        
        # 执行赋值语句
        if stmt[0] == 'ASSIGNMENT':
            var_name = stmt[1]
            value = self.evaluate_expression(stmt[2])
            self.variables[var_name] = value
            if self.debug_mode:
                print(f"Debug: Assigned {value} to variable {var_name}")
            return True
        
        # 处理插件赋值语句: set var | var : plugin : command<args>
        if stmt[0] == 'PLUGIN_ASSIGN':
            var_name = stmt[1]
            plugin_name = stmt[2]
            command_name = stmt[3]
            args_tokens = stmt[4]
            
            # Check if plugin exists
            if plugin_name not in self.plugins:
                print(f"Error: Plugin '{plugin_name}' not found")
                return False
            
            plugin = self.plugins[plugin_name]
            
            # Create a statement that the plugin can understand
            plugin_stmt = None
            
            # For math plugin
            if plugin_name == 'math':
                plugin_stmt = ('MATH', command_name, args_tokens)
            # For string plugin
            elif plugin_name == 'string':
                plugin_stmt = ('STRING_OP', command_name, args_tokens)
            # For crypto plugin
            elif plugin_name == 'crypto':
                plugin_stmt = ('CRYPTO_OP', command_name, args_tokens)
            # For unit plugin
            elif plugin_name == 'unit':
                plugin_stmt = ('UNIT_CONVERT', command_name, args_tokens)
            # For request plugin
            elif plugin_name == 'request':
                plugin_stmt = ('REQUEST', command_name.upper(), args_tokens)
            # For json plugin
            elif plugin_name == 'json':
                plugin_stmt = ('JSON_OP', command_name, args_tokens)
            # For color plugin
            elif plugin_name == 'color':
                # Color plugin doesn't return values, it just prints
                return plugin.execute_statement(('COLOR_OUTPUT', args_tokens[0], args_tokens[2])) if len(args_tokens) >= 3 else False
            
            if plugin_stmt:
                # Create a temporary variable to capture the result
                temp_result = None
                
                # Override print for this execution to capture the result
                import builtins
                original_print = builtins.print
                
                def capture_print(*args, **kwargs):
                    nonlocal temp_result
                    temp_result = ' '.join(map(str, args))
                    original_print(*args, **kwargs)
                
                builtins.print = capture_print
                
                # Execute the plugin statement
                try:
                    success = plugin.execute_statement(plugin_stmt)
                finally:
                    # Restore original print
                    builtins.print = original_print
                
                if success and temp_result is not None:
                    # Try to convert to appropriate type
                    try:
                        if '.' in temp_result:
                            result_value = float(temp_result)
                        else:
                            result_value = int(temp_result)
                    except ValueError:
                        # Keep as string
                        result_value = temp_result
                    
                    # Assign the result to the variable
                    self.variables[var_name] = result_value
                    if self.debug_mode:
                        print(f"Debug: Assigned plugin result '{result_value}' to variable '{var_name}'")
                    return True
            
            print(f"Error: Failed to execute plugin assignment for '{var_name}'")
            return False
        
        # 优先调用siew插件，确保它能处理IF、IF_ELSE和WHILE语句
        if 'siew' in self.plugins:
            if self.plugins['siew'].execute_statement(stmt):
                return True
        
        # 然后调用其他插件
        for plugin_name, plugin in self.plugins.items():
            if plugin_name != 'siew' and hasattr(plugin, 'execute_statement'):
                if plugin.execute_statement(stmt):
                    return True
        return False
    
    def execute(self, code, file_path=None):
        """Execute the given SCL code (optimized with caching and efficient processing)"""
        # 检查缓存
        code_hash = hash(code)
        if code_hash in self.code_block_cache:
            return self.code_block_cache[code_hash]
        
        def smart_split(code):
            """Optimized line splitting that handles strings correctly"""
            # 快速处理
            code_len = len(code)
            if code_len == 0:
                return []
            
            # 预分配空间
            lines = []
            current_line = []
            in_string = False
            
            for char in code:
                if char == '"':
                    in_string = not in_string
                    current_line.append(char)
                elif char == '\n' and not in_string:
                    lines.append(''.join(current_line))
                    current_line = []
                else:
                    current_line.append(char)
            
            if current_line:
                lines.append(''.join(current_line))
            
            return lines
        
        lines = smart_split(code)
        if not lines:
            self.code_block_cache[code_hash] = True
            return True
        
        # 用于处理多行语句
        multi_line_buffer = []
        in_multi_line = False
        nested_level = 0  # 用于跟踪嵌套级别
        
        for line_num, line in enumerate(lines, 1):
            # 快速跳过空行和注释
            if self.empty_pattern.match(line) or self.comment_pattern.match(line):
                continue
            
            # 处理插件导入和SCL文件导入
            if line.startswith('simp{') and line.endswith('}'):
                import_content = line[5:-1].strip()
                
                # 检查是否是SCL文件导入: simp{scl : 路径}
                if import_content.startswith('scl :'):
                    scl_path = import_content[5:].strip()
                    if not self.import_scl_file(scl_path, line_num):
                        self.code_block_cache[code_hash] = False
                        return False
                else:
                    # 插件导入
                    if not self.load_plugin(import_content):
                        print(f"Error at line {line_num}: Failed to load plugin {import_content}")
                        print(f"Code: {line}")
                        self.code_block_cache[code_hash] = False
                        return False
                continue
            
            try:
                # 检查是否是多行语句的开始
                is_multi_line_start = False
                for prefix in self.multi_line_starts:
                    if line.startswith(prefix):
                        is_multi_line_start = True
                        break
                
                # 特殊处理 sde 语句
                if not is_multi_line_start and line.startswith('sde ') and line.endswith(' :'):
                    is_multi_line_start = True
                
                if is_multi_line_start:
                    multi_line_buffer.append(line)
                    if not in_multi_line:
                        in_multi_line = True
                        nested_level = 1  # 开始一个新的多行语句，嵌套级别为1
                    else:
                        nested_level += 1  # 遇到新的嵌套语句，嵌套级别加1
                # 检查是否是多行语句的结束
                elif line == 'end' and in_multi_line:
                    multi_line_buffer.append(line)
                    nested_level -= 1  # 遇到end，嵌套级别减1
                    if nested_level == 0:
                        # 嵌套级别为0，说明是外部语句的结束
                        in_multi_line = False
                        # 处理完整的多行语句
                        multi_line_code = '\n'.join(multi_line_buffer)
                        multi_line_buffer = []
                        # 处理多行语句
                        tokens = self.tokenize(multi_line_code)
                        if tokens:
                            stmt, _ = self.parse_statement(tokens, 0)
                            if stmt:
                                if not self.execute_statement(stmt):
                                    print(f"Error at line {line_num}: Failed to execute statement")
                                    print(f"Code: {multi_line_code}")
                                    self.code_block_cache[code_hash] = False
                                    return False
                            else:
                                print(f"Error at line {line_num}: Invalid syntax")
                                print(f"Code: {multi_line_code}")
                                self.code_block_cache[code_hash] = False
                                return False
                # 处理多行语句的中间部分
                elif in_multi_line:
                    multi_line_buffer.append(line)
                    # 检查是否是新的嵌套语句的开始
                    if line.startswith('sif :') or line.startswith('swhile :'):
                        nested_level += 1  # 遇到新的嵌套语句，嵌套级别加1
                # 处理单行语句
                else:
                    # 使用原始的line，不移除空白字符
                    tokens = self.tokenize(line)
                    if tokens:
                        stmt, _ = self.parse_statement(tokens, 0)
                        if stmt:
                            if not self.execute_statement(stmt):
                                print(f"Error at line {line_num}: Failed to execute statement")
                                print(f"Code: {line}")
                                self.code_block_cache[code_hash] = False
                                return False
                        else:
                            print(f"Error at line {line_num}: Invalid syntax")
                            print(f"Code: {line}")
                            self.code_block_cache[code_hash] = False
                            return False
            except Exception as e:
                print(f"Error at line {line_num}: {e}")
                print(f"Code: {line}")
                import traceback
                traceback.print_exc()
                self.code_block_cache[code_hash] = False
                return False
        
        # 检查是否有未完成的多行语句
        if in_multi_line:
            print(f"Error at line {line_num}: Unclosed multi-line statement")
            print(f"Code: {''.join(multi_line_buffer)}")
            self.code_block_cache[code_hash] = False
            return False
        
        # 缓存结果
        self.code_block_cache[code_hash] = True
        # 管理缓存大小
        self._manage_cache(self.code_block_cache)
        
        return True

def nano_editor(file_path=None):
    """仿nano的终端文本编辑器"""
    import shutil
    
    # 获取终端大小
    def get_terminal_size():
        return shutil.get_terminal_size()
    
    # 清屏
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    # 读取文件内容
    lines = []
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.read().split('\n')
        except:
            lines = ['']
    else:
        lines = ['']
    
    # 确保至少有一行
    if not lines:
        lines = ['']
    
    # 编辑器状态
    cursor_x = 0
    cursor_y = 0
    scroll_y = 0
    modified = False
    filename = file_path if file_path else "New File"
    
    # 隐藏光标（Windows）
    if os.name == 'nt':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        # 禁用行输入和回显
        mode = ctypes.c_uint32()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        kernel32.SetConsoleMode(handle, mode.value & ~0x0004 & ~0x0002)
    
    def draw_editor():
        """绘制编辑器界面"""
        clear_screen()
        term_width, term_height = get_terminal_size()
        
        # 标题栏
        title = f" SCL Nano Editor - {filename}"
        if modified:
            title += " [Modified]"
        title = title[:term_width].ljust(term_width)
        print(f"\033[7m{title}\033[0m")
        
        # 编辑区域
        edit_height = term_height - 3
        for i in range(edit_height):
            line_idx = scroll_y + i
            if line_idx < len(lines):
                line = lines[line_idx]
                # 显示行号
                line_num = str(line_idx + 1).rjust(4)
                # 截断行内容以适应屏幕
                content = line[:term_width - 6]
                content = content.ljust(term_width - 6)
                
                # 高亮当前行
                if line_idx == cursor_y:
                    print(f"\033[7m{line_num}\033[0m {content}")
                else:
                    print(f"{line_num} {content}")
            else:
                print("~".ljust(term_width))
        
        # 状态栏
        status = f" Line {cursor_y + 1}/{len(lines)}, Col {cursor_x + 1} | Ctrl+S=Save, Ctrl+X=Exit, Ctrl+O=Open, Ctrl+R=Run"
        status = status[:term_width].ljust(term_width)
        print(f"\033[7m{status}\033[0m")
        
        # 移动光标到正确位置
        cursor_screen_y = cursor_y - scroll_y + 1
        # 光标位置 = 行号宽度(5) + cursor_x + 1
        # 行号占4位 + 1个空格 = 5，内容从第6列开始
        # cursor_x=0 时，光标应在第6列（内容的第1个字符）
        cursor_screen_x = 5 + cursor_x + 1
        # 限制在屏幕范围内
        cursor_screen_x = min(cursor_screen_x, term_width)
        print(f"\033[{cursor_screen_y + 1};{cursor_screen_x}H", end='', flush=True)
    
    def save_file():
        """保存文件"""
        nonlocal modified, filename
        if not filename or filename == "New File":
            # 提示输入文件名
            term_width, term_height = get_terminal_size()
            prompt = "Filename to write: "
            print(f"\033[{term_height};1H\033[0K{prompt}", end='', flush=True)
            
            # 简单输入文件名
            new_filename = input()
            if new_filename:
                filename = new_filename
            else:
                return False
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            modified = False
            return True
        except Exception as e:
            term_width, term_height = get_terminal_size()
            print(f"\033[{term_height};1H\033[0KError saving: {e}", end='', flush=True)
            input(" Press Enter to continue...")
            return False
    
    def open_file():
        """打开文件"""
        nonlocal lines, cursor_x, cursor_y, scroll_y, modified, filename
        term_width, term_height = get_terminal_size()
        prompt = "Filename to open: "
        print(f"\033[{term_height};1H\033[0K{prompt}", end='', flush=True)
        
        new_filename = input()
        if new_filename and os.path.exists(new_filename):
            try:
                with open(new_filename, 'r', encoding='utf-8') as f:
                    lines = f.read().split('\n')
                if not lines:
                    lines = ['']
                filename = new_filename
                cursor_x = 0
                cursor_y = 0
                scroll_y = 0
                modified = False
                return True
            except Exception as e:
                print(f"\033[{term_height};1H\033[0KError opening: {e}", end='', flush=True)
                input(" Press Enter to continue...")
        return False
    
    # 主循环
    try:
        while True:
            draw_editor()
            
            # 读取按键
            if os.name == 'nt':
                import msvcrt
                key = msvcrt.getch()
                
                # 处理特殊键
                if key == b'\x00' or key == b'\xe0':
                    key = msvcrt.getch()
                    if key == b'H':  # 上箭头
                        if cursor_y > 0:
                            cursor_y -= 1
                            cursor_x = min(cursor_x, len(lines[cursor_y]) if lines[cursor_y] else 0)
                    elif key == b'P':  # 下箭头
                        if cursor_y < len(lines) - 1:
                            cursor_y += 1
                            cursor_x = min(cursor_x, len(lines[cursor_y]) if lines[cursor_y] else 0)
                    elif key == b'K':  # 左箭头
                        if cursor_x > 0:
                            cursor_x -= 1
                    elif key == b'M':  # 右箭头
                        if cursor_x < len(lines[cursor_y]):
                            cursor_x += 1
                elif key == b'\x13':  # Ctrl+S
                    save_file()
                elif key == b'\x18':  # Ctrl+X
                    if modified:
                        term_width, term_height = get_terminal_size()
                        print(f"\033[{term_height};1H\033[0KSave modified buffer? (Y/N/C)", end='', flush=True)
                        response = input().upper()
                        if response == 'Y':
                            if save_file():
                                break
                        elif response == 'N':
                            break
                    else:
                        break
                elif key == b'\x0f':  # Ctrl+O
                    open_file()
                elif key == b'\x12':  # Ctrl+R - 运行文件
                    if filename and filename != "New File":
                        # 先保存文件
                        if modified:
                            save_file()
                        # 退出编辑器并运行文件
                        clear_screen()
                        print(f"Running {filename}...")
                        print("=" * 50)
                        # 创建解释器并执行
                        interpreter = SCLInterpreter()
                        try:
                            with open(filename, 'r', encoding='utf-8') as f:
                                code = f.read()
                            interpreter.execute(code, filename)
                        except Exception as e:
                            print(f"Error: {e}")
                        print("=" * 50)
                        print("Press any key to return to editor...")
                        msvcrt.getch()
                    else:
                        # 提示先保存文件
                        term_width, term_height = get_terminal_size()
                        print(f"\033[{term_height};1H\033[0KPlease save file first (Ctrl+S)", end='', flush=True)
                        msvcrt.getch()
                elif key == b'\r':  # Enter
                    # 在当前位置分割行
                    current_line = lines[cursor_y]
                    lines.insert(cursor_y + 1, current_line[cursor_x:])
                    lines[cursor_y] = current_line[:cursor_x]
                    cursor_y += 1
                    cursor_x = 0
                    modified = True
                elif key == b'\x08':  # Backspace
                    if cursor_x > 0:
                        lines[cursor_y] = lines[cursor_y][:cursor_x-1] + lines[cursor_y][cursor_x:]
                        cursor_x -= 1
                        modified = True
                    elif cursor_y > 0:
                        # 合并到上一行
                        cursor_x = len(lines[cursor_y - 1])
                        lines[cursor_y - 1] += lines[cursor_y]
                        del lines[cursor_y]
                        cursor_y -= 1
                        modified = True
                elif key == b'\x7f':  # Delete
                    if cursor_x < len(lines[cursor_y]):
                        lines[cursor_y] = lines[cursor_y][:cursor_x] + lines[cursor_y][cursor_x+1:]
                        modified = True
                    elif cursor_y < len(lines) - 1:
                        # 合并下一行
                        lines[cursor_y] += lines[cursor_y + 1]
                        del lines[cursor_y + 1]
                        modified = True
                elif key == b'"':  # 双引号
                    lines[cursor_y] = lines[cursor_y][:cursor_x] + '"' + lines[cursor_y][cursor_x:]
                    cursor_x += 1
                    modified = True
                elif key == b"'":  # 单引号
                    lines[cursor_y] = lines[cursor_y][:cursor_x] + "'" + lines[cursor_y][cursor_x:]
                    cursor_x += 1
                    modified = True
                elif key >= b' ' and key <= b'~':  # 其他可打印字符
                    try:
                        char = key.decode('utf-8')
                    except:
                        char = key.decode('ascii', errors='replace')
                    lines[cursor_y] = lines[cursor_y][:cursor_x] + char + lines[cursor_y][cursor_x:]
                    cursor_x += 1
                    modified = True
            else:
                # Linux/Mac 使用简单输入
                import tty
                import termios
                import select
                
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    key = sys.stdin.read(1)
                    
                    if key == '\x13':  # Ctrl+S
                        save_file()
                    elif key == '\x18':  # Ctrl+X
                        if modified:
                            print("\nSave modified buffer? (Y/N/C)")
                            response = input().upper()
                            if response == 'Y':
                                if save_file():
                                    break
                            elif response == 'N':
                                break
                        else:
                            break
                    elif key == '\x0f':  # Ctrl+O
                        open_file()
                    elif key == '\x12':  # Ctrl+R - 运行文件
                        if filename and filename != "New File":
                            # 先保存文件
                            if modified:
                                save_file()
                            # 退出编辑器并运行文件
                            clear_screen()
                            print(f"Running {filename}...")
                            print("=" * 50)
                            # 创建解释器并执行
                            interpreter = SCLInterpreter()
                            try:
                                with open(filename, 'r', encoding='utf-8') as f:
                                    code = f.read()
                                interpreter.execute(code, filename)
                            except Exception as e:
                                print(f"Error: {e}")
                            print("=" * 50)
                            print("Press any key to return to editor...")
                            sys.stdin.read(1)
                        else:
                            # 提示先保存文件
                            term_width, term_height = get_terminal_size()
                            print(f"\033[{term_height};1H\033[0KPlease save file first (Ctrl+S)")
                            sys.stdin.read(1)
                    elif key == '\r':  # Enter
                        current_line = lines[cursor_y]
                        lines.insert(cursor_y + 1, current_line[cursor_x:])
                        lines[cursor_y] = current_line[:cursor_x]
                        cursor_y += 1
                        cursor_x = 0
                        modified = True
                    elif key == '\x7f':  # Backspace
                        if cursor_x > 0:
                            lines[cursor_y] = lines[cursor_y][:cursor_x-1] + lines[cursor_y][cursor_x:]
                            cursor_x -= 1
                            modified = True
                    elif key == '"' or key == "'":  # 引号
                        lines[cursor_y] = lines[cursor_y][:cursor_x] + key + lines[cursor_y][cursor_x:]
                        cursor_x += 1
                        modified = True
                    elif ord(key) >= 32 and ord(key) <= 126:  # 其他可打印字符
                        lines[cursor_y] = lines[cursor_y][:cursor_x] + key + lines[cursor_y][cursor_x:]
                        cursor_x += 1
                        modified = True
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
            # 调整滚动位置
            term_width, term_height = get_terminal_size()
            edit_height = term_height - 3
            if cursor_y < scroll_y:
                scroll_y = cursor_y
            elif cursor_y >= scroll_y + edit_height:
                scroll_y = cursor_y - edit_height + 1
    
    finally:
        # 恢复光标（Windows）
        if os.name == 'nt':
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            kernel32.SetConsoleMode(handle, mode.value | 0x0004 | 0x0002)
        
        clear_screen()
        print(f"Exited nano editor. File: {filename}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python scl.py <file.scl>")
        print("       python scl.py -nano [file.scl]  # Open nano editor")
        sys.exit(1)
    
    # 检查是否是nano编辑器模式
    if sys.argv[1] == '-nano':
        file_path = sys.argv[2] if len(sys.argv) > 2 else None
        nano_editor(file_path)
        sys.exit(0)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    
    interpreter = SCLInterpreter()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        success = interpreter.execute(code, file_path)
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"Error executing file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

