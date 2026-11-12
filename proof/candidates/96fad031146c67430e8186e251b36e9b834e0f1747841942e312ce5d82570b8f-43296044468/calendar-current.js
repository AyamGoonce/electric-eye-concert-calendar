(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.96fad031146c6743.js","sha256":"96fad031146c67430e8186e251b36e9b834e0f1747841942e312ce5d82570b8f","count":2170,"publishedAt":"2026-11-12T20:01:48Z","state":"calendar-state.json","stateSha256":"5f9127f1ca09651891949de9d42e27b7d6d657f0473e29b9c96451f870d4878c","sourceState":"calendar-source-state.json","sourceStateSha256":"b42e0c06d2e73b74205674853012b5f66fccf492c2da252bdf6d04477e18d509"});
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
