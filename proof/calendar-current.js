(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.dc125025134b2ebd.js","sha256":"dc125025134b2ebd3226b7fd1a6758eba599c2c38facbd6c10fd50894b163553","count":2206,"publishedAt":"2026-10-08T08:43:22Z","state":"calendar-state.json","stateSha256":"625489b0b8e9d0dcce1a6ce43ced1c43655a472448d3dd447e5682f1eb80c181","sourceState":"calendar-source-state.json","sourceStateSha256":"0f8ad1c1336f0effd21ef01fde18b25b47a61877ddc8733435bea40bfc0a14cb"});
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
