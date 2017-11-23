(function() {
    var fwUl, fwLi = [], fwRemove, wtFramework = document.getElementById('_wtframework');

    fwRemove = function() {
        document.body.removeChild(fwUl);
    };

    if (wtFramework) {
        document.body.removeChild(wtFramework);
        return;
    }

    function fwItem(verPaths, cdnjsName) {
        if ( ! (verPaths instanceof Array)) {
            verPaths = [ verPaths ];
        }
        this.verPaths  = verPaths;
        this.cdnjsName = cdnjsName || '';
    }

    function fwApplyStyles(element, styles) {
        for (var s in styles) {
            if (typeof element.style.setProperty !== 'undefined') {
                element.style.setProperty(s, styles[s], null);
            } else {
                element.style[s] = styles[s];
            }
        }
    }

    var fwList = {
        'Ace'                        : new fwItem('ace', 'ace'),
        'ActiveJS'                   : new fwItem('ActiveSupport'),
        'AngularJS'                  : new fwItem('angular.version.full'),
        'Backbone.js'                : new fwItem('Backbone.VERSION', 'backbone.js'),
        'Backbone localStorage'      : new fwItem('Store', 'backbone-localstorage.js'),
        'Base2'                      : new fwItem('base2.version'),
        'Batman.js'                  : new fwItem('Batman'),
        'CamanJS'                    : new fwItem('Caman.version.release', 'camanjs'),
        'Chainvas'                   : new fwItem('Chainvas'),
        'CoffeeScript'               : new fwItem('CoffeeScript', 'coffee-script'),
        'Clientcide Libraries'       : new fwItem('Clientcide.version'),
        'Crafty'                     : new fwItem('Crafty.init'),
        'CSS 3 Finalize'             : new fwItem('$.cssFinalize', 'css3finalize'),
        'CSS 3 Pie'                  : new fwItem('PIE', 'css3pie'),
        'Cufón'                      : new fwItem('Cufon', 'cufon'),
        'D3'                         : new fwItem('d3.version', 'd3'),
        'Datejs'                     : new fwItem('Date.today', 'datejs'),
        'Davis.js'                   : new fwItem('Davis.version', 'davis.js'),
        'DD_belatedPNG'              : new fwItem('DD_belatedPNG', 'dd_belatedpng'),
        'DocumentUp'                 : new fwItem('DocumentUp', 'documentup'),
        'DHTMLX'                     : new fwItem('dhtmlx'),
        'Dojo'                       : new fwItem('dojo.version', 'dojo'),
        'Dojo Mobile'                : new fwItem('dojox.mobile'),
        'Ember'                      : new fwItem('Ember.VERSION', 'ember.js'),
        'Enyo'                       : new fwItem('enyo'),
        'Ext JS'                     : new fwItem(['Ext.version','Ext.versions.core.version'], 'ext-core'),
        'fancyBox'                   : new fwItem('$.fancybox.version', 'fancybox'),
        'flexie'                     : new fwItem('Flexie.version', 'flexie'),
        'Flot'                       : new fwItem('$.plot.version', 'flot'),
        'Galleria'                   : new fwItem('Galleria.version', 'galleria'),
        'Google Chrome Frame'        : new fwItem('CFInstall', 'chrome-frame'),
        'g.Raphaël'                  : new fwItem('Raphael.fn.g', 'graphael'),
        'Glow'                       : new fwItem('glow.VERSION'),
        'Handlebars'                 : new fwItem('Handlebars.VERSION', 'handlebars.js'),
        'Head JS'                    : new fwItem('head.js', 'headjs'),
        'Highcharts JS'              : new fwItem('Highcharts.version', 'highcharts'),
        'History.js'                 : new fwItem('History.Adapter', 'History.js'),
        'Hogan.js'                   : new fwItem('Hogan'),
        'html5shiv'                  : new fwItem('html5', 'html5shiv'),
        'ICanHaz.js'                 : new fwItem('ich.VERSION', 'ICanHaz.js'),
        'JS State Machine'           : new fwItem('StateMachine.VERSION', 'javascript-state-machine'),
        'JavaScriptMVC'              : new fwItem('steal.fn'),
        'jQuery'                     : new fwItem('jQuery.fn.jquery', 'jquery'),
        'jQuery Mobile'              : new fwItem('jQuery.mobile'),
        'jQuery throttle / debounce' : new fwItem('jQuery.debounce', 'jquery-throttle-debounce'),
        'jQuery Tools'               : new fwItem('jQuery.tools.version', 'jquery-tools'),
        'jQuery Cycle'               : new fwItem('jQuery.fn.cycle.ver', 'jquery.cycle'),
        'jQuery UI'                  : new fwItem('$.ui.version', 'jqueryui'),
        'js-signals'                 : new fwItem('signals.VERSION', 'js-signals'),
        'JSXGraph'                   : new fwItem('JXG', 'jsxgraph'),
        'Kendo UI'                   : new fwItem('kendo'),
        'Knockout'                   : new fwItem('ko', 'knockout'),
        'LABjs'                      : new fwItem('$LAB', 'labjs'),
        'LESS'                       : new fwItem('less', 'less.js'),
        'LightningJS'                : new fwItem('lightningjs'),
        'LungoJS'                    : new fwItem('LUNGO.VERSION'),
        'Masonry'                    : new fwItem('jQuery.fn.masonry', 'masonry'),
        'Midori'                     : new fwItem('midori.domReady'),
        'Modernizr'                  : new fwItem('Modernizr._version', 'modernizr'),
        'MochiKit'                   : new fwItem('MochiKit.MochiKit.VERSION'),
        'MooTools A.R.T.'            : new fwItem('ART.version'),
        'MooTools Core'              : new fwItem('MooTools.version', 'mootools'),
        'MooTools More'              : new fwItem('MooTools.More.version'),
        'Mustache'                   : new fwItem('Mustache.version', 'mustache.js'),
        'Ninja UI'                   : new fwItem('jQuery.ninja.version', 'ninjaui'),
        'Noisy'                      : new fwItem('jQuery.fn.noisy', 'noisy'),
        'oCanvas'                    : new fwItem('oCanvas', 'ocanvas'),
        'o2.js'                      : new fwItem('o2.version'),
        'PageDown'                   : new fwItem('Markdown', 'pagedown'),
        'Prettify'                   : new fwItem('prettyPrint', 'prettify'),
        'Processing.js'              : new fwItem('Processing.version', 'processing.js'),
        'Prototype'                  : new fwItem('Prototype.Version', 'prototype'),
        'PubNub'                     : new fwItem('PUBNUB', 'pubnub'),
        'Qooxdoo'                    : new fwItem('qx.$$libraries.qx.version'),
        'Raphaël'                    : new fwItem('Raphael.version', 'raphael'),
        'Rico'                       : new fwItem('Rico.Version'),
        'RightJS'                    : new fwItem('RightJS.version'),
        'Sammy'                      : new fwItem('Sammy.VERSION', 'sammy.js'),
        '$script.js'                 : new fwItem('$script', 'script.js'),
        'Script.aculo.us'            : new fwItem('Scriptaculous.Version', 'scriptaculous'),
        'Scripty2'                   : new fwItem('S2.Version'),
        'Sencha Touch'               : new fwItem('Ext.util.TapRepeater'),
        'Sizzle'                     : new fwItem('Sizzle', 'sizzle'),
        'Snack'                      : new fwItem('snack.v'),
        'Socket.io'                  : new fwItem('io.version', 'socket.io'),
        'Spine'                      : new fwItem('Spine.version', 'spinejs'),
        'SproutCore'                 : new fwItem('SC.isReady'),
        'Spry'                       : new fwItem('Spry.$'),
        'Sugar'                      : new fwItem('Object.SugarMethods'),
        'SWFObject'                  : new fwItem('swfobject', 'swfobject'),
        'Terrific'                   : new fwItem('Tc'),
        'Tiny Scrollbar'             : new fwItem('jQuery.fn.tinyscrollbar', 'tinyscrollbar'),
        'Twitter Lib'                : new fwItem('twitterlib', 'twitterlib.js'),
        'Underscore.js'              : new fwItem('_.VERSION', 'underscore.js'),
        'Waypoints'                  : new fwItem('jQuery.waypoints', 'waypoints'),
        'Wink toolkit'               : new fwItem('wink'),
        'WebFont Loader'             : new fwItem('WebFont', 'webfont'),
        'xui'                        : new fwItem('x$', 'xuijs'),
        'yepnope.js'                 : new fwItem('yepnope', 'yepnope'),
        'YUI'                        : new fwItem(['YAHOO.VERSION', 'YUI.version'], 'yui'),
        'Zepto'                      : new fwItem('Zepto', 'zepto'),
        'ZK'                         : new fwItem('zk.version')
    };

    var fwStyleLi = {
        'cursor'            : 'pointer',
        'text-align'        : 'left',
        'padding'           : '12px 16px',
        'margin'            : '0 0 8px',
        'list-style'        : 'none',
        'font'              : 'bold 12px Helvetica, Arial, sans-serif',
        //'background'    : '-moz-linear-gradient(top, rgba(255, 255, 255, 0.9) 0%, rgba(243, 243, 243, 0.9) 100%)', // FF3.6+
        //'background'    : '-webkit-linear-gradient(top, rgba(255, 255, 255, 0.8) 0%, rgba(243, 243, 243, 0.8) 100%)', // Chrome10+, Safari5.1+
        //'background'    : '-o-linear-gradient(top, rgba(255, 255, 255, 0.9) 0%, rgba(243, 243, 243, 0.9) 100%)', // Opera 11.10+
        //'background'    : 'linear-gradient(top, rgba(255, 255, 255, 0.9) 0%, rgba(243, 243, 243, 0.9) 100%)', // W3C
        'background'        : 'rgba(243, 243, 243, 0.9)',
        'color'             : '#666',
        'border-radius'     : '4px',
        'border'            : 'solid 1px rgba(255, 255, 255, 0.9)',
        'text-shadow'       : '0 1px 0 #fff',
        'box-shadow'        : '0 0 8px rgba(0, 0, 0, 0.6)',
        'float'             : 'right',
        'clear'             : 'both',
        'min-width'         : '170px'
    };

    var fwStyleUl = {
        'position'  : 'fixed',
        'padding'   : '0',
        'margin'    : '0',
        'right'     : '10px',
        'top'       : '10px',
        'z-index'   : 16777271
    };

    var fwStyleA = {
        'color'             : '#666',
        'font'              : 'bold 12px Helvetica, Arial, sans-serif',
        'text-decoration'   : 'none'
    };

    var props = {
        id      : '_wtframework',
        onclick : fwRemove
    };

    fwUl = document.createElement('ul');

    for (var prop in props) {
        fwUl[prop] = props[prop];
    }

    fwApplyStyles(fwUl, fwStyleUl);

    document.body.appendChild(fwUl);

    var showInfo = function(fwName, fwVersion) {
        var pkgs = window.wtfPkgs,
            s;

        // Show additional info from cdnjs
        var cdnjsInfo = (fwList[fwName] && pkgs[fwList[fwName].cdnjsName])
                      ? pkgs[fwList[fwName].cdnjsName] : null;

        var curVer      = (cdnjsInfo) ? cdnjsInfo.version : null,
            homepageUrl = (cdnjsInfo) ? cdnjsInfo.homepage : '#',
            description = (cdnjsInfo) ? cdnjsInfo.description : '';

        if (curVer !== null) {
            description += ' (Latest version: ' + curVer + ')';
        }

        fwLi = document.createElement('li');

        fwLink = document.createElement('a');
        fwLink.href = homepageUrl;
        fwLink.title = description;
        fwLink.appendChild(document.createTextNode(fwName));
        fwApplyStyles(fwLink, fwStyleA);

        fwLi.appendChild(fwLink);

        if (fwVersion && (fwVersion != '%build%')) {
            fwLi.appendChild(document.createTextNode(' ('));

            if (curVer !== null) {
                var verSpan = document.createElement('span');
                verSpan.style.color = (curVer != fwVersion) ? '#f33' : '#090';
                verSpan.appendChild(document.createTextNode(fwVersion));
                fwLi.appendChild(verSpan);
            } else {
                fwLi.appendChild(document.createTextNode(fwVersion));
            }

            fwLi.appendChild(document.createTextNode(')'));
        }

        fwApplyStyles(fwLi, fwStyleLi);
        fwUl.appendChild(fwLi);
    };

    var findFrameworks = function() {
        var howMany = 0;

        for (var fwNs in fwList) {
            if (fwList.hasOwnProperty(fwNs)) {
                // Loop through all possible version paths
                for (var j = 0; j < fwList[fwNs].verPaths.length; j++) {
                    var exists = window,
                        verPath = fwList[fwNs].verPaths[j];

                    for (var i = 0, idents = verPath.split('.'); i < idents.length; i++) {
                        exists = exists && exists[idents[i]];
                    }
                    if (exists) {
                        var version = false;
                        if (typeof exists === 'string' && ! exists.match(/^<%=/)) {
                            version = exists;
                        } else if (typeof exists === 'object' && exists.hasOwnProperty('toString')) {
                            version = exists.toString();
                        }
                        if (version !== false) {
                            // remove build number ex. "(12345)"
                            version = version.replace(/\s*\(.+\)\s*/, '');
                        }

                        showInfo(fwNs, version);
                        howMany++;
                        break;
                    }
                }
            }
        }

        if (!howMany) {
            showInfo('No known framework detected.');
        }
    };

    if (!window.wtfPkgs) {
        // Load packages from cdnjs
        // http://www.cdnjs.com/packages.min.json
        // thru Yahoo's YQL jsonp proxy
        window.wtfJsonpCb = function(json) {
            var pkgs = json.query.results.json.packages;
            var pHash = {};
            for (var i = 0; i < pkgs.length; i++) {
                if (pkgs[i]) {
                    pHash[pkgs[i].name.toLowerCase()] = pkgs[i];
                }
            }
            window.wtfPkgs = pHash;
            findFrameworks();
        };

        var jsonp = document.createElement('script');
        jsonp.setAttribute('src', "//query.yahooapis.com/v1/public/yql?q=select%20*%20from%20json%20where%20url%3D'http%3A%2F%2Fwww.cdnjs.com%2Fpackages.min.json'&format=json&callback=wtfJsonpCb");
        document.getElementsByTagName('head')[0].appendChild(jsonp);
    } else {
        findFrameworks();
    }
})();
