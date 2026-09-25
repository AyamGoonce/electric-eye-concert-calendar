(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ae30885f02277302.js","sha256":"ae30885f02277302a59b99a016784b75ef60aae51857ab8f0deb18dfbcf47464","count":2124,"publishedAt":"2026-09-25T15:36:05Z","state":"calendar-state.json","stateSha256":"e75dac42defbf05a4ea31404418d4e893c1bdd82948e40dc311df9aca68991c8","sourceState":"calendar-source-state.json","sourceStateSha256":"a105edea62eece9f80ccdccb8db68d2dde3163e85b297c91aa4c2c4ecc5fc0ca"});
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
