(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.20fd608a8d284040.js","sha256":"20fd608a8d284040722a63acc417c4ce81480ca9fceee691255366b19316b26f","count":2488,"publishedAt":"2026-09-11T21:05:39Z","state":"calendar-state.json","stateSha256":"37dfa150135067e297ad259b400cd637ec0cf3c33a05bb19164206ce2e9dd884"});
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
