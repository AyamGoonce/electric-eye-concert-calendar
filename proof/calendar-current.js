(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.d467211549f746d6.js","sha256":"d467211549f746d63567c3df7642d7dcf18c198fafdd432364ef9b12dd95d3de","count":2030,"publishedAt":"2026-11-01T06:19:28Z","state":"calendar-state.json","stateSha256":"1d92c26d0131aefca7677991bfdd11779a65cb68803395aea9c4e3f65dbc03a6","sourceState":"calendar-source-state.json","sourceStateSha256":"15e7b7206093e23b80739c5f19aed7a13fbedfed57de422a44b3cff4939f7bf2"});
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
