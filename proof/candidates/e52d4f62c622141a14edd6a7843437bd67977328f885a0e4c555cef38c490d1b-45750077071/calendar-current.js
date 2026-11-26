(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e52d4f62c622141a.js","sha256":"e52d4f62c622141a14edd6a7843437bd67977328f885a0e4c555cef38c490d1b","count":2104,"publishedAt":"2026-11-26T03:37:40Z","state":"calendar-state.json","stateSha256":"d6600293982282770f9e9af6f056a685a3e598f57990b64c714bf575daefb808","sourceState":"calendar-source-state.json","sourceStateSha256":"4fff252c9f1bb4ee9ffae81916389cc8962090170005f01a02013c610e096f78"});
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
