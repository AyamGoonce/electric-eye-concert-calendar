(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.84da5dc803fa28d1.js","sha256":"84da5dc803fa28d1171e584a45d937a00b6ea46066d64baf55f9e38d36285172","count":2223,"publishedAt":"2026-11-10T21:20:12Z","state":"calendar-state.json","stateSha256":"1b38c25ca57ba2fc6b9a0a7f783d2c3b1f0c0027f0a88b9734d7b6a862a84dd8","sourceState":"calendar-source-state.json","sourceStateSha256":"d50d018192956a109c2386f6c31df15ef1a06af0d836559c6f5cf743bd774c28"});
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
