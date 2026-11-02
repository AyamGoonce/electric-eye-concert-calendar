(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.929bec604a68e836.js","sha256":"929bec604a68e836f87e19d0ce0d4dc9628ae182d174079c57206d4b8c54d402","count":2038,"publishedAt":"2026-11-02T13:51:22Z","state":"calendar-state.json","stateSha256":"fe14c01069d8b48aec4ace16597ce2d1a9b1a666ec39d97023a98a577d0865e1","sourceState":"calendar-source-state.json","sourceStateSha256":"e59d8f84d76a02e52c6e8a68f24255432a44217d34f0bb97d6ee30aee659a246"});
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
