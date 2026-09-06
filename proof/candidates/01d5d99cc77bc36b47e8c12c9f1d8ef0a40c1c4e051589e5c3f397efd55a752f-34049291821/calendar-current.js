(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.01d5d99cc77bc36b.js","sha256":"01d5d99cc77bc36b47e8c12c9f1d8ef0a40c1c4e051589e5c3f397efd55a752f","count":2466,"publishedAt":"2026-09-06T17:49:35Z","state":"calendar-state.json","stateSha256":"fb1c8acea4514a2cc71b2238670e4f4bdc55f7e2eda2831d3e8a73549dc2c13a"});
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
