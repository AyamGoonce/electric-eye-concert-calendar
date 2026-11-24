(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.667d102fe8f048bb.js","sha256":"667d102fe8f048bbcbfb4150d43b6c065b77bd1c9d84ac1c46f8125aaccc88b7","count":2107,"publishedAt":"2026-11-24T12:32:01Z","state":"calendar-state.json","stateSha256":"6ea575bf34a82529ff8662d6e5b73cbbb63fb83cf59a0feeb110acfaae8d5b97","sourceState":"calendar-source-state.json","sourceStateSha256":"5731708f2373ea2037f02f34ee10a57cdecf5fd85502a8be8bd87904a406358e"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
