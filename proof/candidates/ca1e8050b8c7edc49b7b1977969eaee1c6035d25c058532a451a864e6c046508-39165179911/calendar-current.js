(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ca1e8050b8c7edc4.js","sha256":"ca1e8050b8c7edc49b7b1977969eaee1c6035d25c058532a451a864e6c046508","count":2068,"publishedAt":"2026-10-18T20:53:17Z","state":"calendar-state.json","stateSha256":"f83942ef928113a5bfa9e2ff3bfe314645c865f9b7af4e3c4e9e645b06c5f45a","sourceState":"calendar-source-state.json","sourceStateSha256":"ca8f7d45ae22ef4c57209617519cda1eaac5a2e431d95d70babfb62c9b0e3024"});
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
