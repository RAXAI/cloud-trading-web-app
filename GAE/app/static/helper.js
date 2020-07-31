function myFunc(vars) { 
var arr =[['party','votes']];
for (var key in vars) {
    if (vars.hasOwnProperty(key)) {
        var zx =[key,vars[key]];
        arr.push(zx);
            }
}

return arr
}



