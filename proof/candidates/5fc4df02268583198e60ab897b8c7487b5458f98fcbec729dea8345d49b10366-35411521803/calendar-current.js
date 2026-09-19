(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.5fc4df0226858319.js","sha256":"5fc4df02268583198e60ab897b8c7487b5458f98fcbec729dea8345d49b10366","count":2193,"publishedAt":"2026-09-19T01:09:19Z","state":"calendar-state.json","stateSha256":"e571614f01551a85b7b4566fc9266d274e989ce618d1e52d4f3024da7a5d6635"});
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
