var esprima = require("esprima");
var fs = require("fs");

var jsFile = process.argv[2]
var tokenFile = process.argv[3]

var js = fs.readFileSync(jsFile, {encoding: "utf8"});
var tokens = esprima.tokenize(js);
fs.writeFileSync(tokenFile, JSON.stringify(tokens, 0, 2));