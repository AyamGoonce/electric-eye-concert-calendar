(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.995241f3a980e8f2.js","sha256":"995241f3a980e8f20a07365fbe9781f8dabafcf5b81ee91d28506c023d843fb8","count":2055,"publishedAt":"2026-09-20T22:12:26Z","state":"calendar-state.json","stateSha256":"4610f7d2ba70876e9c1859e6c4a8a533192b7fb5f17bdd4f9fa88f8fb84bb248"});
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
