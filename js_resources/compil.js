
var tokenize = function(string){
    var toks = ['(', ')', '+', '-', '*', '%', '/', 'L', 'R'];
    var retAcc = [];
    var tokAcc = '';
    for(var i = 0; i < string.length; i++){
        if(toks.indexOf(string[i]) >= 0){
            if(tokAcc.length > 0){
                retAcc.push([tokAcc, i - tokAcc.length]);
                tokAcc = '';
            }
            retAcc.push([string[i], i]);
        }else if(string[i] >= '0' && string[i] <= '9'){
            tokAcc += string[i];
        }else if(string[i].trim() !== ''){
            throw new Error("Unrecognized token: " + string[i]);
        }else if(tokAcc.length > 0){
            retAcc.push([tokAcc, i]);
            tokAcc = '';
        }
    }

    return retAcc;
};

var parse = function(tokens){
    var tabs = '';
    var ops = {'*': {code: [tabs + 'popl %ebx', tabs + 'popl %eax', tabs + 'imull %ebx, %eax', tabs + 'pushl %eax'], func: function(x, y){return x * y;}},
            '+': {code: [tabs + 'popl %ebx', tabs + 'popl %eax', tabs + 'addl %ebx, %eax', tabs + 'pushl %eax'], func: function(x, y){return x + y;}},
            '-': {code: [tabs + 'popl %ebx', tabs + 'popl %eax', tabs + 'subl %ebx, %eax', tabs + 'pushl %eax'], func: function(x, y){return x - y;}},
            '/': {code: [tabs + 'popl %eax', tabs + 'popl %ebx', tabs + 'idivl %ebx', tabs + 'pushl %eax'], func: function(x, y){return Math.floor(x/y);}},
            '%': {code: [tabs + 'popl %ebx', tabs + 'popl %eax', tabs + 'idivl %ebx', tabs + 'pushl %edx'], func: function(x, y){return x % y;} }};

    var push_depth = 0;
    var max_depth = 0;
    var lines = [];
    var tok_ind = 0;

    var next_tok = function(){
        if(tok_ind < tokens.length)
            return tokens[tok_ind++];
        throw new Error("Unexpected EOF");
    }

    var doPush = function(change){
        if(change === undefined) change = 1;
        push_depth += change;
        if(push_depth > max_depth){
            max_depth = push_depth;
        }
    };

    var s_expr = function(innards_fn){
        var curr = next_tok();
        if(curr[0] === '('){
            var v = innards_fn(s_expr);
            var t = next_tok();
            if(t[0] !== ')'){
                throw new Error("Mismatched parens at index " + t[1]);
            }
            return v;
        }else if(!isNaN(curr[0])){
            return curr[0] * 1;
        }else if(curr[0] === 'L'){
            lines.push(tabs + 'pushl %edi' + tabs + '//position ' + curr[1] + ' of source.');
            doPush();
        }else if(curr[0] === 'R'){
            lines.push(tabs + 'pushl %esi' + tabs + '//position ' + curr[1] + ' of source.');
            doPush();
        }else{
            throw new Error('Unexpected token ' + curr[0] + ' at ' + curr[1]);
        }
    };

    var innards = function(s_expr_fn){
        var op = next_tok();
        if(ops[op[0]] === undefined){
            throw new Error("Invalid operator: " + op[0] + ' at ' + op[1]);
        }

        var l = s_expr_fn(innards);
        var r = s_expr_fn(innards);

        if(l !== undefined && r !== undefined){
            return ops[op[0]].func(l, r);
        }else{
            if(l !== undefined){
                lines.push(tabs + 'pushl $' + l + tabs + '//evaluated a constant expression');
                doPush();
            }
            if(r !== undefined){
                lines.push(tabs + 'pushl $' + r + tabs + '//evaluated a constant expression');
                doPush();
            }

            if(op[0] == '%' || op[0] == '/'){
                lines.push(tabs + 'movl $0 %edx' + tabs + '//preparing for a divide');
            }

            lines = lines.concat(ops[op[0]].code);
            lines.push(tabs + '//evaluated ' + op[0] + ' at ' + op[1]);
            doPush(-1);
        }
    }

    var rv = s_expr(innards);
    return {lines: lines, depth: max_depth, value: rv};
};
