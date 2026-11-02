(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.770d3db29a1c07b0.js","sha256":"770d3db29a1c07b0508f1bb43aea9a55e430ae1d759067424c642c8cb9a86a1e","count":2045,"publishedAt":"2026-11-02T21:47:21Z","state":"calendar-state.json","stateSha256":"7753ddddddeac8b4d5023d88f19e6065432857f0a58e6d5094246f26c75ec5c2","sourceState":"calendar-source-state.json","sourceStateSha256":"35782bd98146fb5225db2137d19fefbe6a3c2bba35072d0767c89540d25eb60d"});
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
