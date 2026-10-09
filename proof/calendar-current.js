(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.1ea1ef8706769fa5.js","sha256":"1ea1ef8706769fa52ca2cd46a10b683c769e65b0b2561d45f3c6b1e48e256494","count":2199,"publishedAt":"2026-10-09T01:17:44Z","state":"calendar-state.json","stateSha256":"6210c0477ce10052cf4419943d806eeb7d6560b84741d5fb669f9bf8944fb005","sourceState":"calendar-source-state.json","sourceStateSha256":"952b5ad581007a73eafc41c56ac8580a6ec285f9d38cdec331f28564cfa5d5ff"});
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
