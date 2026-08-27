(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.05fead4900e244be.js","sha256":"05fead4900e244bef1ed5f88897dd8820e91f9c2c1b9b629a5e752919c14d9cd","count":1845,"publishedAt":"2026-08-27T15:42:39Z","state":"calendar-state.json","stateSha256":"e53b1263ae9cfa8fc63e845e0ab6a5a7e8b2a54811b5f960426ae3714d9ac01f"});
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
