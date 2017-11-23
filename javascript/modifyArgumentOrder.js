var fs = require("fs");
var esprima = require("esprima");
var estraverse = require("estraverse");
var escodegen = require("escodegen");

var rawJSFilesDir = "../data/js/programs_50/";
var formattedJSFilesDir = "../data/js/shuffled_arguments/orig/";
var modifiedJSFilesDir = "../data/js/shuffled_arguments/shuffled/";

function shuffle(a) {
    var j, x, i;
    for (i = a.length; i; i--) {
        j = Math.floor(Math.random() * i);
        x = a[i - 1];
        a[i - 1] = a[j];
        a[j] = x;
    }
}

function transformAST(ast) {
    estraverse.traverse(ast, {
        enter:function(node, parent) {
            if (node.type === "CallExpression") {
                shuffle(node.arguments);
            }
        }
    });
}

var files = fs.readdirSync(rawJSFilesDir);
for (var i = 0; i < files.length; i++) {
    var file = files[i];
    if (file.endsWith(".js")) {
        var code = fs.readFileSync(rawJSFilesDir + "/" + file, {encoding:"utf8"});
        var ast = esprima.parse(code);
        var formattedCode = escodegen.generate(ast);
        fs.writeFileSync(formattedJSFilesDir + file, formattedCode);
        transformAST(ast);
        var modifiedCode = escodegen.generate(ast);
        fs.writeFileSync(modifiedJSFilesDir + file, modifiedCode);
    }
}