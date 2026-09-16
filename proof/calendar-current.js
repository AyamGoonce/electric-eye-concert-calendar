(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b82b84728da0735e.js","sha256":"b82b84728da0735e69bc3985c44ec13f91cedd86d01b7f61c7639be56c8ac305","count":2492,"publishedAt":"2026-09-16T10:59:28Z","state":"calendar-state.json","stateSha256":"4190ff7ee670b9e6e06768304052d870d02389916240dc287b222d561cf9f7d5"});
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
