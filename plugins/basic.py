# Basic syntax plugin for SunsetCodeLang
import requests

class BasicPlugin:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        # 预定义的颜色名称映射到ANSI转义码
        self.color_names = {
            # 基础颜色
            'black': '30',
            'red': '31',
            'green': '32',
            'yellow': '33',
            'blue': '34',
            'magenta': '35',
            'cyan': '36',
            'white': '37',
            # 亮色
            'bright_black': '90',
            'bright_red': '91',
            'bright_green': '92',
            'bright_yellow': '93',
            'bright_blue': '94',
            'bright_magenta': '95',
            'bright_cyan': '96',
            'bright_white': '97'
        }
        # 类和函数定义
        self.classes = {}
        self.functions = {}
        # 用于解析的辅助变量
        self.tokens = []
        self.current_pos = 0
    
    def consume(self):
        """Consume and return the current token"""
        if self.current_pos < len(self.tokens):
            token = self.tokens[self.current_pos]
            self.current_pos += 1
            return token
        return None
    
    def peek(self, offset=0):
        """Peek at the token at the given offset without consuming it"""
        if self.current_pos + offset < len(self.tokens):
            return self.tokens[self.current_pos + offset]
        return None
    
    def register_syntax(self):
        """Register basic syntax handlers"""
        # This will be called by the interpreter to register syntax handlers
        pass
    
    def parse_statement(self, tokens, pos):
        """Parse basic statements"""
        # 不修改全局状态，使用局部变量
        local_pos = pos
        
        def peek(offset=0):
            if local_pos + offset < len(tokens):
                return tokens[local_pos + offset]
            return None
        
        def consume():
            nonlocal local_pos
            if local_pos < len(tokens):
                token = tokens[local_pos]
                local_pos += 1
                return token
            return None
        
        token = peek()
        if not token:
            return None, pos
        

        
        if token[0] == 'IDENTIFIER' and token[1] == 'set':
            # Variable declaration: set a | a : 1
            consume()  # Consume 'set'
            var_name = consume()[1]  # Get variable name
            if peek() and peek()[0] == 'SEPARATOR':
                consume()  # Consume '|'
                # Check if next is the same variable for assignment
                if peek() and peek()[0] == 'IDENTIFIER' and peek()[1] == var_name:
                    consume()  # Consume variable name
                    if peek() and peek()[0] == 'ASSIGN':
                        consume()  # Consume ':'
                        expr, new_pos = self.interpreter.parse_expression(tokens, local_pos)
                        if expr:
                            local_pos = new_pos
                            return ('ASSIGN', var_name, expr), local_pos
        elif token[0] == 'IDENTIFIER' and token[1] == 'sout':
            # Print statement: sout : "Hello World!"
            consume()  # Consume 'sout'
            if peek() and peek()[0] == 'ASSIGN':
                # Handle sout : "Hello World!"
                consume()  # Consume ':'
                # 使用 parse_expression 解析完整的表达式
                expr, new_pos = self.interpreter.parse_expression(tokens, local_pos)
                if expr:
                    local_pos = new_pos
                    return ('PRINT', expr), local_pos
        elif token[0] == 'IDENTIFIER' and token[1] == 'soutc':
            # Color print statement: soutc : color : text
            consume()  # Consume 'soutc'
            if peek() and peek()[0] == 'ASSIGN':
                consume()  # Consume ':'
                
                # Get color specification
                color_token = consume()
                if not color_token:
                    return None, pos
                
                # Check for another colon before text
                if not (peek() and peek()[0] == 'ASSIGN'):
                    return None, pos
                
                consume()  # Consume ':'
                
                # 使用 parse_expression 解析完整的文本表达式
                text_expr, new_pos = self.interpreter.parse_expression(tokens, local_pos)
                if text_expr:
                    local_pos = new_pos
                    return ('COLOR_OUTPUT', color_token, text_expr), local_pos
        elif token[0] == 'IDENTIFIER' and token[1] == 'start':
            # Run another SCL file: start : "file.scl"
            consume()  # Consume 'start'
            if peek() and peek()[0] == 'ASSIGN':
                # Handle start : "file.scl"
                consume()  # Consume ':'
                # 直接获取下一个令牌作为文件路径
                if local_pos < len(tokens):
                    file_path = tokens[local_pos]
                    local_pos += 1
                    return ('START', file_path), local_pos
        elif token[0] == 'IDENTIFIER' and token[1] == 'sif':
            # If statement: sif condition | ...
            consume()  # Consume 'sif'
            
            # Find separator '|' for condition
            cond_end = local_pos
            while cond_end < len(tokens) and not (tokens[cond_end][0] == 'SEPARATOR' and tokens[cond_end][1] == '|'):
                cond_end += 1
            
            if cond_end >= len(tokens):
                return None, pos
            
            # Extract condition
            condition = tokens[local_pos:cond_end]
            local_pos = cond_end + 1  # Skip '|'
            
            # Parse if body
            if_body = []
            body_end = local_pos
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
            
            local_pos = body_end
            
            # Parse elif clauses
            elif_clauses = []
            while local_pos < len(tokens) and tokens[local_pos][0] == 'IDENTIFIER' and tokens[local_pos][1] == 'seif':
                local_pos += 1  # Skip 'seif'
                
                # Find separator '|' for elif condition
                elif_cond_end = local_pos
                while elif_cond_end < len(tokens) and not (tokens[elif_cond_end][0] == 'SEPARATOR' and tokens[elif_cond_end][1] == '|'):
                    elif_cond_end += 1
                
                if elif_cond_end >= len(tokens):
                    return None, pos
                
                # Extract elif condition
                elif_condition = tokens[local_pos:elif_cond_end]
                local_pos = elif_cond_end + 1  # Skip '|'
                
                # Parse elif body
                elif_body = []
                elif_body_end = local_pos
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
                local_pos = elif_body_end
            
            # Parse else clause
            else_body = []
            if local_pos < len(tokens) and tokens[local_pos][0] == 'IDENTIFIER' and tokens[local_pos][1] == 'sel':
                local_pos += 1  # Skip 'sel'
                
                # Check for separator '|'
                if local_pos >= len(tokens) or not (tokens[local_pos][0] == 'SEPARATOR' and tokens[local_pos][1] == '|'):
                    return None, pos
                
                local_pos += 1  # Skip '|'
                
                # Parse else body
                else_body_end = local_pos
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
                
                local_pos = else_body_end
            
            # Check for end statement
            if local_pos >= len(tokens) or not (tokens[local_pos][0] == 'IDENTIFIER' and tokens[local_pos][1] == 'end'):
                return None, pos
            
            local_pos += 1  # Skip 'end'
            
            return ('IF_ELSE', condition, if_body, elif_clauses, else_body), local_pos
        elif token[0] == 'IDENTIFIER' and token[1] == 'swhi':
            # While statement: swhi condition | ...
            consume()  # Consume 'swhi'
            
            # Find separator '|' for condition
            cond_end = local_pos
            while cond_end < len(tokens) and not (tokens[cond_end][0] == 'SEPARATOR' and tokens[cond_end][1] == '|'):
                cond_end += 1
            
            if cond_end >= len(tokens):
                return None, pos
            
            # Extract condition
            condition = tokens[local_pos:cond_end]
            local_pos = cond_end + 1  # Skip '|'
            
            # Parse while body
            body = []
            body_end = local_pos
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
            
            local_pos = body_end
            
            # Check for end statement
            if local_pos >= len(tokens) or not (tokens[local_pos][0] == 'IDENTIFIER' and tokens[local_pos][1] == 'end'):
                return None, pos
            
            local_pos += 1  # Skip 'end'
            
            return ('WHILE', condition, body), local_pos
        elif token[0] == 'IDENTIFIER' and token[1] == 'break':
            # Break statement: break
            consume()  # Consume 'break'
            return ('BREAK',), local_pos
        elif token[0] == 'IDENTIFIER' and token[1] == 'sde':
            # Function definition or call: sde add : ... end or sde run<add>
         
            consume()  # Consume 'sde'
            
            # Check for function call: sde run<add>
            next_token = peek()

            if next_token and next_token[0] == 'IDENTIFIER' and next_token[1] == 'run':

                consume()  # Consume 'run'
                # Check for <function_name>

                if peek() and peek()[0] == 'OPERATOR' and peek()[1] == '<':

                    consume()  # Consume '<'
                    func_token = peek()

                    if func_token and func_token[0] == 'IDENTIFIER':
                        func_name = func_token[1]

                        consume()  # Consume function name

                        if peek() and peek()[0] == 'OPERATOR' and peek()[1] == '>':

                            consume()  # Consume '>'

                            return ('FUNCTION_CALL', func_name), local_pos

            
            # Check for function definition: sde add :
            func_token = peek()
            if not func_token or func_token[0] != 'IDENTIFIER':
                return None, pos
            func_name = func_token[1]
            consume()  # Consume function name
            
            # Check for assignment operator
            assign_token = peek()
            if not assign_token or assign_token[0] != 'ASSIGN':
                return None, pos
            consume()  # Consume ':'
            
            # Get function body until 'end'
            body_tokens = []
            while local_pos < len(tokens):
                current_token = tokens[local_pos]
                if current_token[0] == 'IDENTIFIER' and current_token[1] == 'end':
                    break
                body_tokens.append(current_token)
                local_pos += 1
            
            # Check for 'end'
            if local_pos < len(tokens) and tokens[local_pos][0] == 'IDENTIFIER' and tokens[local_pos][1] == 'end':
                consume()  # Consume 'end'
                return ('FUNCTION_DEF', func_name, body_tokens), local_pos
            return None, pos
        # Check for function definition: sdef < name > [ params ] : ...
        elif token[0] == 'IDENTIFIER' and token[1] == 'sdef':
            if pos + 3 < len(tokens):
                if (tokens[pos + 1][0] == 'OPERATOR' and tokens[pos + 1][1] == '<' and
                    tokens[pos + 2][0] == 'IDENTIFIER' and
                    tokens[pos + 3][0] == 'OPERATOR' and tokens[pos + 3][1] == '>'):
                    
                    func_name = tokens[pos + 2][1]  # Extract name
                    local_pos = pos + 4
                    
                    # Check for parameters: [ param1 , param2 , ... ]
                    params = []
                    if local_pos < len(tokens) and tokens[local_pos][0] == 'PAREN' and tokens[local_pos][1] == '[':
                        local_pos += 1
                        # Parse parameters
                        while local_pos < len(tokens) and not (tokens[local_pos][0] == 'PAREN' and tokens[local_pos][1] == ']'):
                            if tokens[local_pos][0] == 'IDENTIFIER':
                                params.append(tokens[local_pos][1])
                            elif tokens[local_pos][0] == 'SEPARATOR' and tokens[local_pos][1] == ',':
                                pass  # Skip comma
                            local_pos += 1
                        if local_pos < len(tokens) and tokens[local_pos][0] == 'PAREN' and tokens[local_pos][1] == ']':
                            local_pos += 1
                    
                    # Check for assignment operator
                    if local_pos < len(tokens) and tokens[local_pos][0] == 'ASSIGN' and tokens[local_pos][1] == ':':
                        local_pos += 1
                        
                        # Collect body tokens until 'end'
                        body_tokens = []
                        while local_pos < len(tokens):
                            current_token = tokens[local_pos]
                            if current_token[0] == 'IDENTIFIER' and current_token[1] == 'end':
                                local_pos += 1
                                break
                            body_tokens.append(current_token)
                            local_pos += 1
                        
                        return ('FUNCTION_DEF', func_name, params, body_tokens), local_pos
        # Check for class definition: sclass < name > : ...
        elif token[0] == 'IDENTIFIER' and token[1] == 'sclass':
            if pos + 3 < len(tokens):
                if (tokens[pos + 1][0] == 'OPERATOR' and tokens[pos + 1][1] == '<' and
                    tokens[pos + 2][0] == 'IDENTIFIER' and
                    tokens[pos + 3][0] == 'OPERATOR' and tokens[pos + 3][1] == '>'):
                    
                    class_name = tokens[pos + 2][1]  # Extract name
                    local_pos = pos + 4
                    
                    # Check for assignment operator
                    if local_pos < len(tokens) and tokens[local_pos][0] == 'ASSIGN' and tokens[local_pos][1] == ':':
                        local_pos += 1
                        
                        # Collect body tokens until 'end' (class end)
                        body_tokens = []
                        end_count = 0
                        while local_pos < len(tokens):
                            current_token = tokens[local_pos]
                            if current_token[0] == 'IDENTIFIER' and current_token[1] == 'smethod':
                                # 遇到新的方法定义，增加 end 计数
                                end_count += 1
                            elif current_token[0] == 'IDENTIFIER' and current_token[1] == 'end':
                                # 遇到 end 语句
                                end_count -= 1
                                # 如果 end_count 为 -1，说明是类的结束
                                if end_count == -1:
                                    local_pos += 1
                                    break
                            body_tokens.append(current_token)
                            local_pos += 1
                        
                        return ('CLASS_DEF', class_name, body_tokens), local_pos
        # Check for dcd run command: dcd : run : function_name : [params]
        elif token[0] == 'IDENTIFIER' and token[1] == 'dcd':
            # Handle dcd run command
            consume()  # Consume 'dcd'
            
            # Check for ':'
            next_token = peek()
            if not (next_token and next_token[0] == 'ASSIGN' and next_token[1] == ':'):
                return None, pos
            consume()  # Consume ':'
            
            # Check for 'run'
            next_token = peek()
            if not (next_token and next_token[0] == 'IDENTIFIER' and next_token[1] == 'run'):
                return None, pos
            consume()  # Consume 'run'
            
            # Check for ':'
            next_token = peek()
            if not (next_token and next_token[0] == 'ASSIGN' and next_token[1] == ':'):
                return None, pos
            consume()  # Consume ':'
            
            # Get function name
            func_token = peek()
            if not (func_token and func_token[0] == 'IDENTIFIER'):
                return None, pos
            func_name = func_token[1]
            consume()  # Consume function name
            
            # Check for parameters: : [ param1 , param2 , ... ]
            args = []
            next_token = peek()
            if next_token and next_token[0] == 'ASSIGN' and next_token[1] == ':':
                consume()  # Consume ':'
                next_token = peek()
                if next_token and next_token[0] == 'PAREN' and next_token[1] == '[':
                    consume()  # Consume '['
                    # Parse parameters
                    while True:
                        arg_token = peek()
                        if not arg_token:
                            break
                        if arg_token[0] == 'PAREN' and arg_token[1] == ']':
                            consume()  # Consume ']'
                            break
                        if arg_token[0] in ['STRING', 'IDENTIFIER', 'NUMBER']:
                            args.append(arg_token)
                            consume()  # Consume argument
                        elif (arg_token[0] == 'SEPARATOR' and arg_token[1] == ',') or (arg_token[0] == 'UNKNOWN' and arg_token[1] == ','):
                            consume()  # Consume comma
                        else:
                            consume()  # Consume other tokens
            
            return ('DCD_RUN', func_name, args), local_pos
        # Check for request statement: request : method<url headers data>
        elif token[0] == 'IDENTIFIER' and token[1] == 'request':
            consume()  # Consume 'request'
            if peek() and peek()[0] == 'ASSIGN':
                consume()  # Consume ':'
                
                # Get HTTP method
                method_token = peek()
                if not method_token or method_token[0] != 'IDENTIFIER':
                    return None, pos
                
                method = method_token[1].upper()  # Convert to uppercase
                consume()  # Consume method name
                
                # Check for arguments in angle brackets
                args = []
                has_opened_angle = False
                
                # Handle the special case where '<' and '-' are merged into '<-' 
                if peek() and peek()[0] == 'OPERATOR' and peek()[1] == '<':
                    consume()  # Consume '<'
                    has_opened_angle = True
                elif peek() and peek()[0] == 'OPERATOR' and peek()[1] == '<-':
                    # Special case: split '<-' into '<' and '-'
                    args.append(('OPERATOR', '-'))
                    local_pos += 1  # Consume the entire '<-' token
                    has_opened_angle = True
                
                if has_opened_angle:
                    # Parse arguments until '>' - treat each token as a separate argument
                    while peek() and not (peek()[0] == 'OPERATOR' and peek()[1] == '>'):
                        arg_token = consume()
                        if arg_token:
                            args.append(arg_token)
                    
                    if not (peek() and peek()[0] == 'OPERATOR' and peek()[1] == '>'):
                        return None, pos
                    
                    consume()  # Consume '>'
                
                return ('REQUEST', method, args), local_pos
        # Check for sre statement: sre : expression
        elif token[0] == 'IDENTIFIER' and token[1] == 'sre':
            consume()  # Consume 'sre'
            if peek() and peek()[0] == 'ASSIGN':
                consume()  # Consume ':'
                # Parse the expression to return
                expr, new_pos = self.interpreter.parse_expression(tokens, local_pos)
                if expr:
                    local_pos = new_pos
                    return ('SRE', expr), local_pos
        # Check for class instantiation or method call
        elif token[0] == 'IDENTIFIER':
            identifier = token[1]
            # Check if this is a class instantiation: ClassName : new : [args]
            if (peek(1) and peek(1)[0] == 'ASSIGN' and peek(1)[1] == ':' and 
                peek(2) and peek(2)[0] == 'IDENTIFIER' and peek(2)[1] == 'new'):
                consume()  # Consume class name
                consume()  # Consume ':'
                consume()  # Consume 'new'
                
                # Check for arguments
                args = []
                if peek() and peek()[0] == 'ASSIGN' and peek()[1] == ':':
                    consume()  # Consume ':'
                    if peek() and peek()[0] == 'PAREN' and peek()[1] == '[':
                        consume()  # Consume '['
                        # Parse arguments
                        while True:
                            arg_token = peek()
                            if not arg_token:
                                break
                            if arg_token[0] == 'PAREN' and arg_token[1] == ']':
                                consume()  # Consume ']'
                                break
                            if arg_token[0] in ['STRING', 'IDENTIFIER', 'NUMBER']:
                                args.append(arg_token)
                                consume()  # Consume argument
                            elif (arg_token[0] == 'SEPARATOR' and arg_token[1] == ',') or (arg_token[0] == 'UNKNOWN' and arg_token[1] == ','):
                                consume()  # Consume comma
                            else:
                                consume()  # Consume other tokens
                
                return ('CLASS_INSTANTIATION', identifier, args), local_pos
            # Check if this is a method call: instance : method : [args]
            elif peek(1) and peek(1)[0] == 'ASSIGN' and peek(1)[1] == ':':
                # Look ahead to see if the next token is an identifier (method name)
                next_token = peek(2)
                if next_token and next_token[0] == 'IDENTIFIER':
                    consume()  # Consume instance name
                    consume()  # Consume ':'
                    method_token = consume()  # Consume method name
                    method_name = method_token[1]
                    
                    # Check for arguments
                    args = []
                    if peek() and peek()[0] == 'ASSIGN' and peek()[1] == ':':
                        consume()  # Consume ':'
                        if peek() and peek()[0] == 'PAREN' and peek()[1] == '[':
                            consume()  # Consume '['
                            # Parse arguments
                            while True:
                                arg_token = peek()
                                if not arg_token:
                                    break
                                if arg_token[0] == 'PAREN' and arg_token[1] == ']':
                                    consume()  # Consume ']'
                                    break
                                if arg_token[0] in ['STRING', 'IDENTIFIER', 'NUMBER']:
                                    args.append(arg_token)
                                    consume()  # Consume argument
                                elif (arg_token[0] == 'SEPARATOR' and arg_token[1] == ',') or (arg_token[0] == 'UNKNOWN' and arg_token[1] == ','):
                                    consume()  # Consume comma
                                else:
                                    consume()  # Consume other tokens
                    
                    return ('METHOD_CALL', identifier, method_name, args), local_pos
        # Direct assignment: a : 1
        elif token[0] == 'IDENTIFIER' and peek(1) and peek(1)[0] == 'ASSIGN' and token[1] != 'dcd':
            # Check if this is not a time statement (let time plugin handle it)
            # Also check if this is not a sif or swhile statement (let siew plugin handle it)
            # Also check if this is not a suibtn statement (let sbtn plugin handle it)
            # Also check if this is not a web_get, web_post, web_put or web_delete statement (let web plugin handle it)
            # Also check if this is not a qr_text, qr_ascii or qr_png statement (let qrcode plugin handle it)
            # Also check if this is not a progress, spinner or loading_bar statement (let progress plugin handle it)
            # Also check if this is not a dice, coin, rps or guess_num statement (let game plugin handle it)
            # Also check if this is not a file_write, file_read, file_append, file_delete or dir_list statement (let fileio plugin handle it)
            if token[1] != 'time' and token[1] not in ['sif', 'swhile', 'suibtn', 'sysinfo', 'md5', 'sha256', 'base64_enc', 'base64_dec', 'rot13', 'list_create', 'list_add', 'list_show', 'list_len', 'list_get', 'list_remove', 'map_create', 'map_set', 'map_get', 'map_has', 'map_keys', 'map_values', 'map_clear', 'richtext', 'style', 'rainbow_text', 'typewriter', 'marquee', 'clear_text', 'color_block', 'qr_text', 'qr_ascii', 'qr_png', 'progress', 'spinner', 'loading_bar', 'dice', 'coin', 'rps', 'guess_num', 'file_write', 'file_read', 'file_append', 'file_delete', 'dir_list']:
                var_name = consume()[1]
                consume()  # Consume ':'
                
                # Check if this is a web_get, web_post, web_put or web_delete statement
                if local_pos < len(tokens) and tokens[local_pos][0] == 'IDENTIFIER' and tokens[local_pos][1] in ['web_get', 'web_post', 'web_put', 'web_delete']:
                    # Return None to let web plugin handle it
                    return None, pos
                
                # Check if this is a scui statement (let scui plugin handle it)
                if var_name == 'scui':
                    # Return None to let scui plugin handle it
                    return None, pos
                
                # Check if this is a richtext statement (let richtext plugin handle it)
                if var_name in ['richtext', 'style', 'rainbow_text', 'typewriter', 'marquee', 'clear_text', 'color_block']:
                    # Return None to let richtext plugin handle it
                    return None, pos
                
                expr, new_pos = self.interpreter.parse_expression(tokens, local_pos)
                if expr:
                    local_pos = new_pos
                    return ('ASSIGN', var_name, expr), local_pos
        
        return None, pos
    
    def execute_statement(self, stmt):
        """Execute basic statements"""
        if stmt[0] == 'ASSIGN' or stmt[0] == 'ASSIGNMENT':
            var_name = stmt[1]
            value = self.interpreter.evaluate_expression(stmt[2])
            self.interpreter.variables[var_name] = value
            return True
        elif stmt[0] == 'PRINT':
            value = self.interpreter.evaluate_expression(stmt[1])
            print(value)
            return True
        elif stmt[0] == 'COLOR_OUTPUT':
            color_token = stmt[1]
            text_token = stmt[2]
            
            # Evaluate text
            text = self.interpreter.evaluate_expression(text_token)
            
            # Determine color code
            color_code = '0'  # 默认颜色
            
            # 根据颜色类型处理
            if color_token[0] == 'STRING':
                color_str = color_token[1]
                
                # 检查是否是预定义颜色名称
                if color_str in self.color_names:
                    color_code = self.color_names[color_str]
                # 检查是否是RGB格式 (rgb(255,0,0))
                elif color_str.startswith('rgb(') and color_str.endswith(')'):
                    try:
                        rgb_values = color_str[4:-1].split(',')
                        r = int(rgb_values[0].strip())
                        g = int(rgb_values[1].strip())
                        b = int(rgb_values[2].strip())
                        # 使用ANSI 256色或RGB颜色
                        color_code = f'38;2;{r};{g};{b}'
                    except Exception as e:
                        print(f"Error: Invalid RGB format '{color_str}'")
                        return False
                # 检查是否是16进制格式 (#FF0000)
                elif color_str.startswith('#') and (len(color_str) == 7 or len(color_str) == 4):
                    try:
                        # 转换为RGB
                        hex_str = color_str[1:]
                        if len(hex_str) == 3:
                            # 简写形式 #RGB → #RRGGBB
                            hex_str = ''.join(c*2 for c in hex_str)
                        r = int(hex_str[0:2], 16)
                        g = int(hex_str[2:4], 16)
                        b = int(hex_str[4:6], 16)
                        # 使用ANSI 256色或RGB颜色
                        color_code = f'38;2;{r};{g};{b}'
                    except Exception as e:
                        print(f"Error: Invalid hex color format '{color_str}'")
                        return False
                else:
                    print(f"Error: Unknown color '{color_str}'")
                    return False
            
            # 输出彩色文本
            print(f"\033[{color_code}m{text}\033[0m")
            return True
        elif stmt[0] == 'IF':
            condition = self.interpreter.evaluate_expression(stmt[1])
            if condition:
                for body_stmt in stmt[2]:
                    self.execute_statement(body_stmt)
            return True
        elif stmt[0] == 'IF_ELSE':
            if_condition = stmt[1]
            if_body = stmt[2]
            elif_clauses = stmt[3]
            else_body = stmt[4]
            
            # 检查if条件
            if self.evaluate_condition(if_condition):
                for body_stmt in if_body:
                    self.execute_statement(body_stmt)
                return True
            
            # 检查elif子句
            for elif_condition, elif_body in elif_clauses:
                if self.evaluate_condition(elif_condition):
                    for body_stmt in elif_body:
                        self.execute_statement(body_stmt)
                    return True
            
            # 检查else子句
            if else_body:
                for body_stmt in else_body:
                    self.execute_statement(body_stmt)
            
            return True
        elif stmt[0] == 'WHILE':
            condition_tokens = stmt[1]
            body = stmt[2]
            
            while self.evaluate_condition(condition_tokens):
                for body_stmt in body:
                    self.execute_statement(body_stmt)
            
            return True
        elif stmt[0] == 'FUNCTION_DEF':
            # 处理不同格式的函数定义
            if len(stmt) == 3:
                # 传统格式: sde func : ...
                func_name = stmt[1]
                func_body = stmt[2]
                params = []
            elif len(stmt) == 4:
                # 新格式: sdef <func> [params] : ...
                func_name = stmt[1]
                params = stmt[2]
                func_body = stmt[3]
            else:
                return False
            
            # 存储函数
            self.functions[func_name] = {
                'params': params,
                'body': func_body
            }
            
            # 也存储在解释器变量中以保持兼容性
            self.interpreter.variables[func_name] = {
                'type': 'function',
                'params': params,
                'body': func_body
            }
            
            if hasattr(self.interpreter, 'debug_mode') and self.interpreter.debug_mode:
                print(f"Debug: Defined function '{func_name}' with params {params}")
            return True
        elif stmt[0] == 'FUNCTION_CALL':
            # 处理函数调用
            if len(stmt) == 2:
                # 传统格式: sde run<func>
                func_name = stmt[1]
                args = []
            elif len(stmt) == 3:
                # 新格式: 带参数的调用
                func_name = stmt[1]
                args = stmt[2]
            else:
                return False
            
            return self.handle_function_call(func_name, args)
        elif stmt[0] == 'CLASS_DEF':
            # 处理类定义
            class_name = stmt[1]
            body_tokens = stmt[2]
            return self.handle_class_def(class_name, body_tokens)
        elif stmt[0] == 'DCD_RUN':
            # 处理 dcd run 命令
            func_name = stmt[1]
            args = stmt[2]
            return self.handle_function_call(func_name, args)
        elif stmt[0] == 'CLASS_INSTANTIATION':
            # 处理类实例化
            class_name = stmt[1]
            args = stmt[2]
            return self.handle_class_instantiation(class_name, args)
        elif stmt[0] == 'SRE':
            # Handle return statement: sre : expression
            value = self.interpreter.evaluate_expression(stmt[1])
            # Store the return value in a special variable
            self.interpreter.variables['__return_value__'] = value
            # Return the value to indicate that we want to return from the current function
            return value
        elif stmt[0] == 'METHOD_CALL':
            # 处理方法调用
            instance_name = stmt[1]
            method_name = stmt[2]
            args = stmt[3]
            return self.handle_method_call(instance_name, method_name, args)
        elif stmt[0] == 'START':
            # Run another SCL file
            file_path_token = stmt[1]
            file_path = self.interpreter.evaluate_expression(file_path_token)
            
            # Check if file exists
            import os
            if not os.path.exists(file_path):
                print(f"Error: File {file_path} not found")
                return False
            
            try:
                # Read the file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                
                # Execute the file content
                print(f"Running file: {file_path}")
                success = self.interpreter.execute(file_content, file_path)
                if not success:
                    print(f"Error: Failed to run file {file_path}")
                    return False
                
                return True
            except Exception as e:
                print(f"Error running file {file_path}: {e}")
                import traceback
                traceback.print_exc()
                return False
        elif stmt[0] == 'REQUEST':
            # 处理 HTTP 请求
            method = stmt[1]
            args = stmt[2]
            
            # Evaluate arguments - each arg is a single token
            eval_args = []
            for arg_token in args:
                eval_args.append(self.interpreter.evaluate_expression(arg_token))
            
            if not eval_args:
                print("Error: No URL provided for request")
                return False
            
            url = str(eval_args[0])
            headers = None
            data = None
            
            # Parse optional headers and data
            if len(eval_args) > 1:
                # For simplicity, we'll treat the second argument as headers if it's a dictionary
                # (Note: SCL doesn't support direct dictionary creation, so this is limited)
                headers = eval_args[1]
            
            if len(eval_args) > 2:
                # Third argument as data
                data = eval_args[2]
            
            try:
                response = None
                
                # Make the request with various options to handle proxy issues
                try:
                    if method == 'GET':
                        response = requests.get(url, headers=headers, timeout=5, proxies={}, verify=False, allow_redirects=True)
                    elif method == 'POST':
                        response = requests.post(url, headers=headers, data=data, timeout=5, proxies={}, verify=False, allow_redirects=True)
                    elif method == 'PUT':
                        response = requests.put(url, headers=headers, data=data, timeout=5, proxies={}, verify=False, allow_redirects=True)
                    elif method == 'DELETE':
                        response = requests.delete(url, headers=headers, timeout=5, proxies={}, verify=False, allow_redirects=True)
                    else:
                        print(f"Error: Unsupported HTTP method '{method}'")
                        return False
                except Exception as e:
                    # If all else fails, try with even more options
                    print("Warning: Request failed, trying with more options...")
                    session = requests.Session()
                    session.trust_env = False  # Disable environment proxy settings
                    if method == 'GET':
                        response = session.get(url, headers=headers, timeout=5, verify=False, allow_redirects=True)
                    elif method == 'POST':
                        response = session.post(url, headers=headers, data=data, timeout=5, verify=False, allow_redirects=True)
                    elif method == 'PUT':
                        response = session.put(url, headers=headers, data=data, timeout=5, verify=False, allow_redirects=True)
                    elif method == 'DELETE':
                        response = session.delete(url, headers=headers, timeout=5, verify=False, allow_redirects=True)
                    else:
                        print(f"Error: Unsupported HTTP method '{method}'")
                        return False
                
                # Print response status code
                print(f"Status Code: {response.status_code}")
                
                # Print response headers
                print("Headers:")
                for key, value in response.headers.items():
                    print(f"  {key}: {value}")
                
                # Print response content
                print("\nResponse Content:")
                print(response.text)
                
                # Store response in variables for further processing
                self.interpreter.variables['response_status'] = response.status_code
                self.interpreter.variables['response_text'] = response.text
                
                return True
                
            except requests.exceptions.RequestException as e:
                print(f"Error making HTTP request: {e}")
                return False
            except Exception as e:
                print(f"Error in request operation: {e}")
                import traceback
                traceback.print_exc()
                return False
        return False
    
    def handle_function_call(self, func_name, args):
        """Handle function call"""
        # 首先从 self.functions 中查找
        if func_name in self.functions:
            func = self.functions[func_name]
            params = func['params']
            body = func['body']
        # 尝试从解释器变量中查找
        elif func_name in self.interpreter.variables:
            func_data = self.interpreter.variables[func_name]
            # 检查是否是函数
            if isinstance(func_data, dict) and func_data.get('type') == 'function':
                params = func_data['params']
                body = func_data['body']
            # 检查是否是传统格式的函数（直接存储为列表）
            elif isinstance(func_data, list):
                params = []
                body = func_data
            else:
                print(f"Error: '{func_name}' is not a function")
                return False
        else:
            print(f"Error: Function '{func_name}' not defined")
            return False
        
        # 创建新的变量作用域
        old_vars = self.interpreter.variables.copy()
        
        # 绑定参数到参数名
        for i, param in enumerate(params):
            if i < len(args):
                # 检查参数是否已经是一个值（不是表达式令牌）
                if isinstance(args[i], (int, float, str, bool)):
                    arg_value = args[i]
                else:
                    arg_value = self.interpreter.evaluate_expression(args[i])
                self.interpreter.variables[param] = arg_value
                if hasattr(self.interpreter, 'debug_mode') and self.interpreter.debug_mode:
                    print(f"Debug: Bound parameter '{param}' to value '{arg_value}'")
            else:
                self.interpreter.variables[param] = 0
                if hasattr(self.interpreter, 'debug_mode') and self.interpreter.debug_mode:
                    print(f"Debug: Bound parameter '{param}' to default value 0")
        
        # 执行函数体
        success = True
        return_value = None
        pos = 0
        while pos < len(body):
            stmt, new_pos = self.interpreter.parse_statement(body, pos)
            if stmt:
                result = self.execute_statement(stmt)
                # Check if result is not a boolean - this means we encountered an sre statement
                if not isinstance(result, bool):
                    return_value = result
                    break
                if not result:
                    success = False
                    break
                pos = new_pos
            else:
                pos += 1
        
        # 恢复变量作用域
        old_return_value = old_vars.get('__return_value__')
        self.interpreter.variables = old_vars
        if old_return_value is not None:
            self.interpreter.variables['__return_value__'] = old_return_value
        
        # Return the return value if we have one, otherwise return success
        if return_value is not None:
            return return_value
        return success
    
    def handle_class_def(self, class_name, body_tokens):
        """Handle class definition"""
        # 解析类体以提取方法和属性
        methods = {}
        attributes = {}
        
        # 从体令牌中解析方法
        pos = 0
        while pos < len(body_tokens):
            # 跳过空令牌、换行和其他分隔符
            while pos < len(body_tokens) and body_tokens[pos][1] in ['\n', ' ', '\t']:
                pos += 1
            
            if pos >= len(body_tokens):
                break
            
            # 检查是否是方法定义
            if body_tokens[pos][0] == 'IDENTIFIER' and body_tokens[pos][1] == 'smethod':
                # 检查是否有方法名
                if (pos + 3 < len(body_tokens) and 
                    body_tokens[pos + 1][0] == 'OPERATOR' and body_tokens[pos + 1][1] == '<' and
                    body_tokens[pos + 2][0] == 'IDENTIFIER' and
                    body_tokens[pos + 3][0] == 'OPERATOR' and body_tokens[pos + 3][1] == '>'):
                    
                    method_name = body_tokens[pos + 2][1]
                    pos += 4
                    
                    # 跳过空格和换行
                    while pos < len(body_tokens) and body_tokens[pos][1] in ['\n', ' ', '\t']:
                        pos += 1
                    
                    # 解析参数
                    params = []
                    if pos < len(body_tokens) and body_tokens[pos][0] == 'PAREN' and body_tokens[pos][1] == '[':
                        pos += 1
                        while pos < len(body_tokens) and not (body_tokens[pos][0] == 'PAREN' and body_tokens[pos][1] == ']'):
                            if body_tokens[pos][0] == 'IDENTIFIER':
                                params.append(body_tokens[pos][1])
                            pos += 1
                        if pos < len(body_tokens) and body_tokens[pos][0] == 'PAREN' and body_tokens[pos][1] == ']':
                            pos += 1
                    
                    # 跳过空格和换行
                    while pos < len(body_tokens) and body_tokens[pos][1] in ['\n', ' ', '\t']:
                        pos += 1
                    
                    # 解析方法体
                    if pos < len(body_tokens) and body_tokens[pos][0] == 'ASSIGN' and body_tokens[pos][1] == ':':
                        pos += 1
                        
                        # 跳过空格和换行
                        while pos < len(body_tokens) and body_tokens[pos][1] in ['\n', ' ', '\t']:
                            pos += 1
                        
                        method_body = []
                        while pos < len(body_tokens):
                            if body_tokens[pos][0] == 'IDENTIFIER' and body_tokens[pos][1] == 'end':
                                pos += 1
                                break
                            method_body.append(body_tokens[pos])
                            pos += 1
                        
                        methods[method_name] = {
                            'params': params,
                            'body': method_body
                        }
                else:
                    # 不是有效的方法定义，跳过
                    pos += 1
            else:
                # 不是方法定义，跳过
                pos += 1
        
        self.classes[class_name] = {
            'methods': methods,
            'attributes': attributes
        }
        
        # 也存储在解释器变量中
        self.interpreter.variables[class_name] = {
            'type': 'class',
            'methods': methods,
            'attributes': attributes
        }
        
        if hasattr(self.interpreter, 'debug_mode') and self.interpreter.debug_mode:
            print(f"Debug: Defined class '{class_name}' with methods {list(methods.keys())}")
        return True
    
    def handle_class_instantiation(self, class_name, args):
        """Handle class instantiation"""
        if class_name not in self.classes:
            print(f"Error: Class '{class_name}' not defined")
            return False
        
        class_def = self.classes[class_name]
        
        # 创建实例
        instance = {
            'class': class_name,
            'methods': class_def['methods'].copy(),
            'attributes': class_def['attributes'].copy()
        }
        
        # 存储实例在变量中
        instance_name = f"{class_name.lower()}_instance"
        if args:
            # 如果提供了参数，使用第一个参数作为实例名
            instance_name = self.interpreter.evaluate_expression(args[0])
        
        self.interpreter.variables[instance_name] = instance
        
        if hasattr(self.interpreter, 'debug_mode') and self.interpreter.debug_mode:
            print(f"Debug: Created instance of class '{class_name}' as '{instance_name}'")
        return True
    
    def handle_method_call(self, instance_name, method_name, args):
        """Handle method call"""
        if instance_name not in self.interpreter.variables:
            print(f"Error: Instance '{instance_name}' not found")
            return False
        
        instance = self.interpreter.variables[instance_name]
        
        if 'methods' not in instance or method_name not in instance['methods']:
            print(f"Error: Method '{method_name}' not found in instance")
            return False
        
        method = instance['methods'][method_name]
        params = method['params']
        body = method['body']
        
        # 创建新的变量作用域
        old_vars = self.interpreter.variables.copy()
        
        # 添加 'this' 引用
        self.interpreter.variables['this'] = instance
        
        # 绑定参数到参数名
        for i, param in enumerate(params):
            if i < len(args):
                self.interpreter.variables[param] = self.interpreter.evaluate_expression(args[i])
            else:
                self.interpreter.variables[param] = 0
        
        # 执行方法体
        success = True
        pos = 0
        while pos < len(body):
            stmt, new_pos = self.interpreter.parse_statement(body, pos)
            if stmt:
                if not self.execute_statement(stmt):
                    success = False
                    break
                pos = new_pos
            else:
                pos += 1
        
        # 恢复变量作用域
        self.interpreter.variables = old_vars
        
        return True
    
    def evaluate_condition(self, condition_tokens):
        """Evaluate a condition from tokens"""
        if len(condition_tokens) >= 3:
            left = condition_tokens[0]
            op = condition_tokens[1]
            right = condition_tokens[2]
            
            left_value = self.interpreter.evaluate_expression(left)
            right_value = self.interpreter.evaluate_expression(right)
            
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
            elif op[1] == '&':  # Logical AND
                return left_value and right_value
            elif op[1] == '|':  # Logical OR
                return left_value or right_value
        return False
