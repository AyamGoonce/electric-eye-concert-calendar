(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.37102778b86f92e4.js","sha256":"37102778b86f92e47bb9e30d7fbf2d758b16382c07215d9a211d479ac77971a4","count":1732,"publishedAt":"2026-08-25T02:00:17Z","state":"calendar-state.json","stateSha256":"69b47275cbc944f47368734ea62c1cd945a32fb39af3d6492a8874137d7771c0"});
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
