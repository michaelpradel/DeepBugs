// Author: Michael Pradel

(function() {

    const fs = require("fs");
    const util = require("./jsExtractionUtil");

    function visitFile(path, allTokenSequences) {
        console.log("Reading " + path);

        const assignments = [];
        const code = fs.readFileSync(path);
        const tokens = util.getTokens(code);
        if (tokens) {
            allTokenSequences.push(util.tokensToStrings(tokens));
        } else {
            console.log("Ignoring file with parse errors: " + path);
        }
    }

    module.exports.visitFile = visitFile;

})();