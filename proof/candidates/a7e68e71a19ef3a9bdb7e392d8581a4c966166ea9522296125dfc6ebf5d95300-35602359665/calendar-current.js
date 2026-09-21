(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a7e68e71a19ef3a9.js","sha256":"a7e68e71a19ef3a9bdb7e392d8581a4c966166ea9522296125dfc6ebf5d95300","count":2138,"publishedAt":"2026-09-21T12:59:38Z","state":"calendar-state.json","stateSha256":"efb6cab051813ad996ea5c9e5d9f5bcf635291947286790a60f870bf2a928d43"});
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
