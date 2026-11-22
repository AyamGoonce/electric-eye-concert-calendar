(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f8c86917cf885976.js","sha256":"f8c86917cf885976d27a8f5b93cf50ea6bd543a14accbac2593c897456214a88","count":2100,"publishedAt":"2026-11-22T19:47:23Z","state":"calendar-state.json","stateSha256":"5ce2987404a331ef707ee1a6e346472fdf290c72ac8cd30244ba75857b6252e2","sourceState":"calendar-source-state.json","sourceStateSha256":"c97ee74b96a4cb0d34c1628469faffcbb9aa885433054172381ede92622662cb"});
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
