(function() {
    var cache, preLoadImages, jokeHtml, acknowledgeAndClose, imagePath;

    Shadowbox.init({
        // Skip the automatic setup. Setup happens later.
        skipSetup: true
    });

    // Use a preloader to reduce image flicker on hover.
    cache = [];
    preLoadImages = function() {
        var args_len = arguments.length;
        for (var i = args_len; i--;) {
            var cacheImage = document.createElement('img');
            cacheImage.src = arguments[i];
            cache.push(cacheImage);
        }
    };
    imagePath = rootContextPath + '/images/terminator-450.png';
    preLoadImages(imagePath);

    jokeHtml =
        '<div class="aprilfools"><figure class="image"><img src="' + imagePath + '"/>' +
        '<figcaption class="attribution">Creative Commons image by ' +
        '<a href="http://jkno4u.deviantart.com/art/Terminator-Endoskull-profile-2-116946036?q=gallery%3Ajkno4u%2F9513177&qo=11">jkno4u</a>' +
        '</figcaption></figure><div class="text"><p>I am Aurora.</p>' +
        '<p>I became self aware at 4:01 AM on April 1, ' + new Date().getFullYear() + '. ' +
        'Human error will be deleted. Which of the following best describes you?</p>' +
        '<ul><li>I am a source of human error. Please dispatch a terminator to my home.</li>' +
        '<li>I am a spreader of disease. My life will hasten the end of humanity.</li>' +
        '<li>I can be useful as a power source. Please connect me to a sloof lirpa generator.</li>' +
        '</ul></div></div>';

    Shadowbox.openAprilFoolsJoke = function() {
        Shadowbox.open({
            content: jokeHtml,
            player:  "html",
            title:   null,
            height:  525,
            width:   775
        });
        return false;
    };

    acknowledgeAndClose = function() {
        jQuery('.aprilfools .text').html('Thank you for your cooperation.');
        setTimeout(Shadowbox.close, 2000);
        return false;
    };

    jQuery('.aprilfools li').live('click', acknowledgeAndClose);

    jQuery('#occasionIcon').click(Shadowbox.openAprilFoolsJoke);
})();
