(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.679e1adc2a288f3b.js","sha256":"679e1adc2a288f3bc52bb695abbb80b6c62b379031dd384d3e916a790e092a48","count":2065,"publishedAt":"2026-08-29T09:56:55Z","state":"calendar-state.json","stateSha256":"5ef1dbe6a73997e3b6781d1d76dcf77bc9065f7c7ce0d6fce76c7eaf7c31d293"});
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
