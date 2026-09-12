(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.d50b278750653ec6.js","sha256":"d50b278750653ec63f410d7d533d660a090ccdf6e7cc70de604e3275c4733a81","count":2477,"publishedAt":"2026-09-12T15:39:09Z","state":"calendar-state.json","stateSha256":"166318c8cee3de8ebc166111196097bdd83f407d15c781e12ad07e32625f7805"});
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
