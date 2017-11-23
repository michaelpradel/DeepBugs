// Author: Michael Pradel

(function() {

    const fs = require("fs");
    const util = require("./jsExtractionUtil");

    // configuration parameters
    const tokenContextLength = 20; // must be an even number

    function visitFile(path, allIdsLits) {
        console.log("Reading " + path);

        const code = fs.readFileSync(path);
        const tokens = util.getTokens(code);
        const k = tokenContextLength / 2;
        if (tokens) {
            for (let i = 0; i < tokens.length; i++) {
                const token = tokens[i];
                if (util.isIdLit(token)) {
                    let preContext = tokens.slice(Math.max(0, i - k), i);
                    preContext = util.tokensToStrings(preContext);
                    while (preContext.length !== k) preContext = [""].concat(preContext);
                    let postContext = tokens.slice(i + 1, i + k);
                    postContext = util.tokensToStrings(postContext);
                    while (postContext.length !== k) postContext.push("");
                    const idLit = {
                        token: util.tokenToString(token),
                        context: preContext.concat(postContext)
                    };
                    allIdsLits.push(idLit);
                }
            }
        } else {
            console.log("Ignoring file with parse errors: " + path);
        }
    }

    module.exports.visitFile = visitFile;

})();