// Author: Michael Pradel
// Compares warnings found with different variants of the approach.
//  arg1 = file with inspected warnings
//  arg2 = file with other warnings

(function() {

    const fs = require("fs");
    const process = require("process");

    function Warning(score, location, extraInfo, isTruePositive) {
        this.score = score;
        this.location = location;
        this.extraInfo = extraInfo;
        this.isTruePositive = isTruePositive;
    }

    Warning.prototype.equals = function(other) {
        return this.location === other.location && this.extraInfo === other.extraInfo;
    };

    function readWarnings(path) {
        const result = []
        let allLines = fs.readFileSync(path, {encoding:"utf8"});
        allLines = allLines.split("\n");
        for (let i = 0; i < allLines.length; i++) {
            const line = allLines[i];
            const entries = line.split(" | ");
            let extraInfo, isTruePositive;
            if (entries[entries.length - 2] === "y" || entries[entries.length - 2] === "n") {
                // has been manually inspected and classified
                extraInfo = entries.slice(2, entries.length - 2).join(" | ");
                isTruePositive = entries[entries.length - 2];
            } else {
                extraInfo = entries.slice(2).join(" | ");
            }
            const warning = new Warning(entries[0], entries[1], extraInfo, isTruePositive);
            result.push(warning);
        }
        return result;
    }

    const args = process.argv.slice(2);
    const inspectedWarnings = readWarnings(args[0]);
    const otherWarnings = readWarnings(args[1]);

    for (let i = 0; i < inspectedWarnings.length; i++) {
        const inspectedWarning = inspectedWarnings[i];
        const classification = inspectedWarning.isTruePositive === "y" ? "TP" : "FP";

        let found = false;
        for (let j = 0; j < otherWarnings.length; j++) {
            const otherWarning = otherWarnings[j];
            if (inspectedWarning.equals(otherWarning)) {
                found = true;
                console.log(classification, " with score ", otherWarning.score, inspectedWarning.location);
                break;
            }
        }
        if (!found) {
            console.log(classification, "not found", inspectedWarning.location);
        }



    }


})();