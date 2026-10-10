(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4fadc4e0ce523228.js","sha256":"4fadc4e0ce523228cfde510b8fe78ff59c87f42924fe8fa118762db20e9f325d","count":2188,"publishedAt":"2026-10-10T21:51:59Z","state":"calendar-state.json","stateSha256":"6b7930887f8e49813bde4fc7925edfc745b082a90c1ac586d6bf9dc3b2a2916c","sourceState":"calendar-source-state.json","sourceStateSha256":"1fb589ef86b1e9ba75e7703ad41283c7006ac9eda779222af78445fa8fb4609c"});
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
