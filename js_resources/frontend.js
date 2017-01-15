var setUpDebug = function(comp){
    $('#compiled').html('');
    if(comp.value === undefined){
        for(var i = 0; i < comp.lines.length; i++){
            $('#compiled').append('<li id="instr' + i + '">' + comp.lines[i] + '</li>');
        }
        $('#instr0').addClass('currInstr');
        $('#compiled').append('<li id="instr' + comp.lines.length + '">popl %eax //store a return value</li>');
        return comp.lines.length + 1;
    }else{
        $('#compiled').html('<li id="instr0" class="currInstr">//This was a constant value:</li>');
        $('#compiled').append('<li id="instr1">movl $' + comp.value + ' %eax</li>');
        return 2;
    }

};

$(document).ready(function(){
    var eip = 0;
    var maxEip = -1;
    var stack = [];
    var regs = {eax: 0, ebx: 0, edx: 0, esi: 0, edi: 0};
    var states = [];
    $('#compilClick').click(function(){
        try{
            var comp = parse(tokenize($('#calcula').val()));
            $('#stepBack').prop('disabled', true);
            $('#stepNext').prop('disabled', false);
            maxEip = setUpDebug(comp);
            eip = 0;
            stack = [];
            states = [];
        }catch(e){
            $('#compiled').html('<li id="instr0" class="currInstr">ERROR:</li>');
            $('#compiled').append('<li id="instr1">' + e.message + '</li>');
        }

    });

    var flashState = function(){
        states.push({stack: stack.slice(),
                     regs: {eax: regs.eax, ebx: regs.ebx,
                            edx: regs.edx, esi: regs.esi,
                            edi: regs.edi}});

        $('#stack').html('');
        for(var i = stack.length - 1; i >= 0; i--){
            $('#stack').append('<li>' + stack[i] + '</li>');
        }
    };

    var step = function(n){
        $('#instr' + eip).removeClass('currInstr');
        eip += n;
        $('#instr' + eip).addClass('currInstr');
        var inst = $('#instr' + eip).text().split('//')[0];

        if(eip < states.length){
            stack = states[eip].stack;
            regs = states[eip].regs;
            return flashState();
        }else if(inst.length !== 0){
            parts = inst.trim().split(' ');
            if(parts[0] === 'pushl'){
                if(parts[1][0] === '$'){
                    stack.push(parts[1].substr(1));
                }else{
                    stack.push(regs[parts[1].substr(1)]);
                }
            }else if(parts[0] === 'popl'){
                regs[parts[1].substr(1)] = stack.pop();
            }else if(parts[0] === 'addl'){
                regs[parts[2].substr(1)] += regs[parts[1].substr(1)];
            }else if(parts[0] === 'imull'){
                regs[parts[2].substr(1)] *= regs[parts[1].substr(1)];
            }else if(parts[0] === 'subl'){
                regs[parts[2].substr(1)] -= regs[parts[1].substr(1)];
            }else if(parts[0] === 'movl'){
                if(parts[1][0] === '$')
                    regs[parts[2].substr(1)] = parts[1].substr(1);
                else
                    regs[parts[2].substr(1)] -= regs[parts[1].substr(1)];
            }
        }else{return;}

        if(eip === maxEip - 1){
            $('#stepNext').prop('disabled', true);
        }else{
            $('#stepNext').prop('disabled', false);
        }
        if(eip === 0){
            $('#stepBack').prop('disabled', true);
        }else{
            $('#stepBack').prop('disabled', false);
        }
        flashState();
    };

    $('#stepBack').click(function(){step(-1);});
    $('#stepNext').click(function(){step(1);});
});
